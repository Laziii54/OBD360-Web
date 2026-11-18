-- OBD360 Web - minimal seed data
-- Roles and a few DTC catalog entries.
-- The full DTC catalog (13k+ codes) is populated by DtcCatalogSeeder on API startup.

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

-- Roles
IF NOT EXISTS (SELECT 1 FROM [dbo].[AspNetRoles] WHERE [NormalizedName] = 'USER')
BEGIN
    INSERT INTO [dbo].[AspNetRoles] ([Id], [Name], [NormalizedName], [ConcurrencyStamp])
    VALUES ('11111111-1111-4111-8111-111111111111', 'User', 'USER', NEWID());
END
GO

IF NOT EXISTS (SELECT 1 FROM [dbo].[AspNetRoles] WHERE [NormalizedName] = 'ADMIN')
BEGIN
    INSERT INTO [dbo].[AspNetRoles] ([Id], [Name], [NormalizedName], [ConcurrencyStamp])
    VALUES ('22222222-2222-4222-8222-222222222222', 'Admin', 'ADMIN', NEWID());
END
GO

-- Sample DTC codes
IF NOT EXISTS (SELECT 1 FROM [dbo].[DtcCatalogEntries] WHERE [Code] = 'P0300')
BEGIN
    INSERT INTO [dbo].[DtcCatalogEntries]
        ([Code], [Category], [TitleEn], [TitleKa], [DescriptionEn], [DescriptionKa],
         [Difficulty], [DiyPossible], [EstimatedCostMin], [EstimatedCostMax],
         [EstimatedHoursMin], [EstimatedHoursMax], [DetailsJson])
    VALUES
        ('P0300', 'P', 'Random/Multiple Cylinder Misfire Detected', 'ცილინდრების შემთხვევითი/მრავლობითი გამოტოვება',
         'The engine control module detected misfires on multiple cylinders.',
         'ძრავის მართვის ბლოკმა დააფიქსირა აალების გამოტოვება რამდენიმე ცილინდრში.',
         'Medium', 1, 80, 450, 1.0, 3.0, '{}');
END
GO

IF NOT EXISTS (SELECT 1 FROM [dbo].[DtcCatalogEntries] WHERE [Code] = 'P0420')
BEGIN
    INSERT INTO [dbo].[DtcCatalogEntries]
        ([Code], [Category], [TitleEn], [TitleKa], [DescriptionEn], [DescriptionKa],
         [Difficulty], [DiyPossible], [EstimatedCostMin], [EstimatedCostMax],
         [EstimatedHoursMin], [EstimatedHoursMax], [DetailsJson])
    VALUES
        ('P0420', 'P', 'Catalyst System Efficiency Below Threshold', 'კატალიზატორის ეფექტურობა ზღვრულ მნიშვნელობაზე დაბალია',
         'The catalytic converter is not cleaning the exhaust efficiently.',
         'კატალიზატორი გამონაბოლქვს საკმარისად ეფექტურად არ წმენდს.',
         'Hard', 0, 300, 1500, 2.0, 6.0, '{}');
END
GO

IF NOT EXISTS (SELECT 1 FROM [dbo].[DtcCatalogEntries] WHERE [Code] = 'P0A80')
BEGIN
    INSERT INTO [dbo].[DtcCatalogEntries]
        ([Code], [Category], [TitleEn], [TitleKa], [DescriptionEn], [DescriptionKa],
         [Difficulty], [DiyPossible], [EstimatedCostMin], [EstimatedCostMax],
         [EstimatedHoursMin], [EstimatedHoursMax], [DetailsJson])
    VALUES
        ('P0A80', 'P', 'Replace Hybrid Battery Pack', 'ჰიბრიდული ბატარეის შეცვლა საჭიროა',
         'The hybrid battery pack has degraded below the acceptable threshold.',
         'ჰიბრიდული ბატარეის პაკეტის ტევადობა დასაშვებ ზღვარზე დაბლა დაეცა.',
         'Hard', 0, 800, 4000, 3.0, 8.0, '{}');
END
GO

IF NOT EXISTS (SELECT 1 FROM [dbo].[DtcCatalogEntries] WHERE [Code] = 'P0171')
BEGIN
    INSERT INTO [dbo].[DtcCatalogEntries]
        ([Code], [Category], [TitleEn], [TitleKa], [DescriptionEn], [DescriptionKa],
         [Difficulty], [DiyPossible], [EstimatedCostMin], [EstimatedCostMax],
         [EstimatedHoursMin], [EstimatedHoursMax], [DetailsJson])
    VALUES
        ('P0171', 'P', 'System Too Lean (Bank 1)', 'სისტემა ზედმეტად ღარიბია (ბანკი 1)',
         'The engine is receiving too much air or too little fuel.',
         'ძრავი იღებს ზედმეტ ჰაერს ან არასაკმარის საწვავს.',
         'Easy', 1, 40, 250, 0.5, 2.0, '{}');
END
GO

IF NOT EXISTS (SELECT 1 FROM [dbo].[DtcCatalogEntries] WHERE [Code] = 'C0035')
BEGIN
    INSERT INTO [dbo].[DtcCatalogEntries]
        ([Code], [Category], [TitleEn], [TitleKa], [DescriptionEn], [DescriptionKa],
         [Difficulty], [DiyPossible], [EstimatedCostMin], [EstimatedCostMax],
         [EstimatedHoursMin], [EstimatedHoursMax], [DetailsJson])
    VALUES
        ('C0035', 'C', 'Left Front Wheel Speed Sensor Circuit', 'მარცხენა წინა ბორბლის სიჩქარის სენსორის წრე',
         'The ABS module cannot read the left front wheel speed sensor.',
         'ABS მოდული ვერ კითხულობს მარცხენა წინა ბორბლის სიჩქარის სენსორს.',
         'Medium', 1, 60, 300, 1.0, 2.0, '{}');
END
GO

-- End of seed
