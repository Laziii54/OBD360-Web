from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BASE = Path(r"C:\Users\zukal\OneDrive\Desktop\OBD2 WEB")
OUT = BASE / "docs" / "report" / "OBD360-Defense-Guide.docx"

INK = RGBColor(0x20, 0x25, 0x1F)
SAGE = RGBColor(0x3F, 0x5D, 0x4E)
MUTED = RGBColor(0x72, 0x77, 0x6E)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
CODE_BG = "1F2924"

doc = Document()
section = doc.sections[0]
section.page_width = Cm(21)
section.page_height = Cm(29.7)
section.top_margin = Cm(1.9)
section.bottom_margin = Cm(1.8)
section.left_margin = Cm(2.0)
section.right_margin = Cm(2.0)
section.header_distance = Cm(0.9)
section.footer_distance = Cm(0.7)
section.different_first_page_header_footer = True

normal = doc.styles["Normal"]
normal.font.name = "Sylfaen"
normal.font.size = Pt(10)
normal.font.color.rgb = INK
normal.paragraph_format.line_spacing = 1.12
normal.paragraph_format.space_after = Pt(5)

for name, size, color in [("Heading 1", 17, SAGE), ("Heading 2", 12.5, INK)]:
    style = doc.styles[name]
    style.font.name = "Sylfaen"
    style.font.size = Pt(size)
    style.font.bold = True
    style.font.color.rgb = color
    style.paragraph_format.space_before = Pt(12)
    style.paragraph_format.space_after = Pt(5)
    style.paragraph_format.keep_with_next = True


def shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def margins(cell, top=50, bottom=50, left=80, right=80):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for key, value in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = tc_mar.find(qn(f"w:{key}"))
        if node is None:
            node = OxmlElement(f"w:{key}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def page_number(paragraph):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(instr)
    run._r.append(end)
    run.font.name = "Sylfaen"
    run.font.size = Pt(8.5)
    run.font.color.rgb = MUTED


def header_footer():
    header = section.header
    header.is_linked_to_previous = False
    paragraph = header.paragraphs[0]
    paragraph.text = "OBD360 Web  ·  დაცვის გზამკვლევი"
    for run in paragraph.runs:
        run.font.name = "Sylfaen"
        run.font.size = Pt(8.5)
        run.font.color.rgb = MUTED
    p_pr = paragraph._p.get_or_add_pPr()
    border = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "4")
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), "E4E0D7")
    border.append(bottom)
    p_pr.append(border)

    footer = section.footer
    footer.is_linked_to_previous = False
    paragraph = footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    label = paragraph.add_run("OBD360 Web  ·  2026   |   ")
    label.font.name = "Sylfaen"
    label.font.size = Pt(8.5)
    label.font.color.rgb = MUTED
    page_number(paragraph)


def h1(text):
    doc.add_page_break()
    paragraph = doc.add_paragraph(style="Heading 1")
    run = paragraph.add_run(text)
    run.font.name = "Sylfaen"
    run.font.size = Pt(17)
    run.font.bold = True
    run.font.color.rgb = SAGE


def h2(text):
    paragraph = doc.add_paragraph(style="Heading 2")
    run = paragraph.add_run(text)
    run.font.name = "Sylfaen"
    run.font.size = Pt(12.5)
    run.font.bold = True
    run.font.color.rgb = INK


def p(text, size=10):
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = paragraph.add_run(text)
    run.font.name = "Sylfaen"
    run.font.size = Pt(size)
    run.font.color.rgb = INK
    return paragraph


def bullets(items, size=9.5):
    for item in items:
        paragraph = doc.add_paragraph(style="List Bullet")
        paragraph.paragraph_format.space_after = Pt(2)
        run = paragraph.add_run(item)
        run.font.name = "Sylfaen"
        run.font.size = Pt(size)
        run.font.color.rgb = INK


def table(headers, rows, widths, font_size=8.2, mono_column=None):
    table_obj = doc.add_table(rows=1, cols=len(headers))
    table_obj.style = "Table Grid"
    table_obj.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_obj.autofit = False
    for index, header in enumerate(headers):
        cell = table_obj.rows[0].cells[index]
        cell.width = Cm(widths[index])
        shade(cell, "3F5D4E")
        margins(cell, 55, 55, 70, 70)
        paragraph = cell.paragraphs[0]
        paragraph.paragraph_format.space_after = Pt(0)
        run = paragraph.add_run(header)
        run.font.name = "Sylfaen"
        run.font.size = Pt(font_size)
        run.font.bold = True
        run.font.color.rgb = WHITE
    for row_index, row in enumerate(rows):
        cells = table_obj.add_row().cells
        for index, value in enumerate(row):
            cell = cells[index]
            cell.width = Cm(widths[index])
            margins(cell, 45, 45, 70, 70)
            if row_index % 2 == 1:
                shade(cell, "F7F5F0")
            paragraph = cell.paragraphs[0]
            paragraph.paragraph_format.space_after = Pt(0)
            paragraph.paragraph_format.line_spacing = 1.0
            run = paragraph.add_run(str(value))
            run.font.name = "Consolas" if mono_column is not None and index == mono_column else "Sylfaen"
            run.font.size = Pt(font_size - (0.6 if mono_column is not None and index == mono_column else 0))
            run.font.color.rgb = INK
            
            if mono_column is not None and index == mono_column:
                # Allow long file paths to wrap at directory separators.
                run.text = str(value).replace("/", "/\u200b")
    doc.add_paragraph().paragraph_format.space_after = Pt(1)
    return table_obj


def code_block(lines):
    table_obj = doc.add_table(rows=1, cols=1)
    table_obj.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_obj.autofit = False
    cell = table_obj.rows[0].cells[0]
    cell.width = Cm(16.2)
    shade(cell, CODE_BG)
    margins(cell, 80, 80, 110, 110)
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.line_spacing = 1.0
    run = paragraph.add_run("\n".join(lines))
    run.font.name = "Consolas"
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0xE8, 0xEF, 0xE9)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)


header_footer()

# ---------------------------------------------------------------- TITLE
paragraph = doc.add_paragraph()
paragraph.paragraph_format.space_before = Pt(45)
run = paragraph.add_run("OBD360 WEB")
run.font.name = "Sylfaen"
run.font.size = Pt(36)
run.font.bold = True
run.font.color.rgb = INK

paragraph = doc.add_paragraph()
run = paragraph.add_run("დაცვის გზამკვლევი")
run.font.name = "Sylfaen"
run.font.size = Pt(22)
run.font.bold = True
run.font.color.rgb = SAGE

paragraph = doc.add_paragraph()
paragraph.paragraph_format.space_before = Pt(6)
run = paragraph.add_run("სად არის კოდში რა და როგორ უპასუხო ლექტორს მარტივი ენით")
run.font.name = "Sylfaen"
run.font.size = Pt(12)
run.font.color.rgb = MUTED

paragraph = doc.add_paragraph()
paragraph.paragraph_format.space_before = Pt(16)
run = paragraph.add_run("ეს გზამკვლევი კოდს არ ცვლის — ის მხოლოდ გიჩვენებს გზას.")
run.font.name = "Sylfaen"
run.font.size = Pt(10)
run.font.italic = True
run.font.color.rgb = SAGE

code_block([
    "Angular (ეკრანი) -> ASP.NET API (ლოგიკა) -> SQL Server (მონაცემები)",
    "        ^",
    "OBD-II ადაპტერი -> ECU (მანქანა)",
])

paragraph = doc.add_paragraph()
paragraph.paragraph_format.space_before = Pt(24)
run = paragraph.add_run("ავტორი: ზურაბ ლაზაშვილი  ·  2026")
run.font.name = "Sylfaen"
run.font.size = Pt(10)
run.font.color.rgb = MUTED

# ---------------------------------------------------------------- 30 SEC
h1("1. 30-წამიანი პასუხი")
p("OBD360 Web არის ვებ-აპლიკაცია, რომელიც ბრაუზერიდან უკავშირდება OBD-II ადაპტერს Web Bluetooth-ით, კითხულობს მანქანის ECU-დან DTC კოდებსა და Live Data-ს, აგზავნის შედეგებს ASP.NET Core API-ში, ინახავს SQL Server-ში და აჩვენებს ქართულ ახსნას. AI ასისტენტი მუშაობს n8n + Gemini-ით.")
p("მოკლე ფორმულა: Angular (ეკრანი) → API (ლოგიკა) → SQL (მონაცემები); გვერდით — OBD-II ადაპტერი → ECU.")
p("რიცხვები: 32 REST endpoint, 15 მოდელი, 21 ცხრილი, 13 629 DTC, 29 backend + 19 frontend ტესტი.")
bullets([
    "ეკრანი — Angular (frontend/).",
    "ლოგიკა — ASP.NET Core API (backend/Obd360.Api/).",
    "მონაცემები — SQL Server (backend/Obd360.Infrastructure/).",
], 9.5)

# ---------------------------------------------------------------- MAP
h1("2. სად არის რა — 10-წამიანი ცხრილი")
rows = [
    ("აპლიკაციის დაწყება", "Angular იწყება და უკავშირდება routing/HttpClient-ს", "frontend/src/main.ts; app.config.ts"),
    ("მარშრუტები", "ყველა გვერდი და დაცული route", "frontend/src/app/app.routes.ts"),
    ("Login — ეკრანი", "ფორმა იძახებს Auth.login()", "features/auth/login/login.ts"),
    ("Login — API", "ამოწმებს პაროლს, აბრუნებს token-ებს", "AuthController.cs:95"),
    ("რეგისტრაცია", "ქმნის მომხმარებელს", "AuthController.cs:53; register.ts"),
    ("პაროლის აღდგენა", "6-ციფრიანი კოდი ელფოსტით", "AuthController.cs:157; PasswordResetCodeService.cs"),
    ("JWT-ის შექმნა", "ხელმოწერილი access token", "Infrastructure/Services/TokenService.cs:20"),
    ("Token-ის დამატება", "Authorization: Bearer", "core/interceptors/auth-interceptor.ts:8"),
    ("401 / refresh", "refresh და request-ის გამეორება", "auth-interceptor.ts:22"),
    ("Guard", "გვერდზე შესვლის შემოწმება", "core/guards/auth-guard.ts; admin-guard.ts"),
    ("Sidebar / burger", "მობილურზე მარცხენა drawer", "layout/main-layout/main-layout.ts/.html/.scss"),
    ("Garage", "მანქანების CRUD", "features/garage/garage.ts; VehiclesController.cs"),
    ("Reminders", "შეხსენებების CRUD", "features/reminders/reminders.ts; RemindersController.cs"),
    ("Bluetooth", "ადაპტერთან დაკავშირება", "core/services/obd-bluetooth.service.ts:97"),
    ("Live Data", "PID-ების კითხვა", "features/live-data/live-data.ts; obd-decoder.ts:57"),
    ("DTC სკანირება", "03 / 07 / 0A", "core/services/dtc-scan.service.ts:34"),
    ("DTC პარსერი", "hex → P0300", "core/services/obd-decoder.ts:62"),
    ("DTC კატალოგი", "13 629 კოდის ძებნა", "features/dtc-catalog/dtc-catalog.ts; DtcCatalogController.cs"),
    ("სკანირების ისტორია", "შენახული სკანირებები", "features/scan-history/scan-history.ts; ScansController.cs"),
    ("AI", "კითხვა → API → n8n → Gemini", "AiController.cs; Integrations/N8n/"),
    ("n8n workflow", "ავტომატიზაცია", "n8n/*.workflow.json"),
    ("Admin", "users, roles, scans", "features/admin/admin.ts; AdminController.cs"),
    ("ბაზა", "EF Core DbContext", "Infrastructure/Data/ApplicationDbContext.cs"),
    ("მოდელები", "15 მოდელი", "Obd360.Core/Entities/"),
    ("მიგრაციები", "სქემის ვერსიები", "Infrastructure/Migrations/"),
    ("DTC 13 629", "პირველ გაშვებაზე იტვირთება", "DtcCatalogSeeder.cs; Data/dtc-catalog.json.gz"),
    ("JWT კონფიგურაცია", "AddJwtBearer", "Program.cs:93"),
    ("ლოგირება", "HTTP request logging", "Program.cs:154; appsettings.json"),
    ("Swagger", "API დოკუმენტაცია", "Program.cs:29; /swagger"),
    ("ტესტები", "29 + 19", "Obd360.Tests/; frontend/**/*.spec.ts"),
    ("C4", "Context/Container/Component", "docs/c4/OBD360 C4.pdf"),
]
table(["რას ეძებ", "მოკლე პასუხი", "ფაილი"], rows, [4.0, 6.8, 5.0], font_size=7.5, mono_column=2)

# ---------------------------------------------------------------- SCENARIOS
h1("3. „მაჩვენე, სად არის…“ — 5 სცენარი")
h2("Login")
p("გახსენი features/auth/login/login.ts → core/services/auth.ts:43 → AuthController.cs:95. თქვი: „ფორმა აგზავნის POST /auth/login-ს; controller ამოწმებს პაროლს და აბრუნებს JWT + refresh cookie-ს.“")
h2("მანქანები")
p("garage.ts → vehicles.service.ts → VehiclesController.cs → Vehicle.cs → ApplicationDbContext. თქვი: „CRUD მიდის controller-ში და ინახება Vehicles ცხრილში.“")
h2("OBD კავშირი")
p("bluetooth.ts → obd-bluetooth.service.ts:97 (connect) → :192 (initializeAdapter: ATZ, ATE0, ATSP0, 0100) → dtc-scan.service.ts:34 (03/07/0A) → obd-decoder.ts:68 (parseDtcResponse).")
h2("13 629 კოდი")
p("Data/dtc-catalog.json.gz → DtcCatalogSeeder.cs:12 → Program.cs:127 → DtcCatalogController.cs → dtc-catalog.ts.")
h2("AI")
p("ai-assistant.ts → AiController.cs:96 (/ai/ask) → Integrations/N8n/N8nClient.cs → ScanPromptBuilder.cs → n8n workflow → Gemini.")

h2("პასუხის შაბლონი")
p("„ეკრანი — X, ფაილი — Y, მეთოდი — Z, მონაცემი — T.“ ეს ოთხი სიტყვა საკმარისია, რომ პასუხი სრული იყოს.")

# ---------------------------------------------------------------- Q&A
h1("4. 30 კითხვა-პასუხი")
qa = [
    ("რა ტექნოლოგიები გამოიყენე?", "Angular 22, ASP.NET Core 10, EF Core, SQL Server, JWT, n8n, Gemini."),
    ("რატომ გაყავი frontend და backend?", "ეკრანი და ლოგიკა დამოუკიდებლად იცვლება; API სხვა კლიენტსაც ემსახურება."),
    ("რა არის REST API?", "HTTP მისამართების ნაკრები: GET/POST/PUT/DELETE."),
    ("რამდენი endpoint გაქვს?", "32: auth 7, preferences 2, vehicles 5, reminders 5, scans 2, DTC 2, AI 4, admin 5."),
    ("სად ინახება access token?", "sessionStorage-ში და Angular signal-ში — auth.ts:109."),
    ("სად ინახება refresh token?", "HttpOnly cookie-ში; ბაზაში მხოლოდ hash — RefreshSession."),
    ("რა ხდება 401-ზე?", "Interceptor აკეთებს refresh-ს და request-ს იმეორებს — auth-interceptor.ts:22."),
    ("რატომ არის access token მოკლე?", "15 წუთი — მოპარული token-ის რისკი მცირდება."),
    ("როგორ იცის სისტემამ ვინ არის Admin?", "JWT role claim + [Authorize(Roles=\"Admin\")] + adminGuard."),
    ("სად არის პაროლის აღდგენა?", "AuthController.cs:157/204, PasswordResetCodeService.cs, SmtpEmailSender.cs."),
    ("სად არის ბაზა?", "ApplicationDbContext.cs; connection string appsettings.Development.json."),
    ("რამდენი მოდელია?", "15 მოდელი, 21 ფიზიკური ცხრილი."),
    ("სად არის DtcRecord?", "Obd360.Core/Entities/ScanSession.cs — იქვეა LiveReading, DtcRecord, DtcCatalogEntry."),
    ("სად ინახება სკანირება?", "ScanSessions + DtcRecords + LiveReadings."),
    ("რატომ EF Core?", "C# ობიექტებით ვმუშაობ; მიგრაციები სქემას აახლებს."),
    ("რა არის OBD-II?", "მანქანის დიაგნოსტიკის სტანდარტი; 16-pin პორტი."),
    ("რა არის ECU?", "მანქანის ელექტრონული მართვის ბლოკი."),
    ("რა არის PID?", "პარამეტრის ID: 010C — ბრუნი, 010D — სიჩქარე."),
    ("რა ბრძანებებს აგზავნის აპლიკაცია?", "ATZ, ATE0, ATL0, ATS0, ATH0, ATSP0, 0100, 03, 07, 0A, 0902, 04."),
    ("რას ნიშნავს 43 პასუხში?", "0x40 + 0x03 — რეჟიმ 03-ის პასუხი."),
    ("როგორ იშიფრება 01 33?", "პირველი nibble → P/C/B/U; გამოდის P0133."),
    ("რატომ 13 629 კოდი?", "სტანდარტული + მწარმოებლის კოდები; იტვირთება DtcCatalogSeeder-ით."),
    ("სად არის მანქანების CRUD?", "VehiclesController.cs + garage.ts + vehicles.service.ts."),
    ("სად არის შეხსენებები?", "RemindersController.cs + reminders.ts + ReminderNotificationService.cs."),
    ("სად იგზავნება ელფოსტა?", "SmtpEmailSender.cs; პარამეტრები user-secrets-ში."),
    ("სად არის AI?", "AiController.cs → N8nClient.cs → n8n → Gemini."),
    ("სად არის ადმინი?", "AdminController.cs + admin.ts + admin.service.ts."),
    ("სად არის რესპონსიული მენიუ?", "main-layout.ts (sidebarOpen), .html (burger), .scss (max-width:720px)."),
    ("სად არის ტესტები?", "Obd360.Tests/ და frontend/**/*.spec.ts; 29 + 19."),
    ("სად არის Swagger/ლოგები/C4?", "Program.cs:29; Program.cs:154; docs/c4/OBD360 C4.pdf."),
]
table(["კითხვა", "პასუხი"], qa, [6.2, 9.8], font_size=8.2)

# ---------------------------------------------------------------- TERMS
h1("5. რთული სიტყვები მარტივად")
terms = [
    ("API", "მიმტანი, რომელიც ეკრანსა და ბაზას შორის დგას."),
    ("DTO", "ყუთი, რომლითაც მონაცემები API-სა და ეკრანს შორის გადადის."),
    ("JWT", "ხელმოწერილი ბარათი: „ეს მომხმარებელია“."),
    ("Refresh token", "გრძელვადიანი გასაღები ახალი ბარათის ასაღებად."),
    ("Interceptor", "გამშვები, რომელიც ყოველ request-ს token-ს ამატებს."),
    ("Guard", "მცველი, რომელიც გვერდზე შესვლას ამოწმებს."),
    ("Signal", "Angular-ის ცოცხალი ცვლადი; იცვლება — ეკრანიც იცვლება."),
    ("EF Core", "C#-იდან ბაზასთან მუშაობის ხიდი."),
    ("Migration", "ბაზის სქემის ვერსია."),
    ("PID", "მანქანის პარამეტრის ID."),
    ("DTC", "ხარვეზის კოდი."),
    ("n8n", "ავტომატიზაციის პროგრამა, რომელიც AI-ს იძახებს."),
]
table(["ტერმინი", "მარტივი ახსნა"], terms, [4.4, 11.6], font_size=8.5)

# ---------------------------------------------------------------- PRESENTATION
h1("6. 2-წუთიანი პრეზენტაცია")
p("„პროექტი OBD360 Web არის ავტომობილის დიაგნოსტიკის ვებ-პლატფორმა. მომხმარებელი ბრაუზერიდან უკავშირდება OBD-II ადაპტერს Web Bluetooth-ით. ადაპტერი ECU-ს უგზავნის AT და PID ბრძანებებს, ხოლო პასუხს Angular ამუშავებს. DTC კოდები ინახება SQL Server-ში და აჩვენებს ქართულ ახსნას 13 629-კოდიანი კატალოგიდან. ავტორიზაცია JWT-ითაა, AI ასისტენტი — n8n და Gemini-ით. სისტემას აქვს 32 REST endpoint, 15 მოდელი და 48 ტესტი.“")

# ---------------------------------------------------------------- ANSWER FORMULA
h1("7. ოქროს ფორმულა: 4 ნაბიჯი")
p("როცა ლექტორი ეკითხება „სად არის ეს?“, უპასუხე ზუსტად ამ თანმიმდევრობით:")
bullets([
    "ეკრანი — რომელი გვერდია.",
    "ფაილი — ზუსტი გზა.",
    "მეთოდი — რომელი ფუნქცია.",
    "მონაცემი — რომელ ცხრილში ინახება.",
], 10)
p("მაგალითი: „მანქანების დამატება იწყება garage.ts-ში, იძახებს vehicles.service.ts-ს, მიდის VehiclesController.Create-ში და ინახება Vehicles ცხრილში.“")

# ---------------------------------------------------------------- PLAN
h1("8. სწავლის 3-დღიანი გეგმა")
h2("დღე 1 — დიდი სურათი")
bullets([
    "წაიკითხე ეს გზამკვლევი.",
    "დახაზე 3 ყუთი: Angular → API → SQL.",
    "იპოვე 5 ფაილი: app.routes.ts, AuthController.cs, ApplicationDbContext.cs, obd-bluetooth.service.ts, dtc-scan.service.ts.",
], 9.5)
h2("დღე 2 — ერთი ფუნქცია ბოლომდე")
bullets([
    "აირჩიე login ან scan.",
    "გაიარე გზა: ეკრანი → service → API → controller → ბაზა.",
    "თითო ფაილზე დაწერე 1 წინადადება: „ეს აკეთებს…“.",
], 9.5)
h2("დღე 3 — კითხვები")
bullets([
    "გამოიყენე 30 კითხვა-პასუხი.",
    "ითამაშე ლექტორის როლი: „მაჩვენე…“.",
    "გადახედე დოკუმენტაციის შესაბამის თავს.",
], 9.5)

doc.save(OUT)
print(f"saved {OUT}")
