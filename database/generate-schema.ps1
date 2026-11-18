$ErrorActionPreference = 'Stop'

$connection = @('-S', 'localhost', '-E', '-d', 'GeorgianCarScannerWeb', '-I', '-h', '-1', '-W', '-s', '|')

$columnQuery = @"
SET NOCOUNT ON;
SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE,
       ISNULL(CHARACTER_MAXIMUM_LENGTH, -1),
       ISNULL(NUMERIC_PRECISION, 0),
       ISNULL(NUMERIC_SCALE, 0),
       IS_NULLABLE,
       ISNULL(COLUMNPROPERTY(OBJECT_ID(TABLE_SCHEMA + '.' + TABLE_NAME), COLUMN_NAME, 'IsIdentity'), 0)
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'dbo'
ORDER BY TABLE_NAME, ORDINAL_POSITION;
"@

$pkQuery = @"
SET NOCOUNT ON;
SELECT tc.TABLE_NAME, kcu.COLUMN_NAME
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
  ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
 AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY' AND tc.TABLE_SCHEMA = 'dbo'
ORDER BY tc.TABLE_NAME, kcu.ORDINAL_POSITION;
"@

$fkQuery = @"
SET NOCOUNT ON;
SELECT fk.TABLE_NAME, cu.COLUMN_NAME, pk.TABLE_NAME, pt.COLUMN_NAME, rc.CONSTRAINT_NAME
FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS fk
  ON rc.CONSTRAINT_NAME = fk.CONSTRAINT_NAME AND rc.CONSTRAINT_SCHEMA = fk.CONSTRAINT_SCHEMA
JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS pk
  ON rc.UNIQUE_CONSTRAINT_NAME = pk.CONSTRAINT_NAME AND rc.UNIQUE_CONSTRAINT_SCHEMA = pk.CONSTRAINT_SCHEMA
JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE cu
  ON cu.CONSTRAINT_NAME = fk.CONSTRAINT_NAME AND cu.TABLE_SCHEMA = fk.TABLE_SCHEMA
JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE pt
  ON pt.CONSTRAINT_NAME = pk.CONSTRAINT_NAME AND pt.ORDINAL_POSITION = cu.ORDINAL_POSITION
WHERE fk.TABLE_SCHEMA = 'dbo';
"@

function Get-SqlType($dataType, $length, $precision, $scale) {
    switch ($dataType) {
        'nvarchar' { if ($length -eq -1) { return 'nvarchar(max)' } else { return "nvarchar($length)" } }
        'varchar'  { if ($length -eq -1) { return 'varchar(max)' } else { return "varchar($length)" } }
        'nchar'    { return "nchar($length)" }
        'char'     { return "char($length)" }
        'varbinary'{ if ($length -eq -1) { return 'varbinary(max)' } else { return "varbinary($length)" } }
        'decimal'  { return "decimal($precision,$scale)" }
        'numeric'  { return "numeric($precision,$scale)" }
        'datetime2'{ return 'datetime2' }
        'datetimeoffset' { return 'datetimeoffset' }
        'float'    { return 'float' }
        'real'     { return 'real' }
        default    { return $dataType }
    }
}

$columns = @{}
foreach ($line in (sqlcmd @connection -Q $columnQuery)) {
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    $parts = $line -split '\|'
    if ($parts.Count -lt 8) { continue }
    $table = $parts[0].Trim()
    if (-not $columns.ContainsKey($table)) { $columns[$table] = @() }
    $columns[$table] += [pscustomobject]@{
        Name = $parts[1].Trim()
        DataType = $parts[2].Trim()
        Length = [int]$parts[3]
        Precision = [int]$parts[4]
        Scale = [int]$parts[5]
        Nullable = $parts[6].Trim()
        Identity = $parts[7].Trim()
    }
}

$primaryKeys = @{}
foreach ($line in (sqlcmd @connection -Q $pkQuery)) {
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    $parts = $line -split '\|'
    if ($parts.Count -lt 2) { continue }
    $table = $parts[0].Trim()
    if (-not $primaryKeys.ContainsKey($table)) { $primaryKeys[$table] = @() }
    $primaryKeys[$table] += $parts[1].Trim()
}

$foreignKeys = @()
foreach ($line in (sqlcmd @connection -Q $fkQuery)) {
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    $parts = $line -split '\|'
    if ($parts.Count -lt 5) { continue }
    $foreignKeys += [pscustomobject]@{
        Table = $parts[0].Trim()
        Column = $parts[1].Trim()
        RefTable = $parts[2].Trim()
        RefColumn = $parts[3].Trim()
        Name = $parts[4].Trim()
    }
}

$output = @()
$output += '-- OBD360 Web - SQL Server schema'
$output += '-- Generated from the development database.'
$output += '-- Source of truth: EF Core migrations in backend/Obd360.Infrastructure/Migrations.'
$output += ''
$output += 'SET ANSI_NULLS ON;'
$output += 'SET QUOTED_IDENTIFIER ON;'
$output += 'GO'
$output += ''

foreach ($table in ($columns.Keys | Sort-Object)) {
    $output += "CREATE TABLE [dbo].[$table] ("
    $definitions = @()
    foreach ($column in $columns[$table]) {
        $type = Get-SqlType $column.DataType $column.Length $column.Precision $column.Scale
        $definition = "    [$($column.Name)] $type"
        if ($column.Identity -eq '1') { $definition += ' IDENTITY(1,1)' }
        if ($column.Nullable -eq 'NO') { $definition += ' NOT NULL' } else { $definition += ' NULL' }
        $definitions += $definition
    }
    if ($primaryKeys.ContainsKey($table)) {
        $keyColumns = ($primaryKeys[$table] | ForEach-Object { "[$_]" }) -join ', '
        $definitions += "    CONSTRAINT [PK_$table] PRIMARY KEY ($keyColumns)"
    }
    $output += ($definitions -join ",`n")
    $output += ');'
    $output += 'GO'
    $output += ''
}

$output += '-- Foreign keys'
foreach ($foreignKey in ($foreignKeys | Sort-Object Table, Column)) {
    $output += "ALTER TABLE [dbo].[$($foreignKey.Table)] ADD CONSTRAINT [$($foreignKey.Name)] FOREIGN KEY ([$($foreignKey.Column)]) REFERENCES [dbo].[$($foreignKey.RefTable)] ([$($foreignKey.RefColumn)]);"
    $output += 'GO'
}

$output += ''
$output += '-- End of schema'
Set-Content -Path 'database\schema.sql' -Value ($output -join "`r`n") -Encoding UTF8
Write-Output "Wrote database\schema.sql with $($columns.Count) tables and $($foreignKeys.Count) foreign keys."
