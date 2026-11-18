using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Obd360.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class ExpandDtcCatalog : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // The catalog is reference data and is re-imported from the data file.
            migrationBuilder.DropTable(
                name: "DtcCatalogEntries");

            migrationBuilder.CreateTable(
                name: "DtcCatalogEntries",
                columns: table => new
                {
                    Code = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    Category = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: false),
                    TitleEn = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: false),
                    TitleKa = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: false),
                    DescriptionEn = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    DescriptionKa = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Difficulty = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: false),
                    DiyPossible = table.Column<bool>(type: "bit", nullable: false),
                    EstimatedCostMin = table.Column<int>(type: "int", nullable: true),
                    EstimatedCostMax = table.Column<int>(type: "int", nullable: true),
                    EstimatedHoursMin = table.Column<double>(type: "float", nullable: true),
                    EstimatedHoursMax = table.Column<double>(type: "float", nullable: true),
                    DetailsJson = table.Column<string>(type: "nvarchar(max)", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DtcCatalogEntries", x => x.Code);
                });

            migrationBuilder.CreateIndex(
                name: "IX_DtcCatalogEntries_Category",
                table: "DtcCatalogEntries",
                column: "Category");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "DtcCatalogEntries");

            migrationBuilder.CreateTable(
                name: "DtcCatalogEntries",
                columns: table => new
                {
                    Code = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    Title = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Description = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Severity = table.Column<int>(type: "int", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DtcCatalogEntries", x => x.Code);
                });
        }
    }
}
