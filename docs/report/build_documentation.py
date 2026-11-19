from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BASE = Path(r"C:\Users\zukal\OneDrive\Desktop\OBD2 WEB")
ASSETS = BASE / "docs" / "report" / "assets"
SLIDE_ASSETS = BASE / "docs" / "slides" / "assets"
OUT = BASE / "docs" / "report" / "OBD360-Web-Documentation.docx"

INK = RGBColor(0x20, 0x25, 0x1F)
SAGE = RGBColor(0x3F, 0x5D, 0x4E)
MUTED = RGBColor(0x72, 0x77, 0x6E)
AMBER = RGBColor(0xB9, 0x86, 0x3F)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
CODE_BG = "1F2924"

doc = Document()

# ---------------------------------------------------------------- page setup
section = doc.sections[0]
section.page_width = Cm(21)
section.page_height = Cm(29.7)
section.top_margin = Cm(2.2)
section.bottom_margin = Cm(2.0)
section.left_margin = Cm(2.3)
section.right_margin = Cm(2.3)
section.header_distance = Cm(1.0)
section.footer_distance = Cm(0.8)
section.different_first_page_header_footer = True

# ---------------------------------------------------------------- styles
styles = doc.styles
normal = styles["Normal"]
normal.font.name = "Sylfaen"
normal.font.size = Pt(10.5)
normal.font.color.rgb = INK
normal.paragraph_format.line_spacing = 1.18
normal.paragraph_format.space_after = Pt(6)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Sylfaen")

for style_name, size, color in [("Heading 1", 18, SAGE), ("Heading 2", 13, INK), ("Heading 3", 11.5, SAGE)]:
    style = styles[style_name]
    style.font.name = "Sylfaen"
    style.font.size = Pt(size)
    style.font.bold = True
    style.font.color.rgb = color
    style.paragraph_format.space_before = Pt(14 if style_name == "Heading 1" else 10)
    style.paragraph_format.space_after = Pt(6)
    style.paragraph_format.keep_with_next = True

styles["Caption"].font.name = "Sylfaen"
styles["Caption"].font.size = Pt(8.5)
styles["Caption"].font.italic = True
styles["Caption"].font.color.rgb = MUTED

# ---------------------------------------------------------------- helpers
def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_margins(cell, top=80, bottom=80, left=100, right=100):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = tc_mar.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def add_page_number(paragraph):
    run = paragraph.add_run()
    fld_char_begin = OxmlElement("w:fldChar")
    fld_char_begin.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = " PAGE "
    fld_char_end = OxmlElement("w:fldChar")
    fld_char_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char_begin)
    run._r.append(instr_text)
    run._r.append(fld_char_end)
    run.font.name = "Sylfaen"
    run.font.size = Pt(8.5)
    run.font.color.rgb = MUTED


def add_header_footer():
    header = section.header
    header.is_linked_to_previous = False
    paragraph = header.paragraphs[0]
    paragraph.text = "OBD360 Web  ·  ავტომობილის დიაგნოსტიკის ვებ-პლატფორმა"
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in paragraph.runs:
        run.font.name = "Sylfaen"
        run.font.size = Pt(8.5)
        run.font.color.rgb = MUTED
    p_pr = paragraph._p.get_or_add_pPr()
    p_bdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "4")
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), "E4E0D7")
    p_bdr.append(bottom)
    p_pr.append(p_bdr)

    footer = section.footer
    footer.is_linked_to_previous = False
    paragraph = footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    label = paragraph.add_run("OBD360 Web  ·  2026   |   ")
    label.font.name = "Sylfaen"
    label.font.size = Pt(8.5)
    label.font.color.rgb = MUTED
    add_page_number(paragraph)


def h1(number, title):
    doc.add_page_break()
    paragraph = doc.add_paragraph(style="Heading 1")
    run = paragraph.add_run(f"{number}. {title}")
    run.font.name = "Sylfaen"
    run.font.size = Pt(18)
    run.font.bold = True
    run.font.color.rgb = SAGE
    return paragraph


def h2(number, title):
    paragraph = doc.add_paragraph(style="Heading 2")
    run = paragraph.add_run(f"{number}  {title}")
    run.font.name = "Sylfaen"
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = INK
    return paragraph


def h3(title):
    paragraph = doc.add_paragraph(style="Heading 3")
    run = paragraph.add_run(title)
    run.font.name = "Sylfaen"
    run.font.size = Pt(11.5)
    run.font.bold = True
    run.font.color.rgb = SAGE
    return paragraph


def p(text, bold_lead=None, italic=False, size=10.5, color=INK, space_after=6):
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(space_after)
    paragraph.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_lead:
        lead = paragraph.add_run(bold_lead)
        lead.font.name = "Sylfaen"
        lead.font.size = Pt(size)
        lead.font.bold = True
        lead.font.color.rgb = color
    run = paragraph.add_run(text)
    run.font.name = "Sylfaen"
    run.font.size = Pt(size)
    run.font.italic = italic
    run.font.color.rgb = color
    return paragraph


def bullet(text, level=0):
    paragraph = doc.add_paragraph(style="List Bullet")
    paragraph.paragraph_format.left_indent = Cm(0.7 + level * 0.5)
    paragraph.paragraph_format.space_after = Pt(3)
    run = paragraph.add_run(text)
    run.font.name = "Sylfaen"
    run.font.size = Pt(10)
    return paragraph


def code_block(lines):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    cell = table.rows[0].cells[0]
    cell.width = Cm(15.8)
    set_cell_shading(cell, CODE_BG)
    set_cell_margins(cell, 110, 110, 150, 150)
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.line_spacing = 1.0
    run = paragraph.add_run("\n".join(lines))
    run.font.name = "Consolas"
    run.font.size = Pt(8.2)
    run.font.color.rgb = RGBColor(0xE8, 0xEF, 0xE9)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def table(headers, rows, widths=None, font_size=8.5):
    table_obj = doc.add_table(rows=1, cols=len(headers))
    table_obj.style = "Table Grid"
    table_obj.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_obj.autofit = False
    header_row = table_obj.rows[0]
    for index, header in enumerate(headers):
        cell = header_row.cells[index]
        if widths:
            cell.width = Cm(widths[index])
        set_cell_shading(cell, "3F5D4E")
        set_cell_margins(cell, 70, 70, 90, 90)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
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
            if widths:
                cell.width = Cm(widths[index])
            set_cell_margins(cell, 60, 60, 90, 90)
            if row_index % 2 == 1:
                set_cell_shading(cell, "F7F5F0")
            paragraph = cell.paragraphs[0]
            paragraph.paragraph_format.space_after = Pt(0)
            paragraph.paragraph_format.line_spacing = 1.05
            run = paragraph.add_run(str(value))
            run.font.name = "Sylfaen"
            run.font.size = Pt(font_size)
            run.font.color.rgb = INK
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table_obj


def figure(path, caption, width_cm=15.5):
    doc.add_picture(str(path), width=Cm(width_cm))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph = doc.add_paragraph(style="Caption")
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(caption)
    run.font.name = "Sylfaen"
    run.font.size = Pt(8.5)
    run.font.italic = True
    run.font.color.rgb = MUTED


def callout(title, text_value):
    table_obj = doc.add_table(rows=1, cols=1)
    table_obj.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_obj.autofit = False
    cell = table_obj.rows[0].cells[0]
    cell.width = Cm(15.8)
    set_cell_shading(cell, "E9EFE9")
    set_cell_margins(cell, 120, 120, 160, 160)
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(2)
    run = paragraph.add_run(title)
    run.font.name = "Sylfaen"
    run.font.size = Pt(10)
    run.font.bold = True
    run.font.color.rgb = SAGE
    paragraph2 = cell.add_paragraph()
    paragraph2.paragraph_format.space_after = Pt(0)
    run2 = paragraph2.add_run(text_value)
    run2.font.name = "Sylfaen"
    run2.font.size = Pt(9.5)
    run2.font.color.rgb = INK
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


add_header_footer()

# ================================================================ TITLE PAGE
paragraph = doc.add_paragraph()
paragraph.paragraph_format.space_before = Pt(90)
paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
run = paragraph.add_run("სადიპლომო პროექტი")
run.font.name = "Sylfaen"
run.font.size = Pt(13)
run.font.bold = True
run.font.color.rgb = SAGE

paragraph = doc.add_paragraph()
paragraph.paragraph_format.space_before = Pt(20)
run = paragraph.add_run("OBD360 WEB")
run.font.name = "Sylfaen"
run.font.size = Pt(40)
run.font.bold = True
run.font.color.rgb = INK

paragraph = doc.add_paragraph()
run = paragraph.add_run("ავტომობილის დიაგნოსტიკის ვებ-პლატფორმა")
run.font.name = "Sylfaen"
run.font.size = Pt(20)
run.font.color.rgb = SAGE

paragraph = doc.add_paragraph()
paragraph.paragraph_format.space_before = Pt(50)
run = paragraph.add_run("პროექტის დოკუმენტაცია")
run.font.name = "Sylfaen"
run.font.size = Pt(14)
run.font.bold = True
run.font.color.rgb = INK

paragraph = doc.add_paragraph()
paragraph.paragraph_format.space_before = Pt(150)
run = paragraph.add_run("ავტორი: ზურაბ ლაზაშვილი")
run.font.name = "Sylfaen"
run.font.size = Pt(12)
run.font.color.rgb = INK

paragraph = doc.add_paragraph()
run = paragraph.add_run("2026")
run.font.name = "Sylfaen"
run.font.size = Pt(12)
run.font.color.rgb = MUTED

# ================================================================ ABSTRACT
doc.add_page_break()
doc.add_paragraph(style="Heading 1").add_run("რეზიუმე").font.name = "Sylfaen"
p("თანამედროვე ავტომობილები აღჭურვილია OBD-II (On-Board Diagnostics II) სისტემით, რომელიც მძღოლსა და ტექნიკურ სერვისს აძლევს წვდომას ძრავის, ემისიისა და სხვა ელექტრონული მოდულების დიაგნოსტიკურ მონაცემებზე. პრობლემა იმაშია, რომ მიღებული ინფორმაცია უმეტესად ტექნიკური კოდების სახითაა წარმოდგენილი და მძღოლისთვის გაუგებარია. OBD360 Web არის ვებ-პლატფორმა, რომელიც აკავშირებს OBD-II ადაპტერს ბრაუზერთან Web Bluetooth-ის საშუალებით, კითხულობს DTC კოდებსა და Live Data-ს, ინახავს სკანირების ისტორიას, ხსნის კოდებს ქართულ ენაზე და ეხმარება მომხმარებელს ტექნიკური მომსახურების დაგეგმვაში.")
p("სისტემა აგებულია Angular 22-ის, ASP.NET Core 10-ის, Entity Framework Core-ისა და SQL Server-ის გამოყენებით. ავტორიზაცია დაფუძნებულია JWT access token-სა და rotating refresh token-ზე; პაროლის აღდგენა ხდება ელფოსტით გაგზავნილი 6-ციფრიანი კოდით. DTC კატალოგი მოიცავს 13 629 ჩანაწერს. AI ასისტენტი მუშაობს n8n workflow-ისა და Google Gemini-ის მეშვეობით. ადმინისტრატორს შეუძლია მომხმარებლების, როლებისა და სკანირებების მართვა.")
p("პროექტი მოიცავს 32 REST endpoint-ს, 15 მონაცემთა მოდელს, 29 backend და 19 frontend ტესტს, C4 არქიტექტურულ დიაგრამებს, Swagger დოკუმენტაციასა და სტრუქტურირებულ ლოგირებას. ნაშრომში აღწერილია OBD-II-ის მუშაობის პრინციპი, სისტემის არქიტექტურა, მონაცემთა მოდელი, API, OBD-II ინტეგრაციის კოდი, უსაფრთხოება, ტესტირება და გაშვების ინსტრუქცია.")
p("საკვანძო სიტყვები: OBD-II, DTC, ECU, Web Bluetooth, Angular, ASP.NET Core, SQL Server, JWT, n8n, Gemini.", italic=True)

# ================================================================ ABSTRACT EN
doc.add_page_break()
doc.add_paragraph(style="Heading 1").add_run("Abstract").font.name = "Sylfaen"
p("Modern vehicles expose diagnostic data through the OBD-II (On-Board Diagnostics II) standard. The data is available, but it is usually presented as technical trouble codes that are difficult for a driver to interpret. OBD360 Web is a web platform that connects an OBD-II adapter to the browser through Web Bluetooth, reads diagnostic trouble codes (DTCs) and live sensor data, stores scan history, explains codes in Georgian, and helps users plan vehicle maintenance.")
p("The system is built with Angular 22, ASP.NET Core 10, Entity Framework Core, and SQL Server. Authentication uses a short-lived JWT access token and a rotating refresh token stored in an HttpOnly cookie. Password recovery is implemented with a six-digit email code. The DTC catalog contains 13,629 entries. An AI assistant is integrated through an n8n workflow and Google Gemini. Administrators can manage users, roles, and scan activity.")
p("The project includes 32 REST endpoints, 15 data models, 29 backend tests, 19 frontend tests, C4 architecture diagrams, Swagger documentation, and structured logging. This document describes the OBD-II domain, system architecture, data model, API, code-level integration, security, testing, deployment, and user guide.")
p("Keywords: OBD-II, DTC, ECU, Web Bluetooth, Angular, ASP.NET Core, SQL Server, JWT, n8n, Gemini.", italic=True)

# ================================================================ TOC
doc.add_page_break()
doc.add_paragraph(style="Heading 1").add_run("სარჩევი").font.name = "Sylfaen"
toc = [
    ("1", "შესავალი"),
    ("2", "OBD-II და ავტომობილის დიაგნოსტიკა"),
    ("3", "მოთხოვნები და გამოყენების სცენარები"),
    ("4", "სისტემის არქიტექტურა"),
    ("5", "მონაცემთა მოდელი"),
    ("6", "Backend — ASP.NET Core API"),
    ("7", "Frontend — Angular"),
    ("8", "OBD-II ინტეგრაცია კოდში"),
    ("9", "DTC კატალოგი"),
    ("10", "AI ასისტენტი — n8n და Gemini"),
    ("11", "შეხსენებები და ელფოსტა"),
    ("12", "უსაფრთხოება"),
    ("13", "ტესტირება და ხარისხი"),
    ("14", "გაშვება და ინსტალაცია"),
    ("15", "მომხმარებლის გზამკვლევი"),
    ("16", "შეზღუდვები და მომავალი სამუშაო"),
    ("17", "დასკვნა"),
    ("", "ბიბლიოგრაფია"),
    ("", "დანართი A — REST API"),
    ("", "დანართი B — პროექტის სტრუქტურა"),
]
for number, title in toc:
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(3)
    run = paragraph.add_run(f"{number + '  ' if number else ''}{title}")
    run.font.name = "Sylfaen"
    run.font.size = Pt(11)
    run.font.color.rgb = INK if number else MUTED

# ================================================================ 1. INTRODUCTION
h1("1", "შესავალი")
h2("1.1", "პრობლემის აქტუალურობა")
p("ავტომობილის ელექტრონული სისტემები დღეს ათეულობით მოდულს მოიცავს. ძრავის მართვის ბლოკი (ECU) განუწყვეტლივ ამუშავებს სენსორების მონაცემებს და აღრიცხავს გადახრებს. როდესაც სისტემა პოულობს ხარვეზს, ის ინახავს DTC (Diagnostic Trouble Code) კოდს და აანთებს Check Engine ინდიკატორს. მძღოლს შეუძლია კოდის წაკითხვა იაფი OBD-II ადაპტერით, მაგრამ მიღებული შედეგი, მაგალითად P0300 ან P0A80, თავისთავად არაფერს ამბობს.")
p("ამის შედეგად მომხმარებელი ხშირად მიდის სერვისში მხოლოდ იმისთვის, რომ გაიგოს კოდის მნიშვნელობა, ან პირიქით — უგულებელყოფს სერიოზულ ხარვეზს. სკანირების ისტორია, გარბენი და ტექნიკური მომსახურების ვადები ჩვეულებრივ იფანტება სხვადასხვა ჩანაწერში. OBD360 Web სწორედ ამ სამ პრობლემას პასუხობს: კოდის გაგება, ისტორიის შენახვა და პრევენციული შეხსენებები.")

h2("1.2", "პროექტის მიზანი")
p("მიზანია შეიქმნას ვებ-პლატფორმა, რომელიც მომხმარებელს საშუალებას აძლევს ბრაუზერიდან დაუკავშირდეს OBD-II ადაპტერს, წაიკითხოს ავტომობილის დიაგნოსტიკური მონაცემები, მიიღოს მათი გასაგები ახსნა ქართულად და შეინახოს შედეგები პირად ისტორიაში. სისტემა უნდა იყოს მარტივი მძღოლისთვის, სასარგებლო ტექნიკური სპეციალისტისთვის და კონტროლირებადი ადმინისტრატორისთვის.")

h2("1.3", "ამოცანები")
for item in [
    "OBD-II სტანდარტის, 16-pin კონექტორის, CAN/K-line პროტოკოლების, PID-ებისა და DTC კოდების შესწავლა.",
    "Angular-ზე დაფუძნებული standalone ვებ-აპლიკაციის შექმნა; Web Bluetooth-ით ადაპტერთან დაკავშირება.",
    "ASP.NET Core REST API-ის, JWT ავტორიზაციისა და refresh token-ის როტაციის რეალიზაცია.",
    "SQL Server-ის მონაცემთა მოდელისა და EF Core მიგრაციების შექმნა.",
    "13 629 DTC კოდის კატალოგის ინტეგრაცია და ქართული ახსნების მიწოდება.",
    "n8n + Gemini-ის AI ასისტენტის ინტეგრაცია.",
    "ტექნიკური მომსახურების შეხსენებები და ელფოსტით გაგზავნა.",
    "ადმინისტრატორის პანელი მომხმარებლების, როლებისა და სკანირებების სამართავად.",
    "ტესტირება, ლოგირება, Swagger დოკუმენტაცია და C4 არქიტექტურა.",
]:
    bullet(item)

h2("1.4", "პროექტის საზღვრები")
p("სისტემა განკუთვნილია OBD-II თავსებადი მსუბუქი ავტომობილებისთვის და ELM327-ის ტიპის BLE ადაპტერებისთვის. ბრაუზერიდან მუშაობს Web Bluetooth-ის მხარდამჭერ გარემოში (Chrome/Edge; HTTPS ან localhost). პროექტი არ აკეთებს ECU-ის პროგრამირებას, არ ცვლის მანქანის პარამეტრებს და არ იძლევა დიაგნოზის სამედიცინო სიზუსტის გარანტიას. რემაინდერები ამჟამად მხოლოდ თარიღით მუშაობს; გარბენით რემაინდერისთვის საჭიროა ოდომეტრის მონაცემის შენახვა, რაც მომავალი სამუშაოა.")

h2("1.5", "მეთოდოლოგია")
p("პროექტი შესრულებულია იტერაციული მიდგომით: ჯერ შეიქმნა მონაცემთა მოდელი და ავტორიზაცია, შემდეგ ავტომობილისა და სკანირების ფუნქციონალი, შემდეგ DTC კატალოგი, AI ინტეგრაცია, რემაინდერები და ადმინის პანელი. არქიტექტურა აღწერილია C4 მოდელით (Context, Container, Component), API — OpenAPI/Swagger-ით, ხოლო ხარისხი — ავტომატური ტესტებითა და ხელით E2E სცენარებით.")

# ================================================================ 2. OBD-II
h1("2", "OBD-II და ავტომობილის დიაგნოსტიკა")
h2("2.1", "რა არის OBD-II")
p("OBD-II (On-Board Diagnostics II) არის ავტომობილის ჩაშენებული დიაგნოსტიკის სტანდარტი, რომელიც აშშ-ში 1996 წლიდან სავალდებულო გახდა მსუბუქი ავტომობილებისთვის; ევროპაში მისი ანალოგი EOBD 2001 წლიდან დაინერგა. სტანდარტი აერთიანებს ფიზიკურ კონექტორს, ელექტრულ ინტერფეისს, კომუნიკაციის პროტოკოლებსა და დიაგნოსტიკური მომსახურებების (services) ერთობლიობას. მისი მთავარი დანიშნულება ემისიის კონტროლი და ძრავის მუშაობის მონიტორინგია, თუმცა პრაქტიკაში ის სხვა მოდულების დიაგნოსტიკისთვისაც გამოიყენება.")
figure(ASSETS / "obd-connector.png", "ნახ. 1. OBD-II 16-pin დიაგნოსტიკური კონექტორი და ძირითადი პინები.")

h2("2.2", "16-pin კონექტორი და პინები")
p("სტანდარტული OBD-II კონექტორი 16-პინიანია და მდებარეობს საჭის ქვეშ, ჩვეულებრივ მძღოლის მხარეს. ყველა თანამედროვე ავტომობილს აქვს იგივე ფორმის პორტი, თუმცა პინების გამოყენება პროტოკოლის მიხედვით იცვლება.")
table(
    ["პინი", "დანიშნულება", "აღწერა"],
    [
        ("4", "Chassis ground", "ელექტრული მიწა"),
        ("5", "Signal ground", "სიგნალის მიწა"),
        ("6", "CAN-H", "CAN bus-ის მაღალი ხაზი"),
        ("14", "CAN-L", "CAN bus-ის დაბალი ხაზი"),
        ("7", "K-line", "ISO 9141 / ISO 14230"),
        ("15", "L-line", "ძველი ინტერფეისი"),
        ("16", "Battery +", "12V კვება"),
    ],
    [2.2, 4.2, 8.6],
)
p("კონექტორის 16 pin-იდან ყველა ერთდროულად არ გამოიყენება. ELM327 ადაპტერი ავტომატურად ამოწმებს ხელმისაწვდომ პროტოკოლს და ირჩევს შესაბამის პინებს. სწორედ ამიტომ ერთი და იგივე ადაპტერი მუშაობს სხვადასხვა მწარმოებლის ავტომობილთან.")

h2("2.3", "ECU და ელექტრონული მოდულები")
p("ECU (Electronic Control Unit) არის ავტომობილის ელექტრონული მართვის ბლოკი. თანამედროვე მანქანაში ათობით მოდულია: ძრავის ECU, ABS/ESP, უსაფრთხოების ბალიშების (SRS), ძარის (BCM), ტრანსმისიის, კლიმატისა და ინფოტეინმენტის მოდულები. OBD-II პორტი პირველ რიგში ძრავის ECU-სთან კომუნიკაციისთვისაა განკუთვნილი, მაგრამ მწარმოებლის მიხედვით შესაძლებელია სხვა მოდულების წვდომაც.")
p("ECU ამუშავებს სენსორების სიგნალებს (ბრუნი, ჰაერის ხარჯი, ტემპერატურა, ჟანგბადის დონე, ძაბვა), ადარებს მათ მოსალოდნელ მნიშვნელობებს და ხარვეზის აღმოჩენისას ინახავს DTC-ს. ზოგიერთი კოდი დროებითია (pending), ზოგი — დადასტურებული (stored), ზოგი კი ემისიის მონიტორინგისთვის permanent რეჟიმში ინახება.")

h2("2.4", "პროტოკოლები: CAN და K-line")
p("თანამედროვე ავტომობილების უმეტესობა იყენებს CAN (Controller Area Network) bus-ს, ჩვეულებრივ 500 kbps სიჩქარით. OBD-II კონტექსტში ხშირად გამოიყენება ISO 15765-4 (CAN-ზე დაფუძნებული დიაგნოსტიკა). ძველი მოდელები იყენებენ ISO 9141-2 ან ISO 14230-4 (K-line) პროტოკოლებს. ELM327 ადაპტერი ავტომატურად ცდილობს პროტოკოლის ამოცნობას; ხელით შერჩევაც შესაძლებელია `ATSP` ბრძანებით.")
p("CAN-ის უპირატესობაა მაღალი სიჩქარე, მრავალმოდულიანი კომუნიკაცია და სტანდარტიზებული frame-ები. ამიტომ Live Data-სა და DTC-ის წაკითხვისას OBD360 ცდილობს დაადგინოს, CAN-ის რეჟიმია თუ არა, რათა პასუხი სწორად გაშიფროს.")

h2("2.5", "PID — Parameter ID")
p("PID არის პარამეტრის იდენტიფიკატორი, რომლითაც ECU-ს კონკრეტული მონაცემი მოეთხოვება. მოთხოვნა იგზავნება რეჟიმ 01-ში (მიმდინარე მონაცემები), ხოლო პასუხი შეიცავს 0x40 + PID ბაიტს და მონაცემებს. მაგალითად, `010C` ითხოვს ძრავის ბრუნს, `010D` — სიჩქარეს, `0105` — გამაგრილებლის ტემპერატურას, `0142` — ელექტროსისტემის ძაბვას.")
table(
    ["PID", "პარამეტრი", "ერთეული", "ფორმულა"],
    [
        ("010C", "Engine RPM", "rpm", "((A × 256) + B) / 4"),
        ("010D", "Vehicle speed", "km/h", "A"),
        ("0105", "Coolant temperature", "°C", "A − 40"),
        ("0111", "Throttle position", "%", "A × 100 / 255"),
        ("0142", "Control module voltage", "V", "((A × 256) + B) / 1000"),
    ],
    [2.2, 6.2, 3.0, 5.0],
)
p("OBD360-ის Live Data ეკრანი 500 ms ინტერვალით კითხულობს PID-ებს და ინახავს LiveReading ჩანაწერებს. გრაფიკი იძლევა ტენდენციის დანახვის საშუალებას — მაგალითად, გაგრილების ტემპერატურის მატებას ან ძაბვის ვარდნას.")

h2("2.6", "DTC — Diagnostic Trouble Code")
p("DTC არის ხუთსიმბოლოიანი კოდი, რომელიც აღწერს კონკრეტულ ხარვეზს. პირველი სიმბოლო განსაზღვრავს სისტემას: P — Powertrain (ძრავი/ტრანსმისია), B — Body (ძარა), C — Chassis (შასი), U — Network (ქსელი). მეორე სიმბოლო მიუთითებს, არის თუ არა კოდი სტანდარტული (0) თუ მწარმოებლის სპეციფიკური (1). დანარჩენი სამი სიმბოლო კონკრეტულ ხარვეზს აღნიშნავს.")
p("მაგალითად, P0300 ნიშნავს ცილინდრების გამოტოვებას (misfire), P0420 — კატალიზატორის დაბალ ეფექტურობას, P0A80 — ჰიბრიდული ბატარეის შეცვლის აუცილებლობას. DTC კოდის მხოლოდ წაკითხვა საკმარისი არ არის: მნიშვნელოვანია freeze frame მონაცემები, კოდის გამოჩენის სიხშირე და სხვა კოდებთან კავშირი.")
code_block([
    "43 01 33 00 00 00 00",
    "43 = response to mode 03",
    "01 33 = DTC bytes -> P0133",
])

h2("2.7", "დიაგნოსტიკური რეჟიმები")
table(
    ["რეჟიმი", "დანიშნულება", "OBD360-ში"],
    [
        ("01", "მიმდინარე PID მონაცემები", "Live Data"),
        ("03", "Stored DTC", "სკანირება"),
        ("07", "Pending DTC", "სკანირება"),
        ("0A", "Permanent DTC", "სკანირება"),
        ("04", "Clear DTC / freeze frame", "კოდების გასუფთავება"),
        ("0902", "VIN", "ავტომობილის იდენტიფიკაცია"),
        ("0101", "Readiness monitors", "სკანირების სტატუსი"),
    ],
    [2.0, 6.8, 7.0],
)
p("რეჟიმ 04-ს აქვს გვერდითი ეფექტი: ის შლის freeze frame-ს და აბრუნებს readiness მონიტორებს. ამიტომ OBD360 კოდების გასუფთავებას მხოლოდ მომხმარებლის დადასტურების შემდეგ აკეთებს და შედეგს ცალკე აჩვენებს.")

# ================================================================ 3. REQUIREMENTS
h1("3", "მოთხოვნები და გამოყენების სცენარები")
h2("3.1", "ფუნქციური მოთხოვნები")
table(
    ["ID", "მოთხოვნა", "აღწერა"],
    [
        ("FR-01", "რეგისტრაცია/ავტორიზაცია", "ელფოსტა + პაროლი, JWT და refresh cookie"),
        ("FR-02", "პაროლის აღდგენა", "6-ციფრიანი კოდი ელფოსტით, 10 წუთი"),
        ("FR-03", "მანქანების მართვა", "CRUD, VIN, მოდელი, წელი"),
        ("FR-04", "Bluetooth დაკავშირება", "ELM327 BLE ადაპტერთან დაკავშირება"),
        ("FR-05", "Live Data", "RPM, სიჩქარე, ტემპერატურა, ძაბვა"),
        ("FR-06", "DTC სკანირება", "03/07/0A რეჟიმები და ისტორია"),
        ("FR-07", "კოდების გასუფთავება", "04 რეჟიმი დადასტურებით"),
        ("FR-08", "DTC კატალოგი", "ძებნა, დეტალები, სირთულე, ხარჯი"),
        ("FR-09", "AI ასისტენტი", "კითხვა ქართულად, სკანირების კონტექსტით"),
        ("FR-10", "შეხსენებები", "თარიღით ვადა, email digest"),
        ("FR-11", "ადმინის პანელი", "users, roles, scans, delete"),
        ("FR-12", "რესპონსიული UI", "მობილურზე burger drawer"),
    ],
    [1.8, 4.5, 9.5],
)

h2("3.2", "არაფუნქციური მოთხოვნები")
table(
    ["ID", "მოთხოვნა", "კრიტერიუმი"],
    [
        ("NFR-01", "უსაფრთხოება", "JWT, refresh rotation, hash, CORS, role checks"),
        ("NFR-02", "წარმადობა", "API პასუხი < 2 წმ ჩვეულებრივი დატვირთვით"),
        ("NFR-03", "თავსებადობა", "Chrome/Edge, Web Bluetooth, Android/Desktop"),
        ("NFR-04", "რესპონსიულობა", "360px–1920px, mobile drawer"),
        ("NFR-05", "შენარჩუნებადობა", "ფენები, DTO, service, standalone components"),
        ("NFR-06", "ტესტირებადობა", "backend/frontend ავტომატური ტესტები"),
        ("NFR-07", "ლოკალიზაცია", "ქართული ინტერფეისი და კატალოგი"),
        ("NFR-08", "დაკვირვებადობა", "HTTP/auth/reminder ლოგები, Swagger"),
    ],
    [1.8, 4.2, 9.8],
)

h2("3.3", "როლები")
table(
    ["როლი", "უფლებები"],
    [
        ("Guest", "login/register/forgot-password; დაცული გვერდები მიუწვდომელია"),
        ("User", "საკუთარი მანქანები, სკანირებები, შეხსენებები, AI, პარამეტრები"),
        ("Admin", "ყველა User უფლება + users/scans/roles მართვა"),
    ],
    [3.2, 12.6],
)

h2("3.4", "გამოყენების სცენარები")
table(
    ["სცენარი", "ნაბიჯები", "შედეგი"],
    [
        ("UC-01", "რეგისტრაცია → login", "ახალი ანგარიში და სესია"),
        ("UC-02", "მანქანის დამატება → ადაპტერთან დაკავშირება", "Bluetooth სესია"),
        ("UC-03", "სკანირება → კოდების ნახვა", "DTC + კატალოგის ახსნა"),
        ("UC-04", "კოდის გასუფთავება", "04 დადასტურება, ახალი სკანირება"),
        ("UC-05", "AI კითხვა", "ქართული ტექნიკური პასუხი"),
        ("UC-06", "ადმინი → user/role/delete", "სისტემის მართვა"),
    ],
    [2.2, 8.6, 5.0],
)

# ================================================================ 4. ARCHITECTURE
h1("4", "სისტემის არქიტექტურა")
h2("4.1", "ზოგადი მიმოხილვა")
p("OBD360 Web აგებულია სამფენიან არქიტექტურაზე. წარმოდგენის ფენა არის Angular-ის ერთგვერდიანი აპლიკაცია; ბიზნეს ლოგიკა და მონაცემებზე წვდომა რეალიზებულია ASP.NET Core REST API-ში; მონაცემები ინახება SQL Server-ში EF Core-ის მეშვეობით. ბრაუზერი პირდაპირ ბაზას არ უკავშირდება — მხოლოდ HTTPS/JSON API-ს.")
p("OBD-II ინტეგრაცია განსაკუთრებულია: ფიზიკურ ადაპტერთან კომუნიკაცია ხდება კლიენტის მხარეს, Web Bluetooth API-ით. სერვერი ვერ ხედავს Bluetooth მოწყობილობას; ამიტომ ადაპტერის ბრძანებები და პასუხების გაშიფვრა frontend-შია, ხოლო შედეგები API-ში ინახება.")

h2("4.2", "C4 Context")
p("სისტემის კონტექსტში გამოყოფილია: მომხმარებელი (მძღოლი/ტექნიკოსი), OBD-II ადაპტერი, OBD360 Web, SQL Server, SMTP, n8n და Gemini. მომხმარებელი ბრაუზერით მართავს აპლიკაციას; ადაპტერი მანქანის ECU-სთან ურთიერთობს; სერვისი იყენებს მონაცემთა ბაზას, უგზავნის ელფოსტას და იძახებს AI workflow-ს.")

h2("4.3", "C4 Container")
p("კონტეინერების დონეზე Angular SPA, ASP.NET Core API და SQL Server ქმნიან ბირთვს. n8n არის ცალკე სერვისი, რომელიც იღებს API-ის მოთხოვნას და აორკესტრირებს Gemini-ის გამოძახებას. SMTP სერვისი გამოიყენება პაროლის აღდგენის კოდებისა და რემაინდერებისთვის.")
figure(SLIDE_ASSETS / "c4-container.png", "ნახ. 2. C4 Container დიაგრამა — ძირითადი კონტეინერები და ურთიერთობები.", 15.5)

h2("4.4", "მონაცემთა ნაკადი")
figure(ASSETS / "obd-flow.png", "ნახ. 3. OBD-II კავშირის ნაკადი: ECU → პორტი → ადაპტერი → ბრაუზერი → OBD360.", 16.2)
p("ტიპიური სკანირების ნაკადი: მომხმარებელი ირჩევს მანქანას → აპლიკაცია ითხოვს Bluetooth მოწყობილობას → ELM327-ის ინიციალიზაცია → PID/DTC ბრძანებები → პასუხების გაშიფვრა → შედეგის API-ში შენახვა → UI-ში ჩვენება და AI/კატალოგის ახსნა.")

h2("4.5", "ტექნოლოგიური სტეკი")
table(
    ["ფენა", "ტექნოლოგია", "დანიშნულება"],
    [
        ("Frontend", "Angular 22, TypeScript, SCSS", "SPA, standalone components, signals"),
        ("HTTP", "Angular HttpClient, interceptors", "REST, JWT header, refresh"),
        ("Backend", "ASP.NET Core 10", "REST API, DI, middleware"),
        ("ORM", "EF Core 10", "SQL Server mapping, migrations"),
        ("Identity", "ASP.NET Identity", "users, roles, password hashing"),
        ("Auth", "JWT + refresh cookie", "access/refresh tokens"),
        ("DB", "SQL Server / LocalDB", "relational data"),
        ("AI", "n8n + Google Gemini", "workflow, explanations"),
        ("Email", "SMTP (Gmail)", "reset codes, reminders"),
        ("Tests", "xUnit, Vitest", "backend/frontend"),
        ("Docs", "Swagger/OpenAPI, C4", "API and architecture"),
    ],
    [2.8, 6.2, 6.8],
)

# ================================================================ 5. DATA MODEL
h1("5", "მონაცემთა მოდელი")
h2("5.1", "მიმოხილვა")
p("სისტემა იყენებს 15 ძირითად მოდელს, რომლებიც 21 ფიზიკურ ცხრილად იშლება Identity-ის ცხრილების ჩათვლით. მოდელები დაყოფილია ავტორიზაციის, ავტომობილის, დიაგნოსტიკის, კატალოგის, AI-ისა და შეტყობინებების დომენებად.")
figure(ASSETS / "data-model.png", "ნახ. 4. მონაცემთა მოდელის ბირთვი და ძირითადი ურთიერთობები.", 16.0)

h2("5.2", "მოდელები")
table(
    ["მოდელი", "დანიშნულება", "ძირითადი ველები"],
    [
        ("ApplicationUser", "მომხმარებელი", "Id, Email, DisplayName, CreatedAt"),
        ("ApplicationRole", "როლი", "Id, Name (User/Admin)"),
        ("Vehicle", "ავტომობილი", "Make, Model, Year, VIN, Plate"),
        ("Adapter", "Bluetooth ადაპტერი", "Name, Address, UserId, VehicleId"),
        ("ScanSession", "სკანირების სესია", "VehicleId, StartedAt, EndedAt"),
        ("LiveReading", "PID გაზომვა", "SessionId, Pid, Value, RecordedAt"),
        ("DtcRecord", "სკანირების კოდი", "SessionId, Code, Severity"),
        ("DtcCatalogEntry", "კატალოგის ჩანაწერი", "Code, TitleKa, Description, Cost"),
        ("MaintenanceReminder", "ტექნიკური შეხსენება", "VehicleId, Type, DueAtDate, Status"),
        ("AiConversation", "AI საუბარი", "UserId, Title, CreatedAt"),
        ("AiMessage", "AI შეტყობინება", "ConversationId, Role, Content"),
        ("Report", "რეპორტი", "VehicleId, Type, GeneratedAt"),
        ("NotificationLog", "შეტყობინების ლოგი", "UserId, Channel, Type, Status"),
        ("UserPreference", "პარამეტრები", "UserId, UnitSystem, Theme"),
        ("RefreshSession", "refresh სესია", "UserId, TokenHash, ExpiresAt"),
    ],
    [4.0, 4.8, 7.0],
    font_size=8.2,
)

h2("5.3", "ურთიერთობები")
for item in [
    "User 1–N Vehicle: ერთ მომხმარებელს შეიძლება ჰქონდეს რამდენიმე მანქანა.",
    "Vehicle 1–N ScanSession: თითოეული სკანირება კონკრეტულ მანქანას ეკუთვნის.",
    "ScanSession 1–N DtcRecord / LiveReading: სესია აერთიანებს კოდებსა და გაზომვებს.",
    "DtcRecord N–1 DtcCatalogEntry: კოდი კატალოგის ჩანაწერს უკავშირდება (კოდით).",
    "Vehicle 1–N MaintenanceReminder: შეხსენება მანქანაზეა მიბმული.",
    "User 1–N AiConversation 1–N AiMessage: საუბრის ისტორია.",
    "User 1–N NotificationLog: გაგზავნილი შეტყობინებების დუბლიკატის კონტროლი.",
]:
    bullet(item)

h2("5.4", "მიგრაციები და საწყისი მონაცემები")
p("სქემა იმართება EF Core მიგრაციებით. `database/schema.sql` და `database/seed.sql` შეიცავს SQL ვერსიას, რომელიც შემოწმებულია ცალკე ბაზაზე. აპლიკაციის გაშვებისას `Database.MigrateAsync()` ცდილობს სქემის განახლებას, ხოლო DTC კატალოგის ცარიელი ცხრილი ივსება 13 629 ჩანაწერით. საწყისი როლები — User და Admin — იქმნება იმავე ინიციალიზაციის დროს.")

# ================================================================ 6. BACKEND
h1("6", "Backend — ASP.NET Core API")
h2("6.1", "ფენები და სტრუქტურა")
p("Backend დაყოფილია სამ პროექტად: `Obd360.Api` (controllers, middleware, DI, integrations), `Obd360.Core` (entities, enums, interfaces) და `Obd360.Infrastructure` (DbContext, EF configurations, Identity, services, migrations). ეს გამიჯვნა ამარტივებს ტესტირებას და ცვლილებების იზოლაციას.")
table(
    ["კომპონენტი", "პასუხისმგებლობა"],
    [
        ("Controllers", "HTTP მარშრუტიზაცია, ვალიდაცია, status codes"),
        ("Services", "token, email, reset code, reminders, AI"),
        ("Infrastructure", "EF Core, Identity, migrations, SMTP"),
        ("Integrations/N8n", "AI workflow-ის გამოძახება"),
        ("Middleware", "HTTP logging, error handling"),
        ("Swagger", "OpenAPI დოკუმენტაცია"),
    ],
    [4.0, 11.8],
)

h2("6.2", "კონტროლერები და endpoint-ები")
table(
    ["კონტროლერი", "Base route", "Endpoint-ები"],
    [
        ("AuthController", "/api/v1/auth", "register, login, refresh, logout, forgot, reset, change-password"),
        ("PreferencesController", "/api/v1/preferences", "get, update"),
        ("VehiclesController", "/api/v1/vehicles", "list, get, create, update, delete"),
        ("RemindersController", "/api/v1/reminders", "list, create, update, delete, complete"),
        ("ScansController", "/api/v1/scans", "list, create"),
        ("DtcCatalogController", "/api/v1/dtc-catalog", "list/search, detail"),
        ("AiController", "/api/v1/ai", "status, latest report, ask, conversation"),
        ("AdminController", "/api/v1/admin", "overview, users, delete, toggle-role, scans"),
    ],
    [4.2, 4.8, 6.8],
    font_size=8.2,
)
p("სულ რეგისტრირებულია 32 REST endpoint. ყველა პასუხი JSON-ის ფორმატშია; ავტორიზებული endpoint-ები იღებენ `Authorization: Bearer <token>` header-ს. ვალიდაციის შეცდომები ბრუნდება `ValidationProblemDetails`-ით, ხოლო ავტორიზაციისა — 401/403 status-ებით.")

h2("6.3", "ავტორიზაცია და token-ები")
p("ავტორიზაცია დაფუძნებულია ASP.NET Identity-ზე. პაროლი ინახება hash-ით; მომხმარებლის ელფოსტა უნიკალურია. წარმატებული login-ის შემდეგ იქმნება მოკლევადიანი JWT access token (15 წუთი) და გრძელვადიანი refresh token (30 დღე), რომელიც ინახება HttpOnly cookie-ში. Refresh token ბაზაში ინახება SHA-256 hash-ის სახით და ყოველი განახლებისას იცვლება (rotation).")
code_block([
    "Jwt:AccessTokenMinutes = 15",
    "Jwt:RefreshTokenDays   = 30",
    "refresh cookie: HttpOnly, Secure, SameSite=Strict",
    "logout/password change -> revoke all refresh sessions",
])
p("JWT შეიცავს userId, email, role claim-ებს. API ამოწმებს issuer-ს, audience-ს, signing key-სა და ვადას. როლებზე დაშვება ხდება `[Authorize(Roles = \"Admin\")]` ატრიბუტით. access token-ის მოკლე სიცოცხლე ამცირებს მოპარული token-ის რისკს; refresh token-ის rotation თავიდან ირიდებს ხელახლა გამოყენებას.")

h2("6.4", "პაროლის აღდგენა")
p("პაროლის აღდგენა ხდება ელფოსტით გაგზავნილი 6-ციფრიანი კოდით. კოდი მოქმედებს 10 წუთი, აქვს 5 მცდელობა და ერთჯერადია. კოდები ინახება ფაილურ საცავში (`App_Data/password-reset-codes.json`), რაც გადაიტანს API-ის გადატვირთვას. წარმატებული reset-ის შემდეგ ყველა refresh session უქმდება.")
p("უსაფრთხოებისთვის პასუხი არ ამხელს, არსებობს თუ არა მოცემული ელფოსტა: ბრუნდება ზოგადი შეტყობინება. Development გარემოში, SMTP-ის არარსებობისას, კოდი ბრუნდება `devCode`-ში მხოლოდ ლოკალური ტესტირებისთვის.")

h2("6.5", "ადმინის API")
p("AdminController დაცულია Admin როლით და იძლევა სისტემის მართვის საშუალებას. გვერდი `/app/admin` იღებს რეალურ მონაცემებს: users, vehicles, scans, DTC count. მომხმარებლის წაშლისას იშლება მისი Adapter ჩანაწერები და Identity ანგარიში; საკუთარი თავის ან ბოლო Admin-ის წაშლა დაბლოკილია. როლის გადართვა იცავს იმავე წესებს.")
table(
    ["Endpoint", "აღწერა"],
    [
        ("GET /admin/overview", "users/vehicles/scans/DTC რაოდენობები"),
        ("GET /admin/users?search=", "მომხმარებლები, როლები, აქტივობა"),
        ("DELETE /admin/users/{id}", "მომხმარებლის წაშლა"),
        ("POST /admin/users/{id}/toggle-role", "Admin როლის დამატება/მოხსნა"),
        ("GET /admin/scans?search=", "ყველა სკანირება"),
    ],
    [7.0, 8.8],
)

h2("6.6", "ლოგირება")
p("API იყენებს ჩაშენებულ `ILogger`-ს. HTTP logging აღრიცხავს method-ს, path-ს, status code-სა და ხანგრძლივობას. Auth ლოგები მოიცავს რეგისტრაციას, login success/failure-ს, პაროლის reset/change-ს; reminder სერვისი — გაგზავნასა და შეცდომებს. ლოგები არ შეიცავს პაროლს, token-ს ან reset კოდს.")
code_block([
    "info: Microsoft.AspNetCore.HttpLogging[1]",
    "      Request: GET /api/v1/admin/overview",
    "info: Microsoft.AspNetCore.HttpLogging[2]",
    "      Response: StatusCode: 200",
    "info: Microsoft.AspNetCore.HttpLogging[8]",
    "      Duration: 42.7ms",
])

h2("6.7", "Swagger")
p("Swagger UI ხელმისაწვდომია `http://localhost:5269/swagger` მისამართზე. კონფიგურაცია შეიცავს API სათაურს, ვერსიას, JWT Authorize ღილაკსა და XML კომენტარებს Admin/Auth endpoint-ებისთვის. Bearer ტოკენის შეყვანის შემდეგ დაცული endpoint-ები პირდაპირ UI-დან გამოიძახება, რაც ხელს უწყობს ხელით ტესტირებას.")

# ================================================================ 7. FRONTEND
h1("7", "Frontend — Angular")
h2("7.1", "არქიტექტურა")
p("Frontend არის Angular 22-ის standalone აპლიკაცია. არ არის NgModule-ები; თითოეული component დამოუკიდებლად აცხადებს საკუთარ იმპორტებს. მარშრუტები lazy-loaded-ია, რაც ამცირებს საწყის bundle-ს. მდგომარეობა იმართება Signals-ით, ხოლო HTTP ოპერაციები — RxJS Observable-ებით, რაც Angular-ის სტანდარტულ მიდგომას შეესაბამება.")
table(
    ["ფენა", "მაგალითები", "დანიშნულება"],
    [
        ("core/services", "Auth, ObdBluetooth, DtcScan, VehiclesApi", "ბიზნეს და API ლოგიკა"),
        ("core/guards", "authGuard, adminGuard", "მარშრუტების დაცვა"),
        ("core/interceptors", "authInterceptor", "JWT header, refresh"),
        ("features", "garage, reminders, admin, live-data", "ეკრანები"),
        ("layout", "main-layout", "sidebar, header, responsive drawer"),
        ("shared", "UI helpers", "საერთო ელემენტები"),
    ],
    [4.0, 7.0, 4.8],
)

h2("7.2", "მარშრუტები და კომპონენტები")
table(
    ["მარშრუტი", "კომპონენტი", "დანიშნულება"],
    [
        ("/login", "Login", "ავტორიზაცია"),
        ("/register", "Register", "რეგისტრაცია"),
        ("/forgot-password", "ForgotPassword", "კოდით აღდგენა"),
        ("/app/dashboard", "Dashboard", "მიმოხილვა"),
        ("/app/garage", "Garage", "მანქანები"),
        ("/app/reminders", "Reminders", "შეხსენებები"),
        ("/app/bluetooth", "Bluetooth", "ადაპტერი"),
        ("/app/live-data", "LiveData", "PID გრაფიკები"),
        ("/app/dtc-scanner", "DtcScanner", "DTC სკანირება"),
        ("/app/ecu-modules", "EcuModules", "მოდულები"),
        ("/app/scan-history", "ScanHistory", "ისტორია"),
        ("/app/ai-assistant", "AiAssistant", "AI"),
        ("/app/settings", "Settings", "პარამეტრები"),
        ("/app/admin", "Admin", "ადმინი"),
    ],
    [4.4, 4.4, 7.0],
    font_size=8.2,
)
p("სულ 17 feature/layout კომპონენტია. `authGuard` ზღუდავს არაავტორიზებულ მომხმარებელს, ხოლო `adminGuard` — არაადმინისტრატორს. Admin ბმული sidebar-ში მხოლოდ მაშინ ჩნდება, როცა მიმდინარე მომხმარებლის როლებში Admin არის.")

h2("7.3", "State management სიგნალებით")
p("Auth სერვისი ინახავს access token-სა და მიმდინარე მომხმარებელს Signals-ის სახით. UserSettings ინახავს თემას, ერთეულების სისტემასა და refresh ინტერვალს; ცვლილებები აისახება localStorage-ში. Dashboard, Garage, Reminders, Scan History და Admin იყენებენ `signal`/`computed`-ს ფილტრაციისა და ჯამებისთვის. ეს ამცირებს manual change detection-ის საჭიროებას.")
code_block([
    "readonly currentUser = signal<CurrentUser | null>(null);",
    "readonly isAdmin = computed(",
    "  () => this.currentUser()?.roles.includes('Admin') ?? false",
    ");",
])

h2("7.4", "UI/UX და რესპონსიულობა")
p("ინტერფეისი იყენებს ღია, თბილ პალიტრას: რბილი კრემისფერი ფონი, მუქი მწვანე აქცენტი და თეთრი ბარათები. ტიპოგრაფია ეფუძნება Manrope/Noto Sans Georgian-ს. მობილურზე 720px-ზე ნაკლები სიგანისას sidebar გადაიქცევა მარცხენა off-canvas drawer-ად, იხსნება ბურგერ ღილაკით და იხურება overlay-ზე ან ნავიგაციაზე დაჭერით. ღია drawer-ის დროს ფონი არ სქროლავს.")
figure(SLIDE_ASSETS / "dashboard.png", "ნახ. 5. Dashboard — Live Data, DTC და აქტივობის მიმოხილვა.", 14.5)
figure(SLIDE_ASSETS / "garage.png", "ნახ. 6. Garage — მანქანების სია და CRUD ოპერაციები.", 14.5)
figure(SLIDE_ASSETS / "reminders.png", "ნახ. 7. Reminders — ვადები, Overdue სტატუსი და დასრულება.", 14.5)
figure(SLIDE_ASSETS / "mobile-menu.png", "ნახ. 8. მობილური ნავიგაცია — მარცხენა burger drawer.", 7.0)
p("მობილურ ვერსიაზე drawer იხსნება მხოლოდ მომხმარებლის მოქმედებით, ფონი იბლოკება scroll-ისგან, ხოლო ნავიგაციაზე გადასვლისას ის ავტომატურად იხურება. ამით თავიდან ირიდება კონტენტის დაფარვა და უზრუნველყოფილია კლავიატურით/თაჩით მართვადობა.")

# ================================================================ 8. OBD CODE
h1("8", "OBD-II ინტეგრაცია კოდში")
h2("8.1", "Web Bluetooth")
p("ბრაუზერი ადაპტერთან ურთიერთობს Web Bluetooth API-ით. `navigator.bluetooth.requestDevice()` იძახებს მოწყობილობის არჩევის დიალოგს; ფილტრაცია ხდება OBD-II სერვისის UUID-ებით. დაკავშირების შემდეგ იხსნება GATT server, მოიძებნება write/notify characteristic-ები და იწყება ორმხრივი კომუნიკაცია.")
p("Web Bluetooth მუშაობს მხოლოდ უსაფრთხო კონტექსტში: HTTPS ან localhost. Chrome/Edge-ის desktop და Android ვერსიები მხარდაჭერილია; iOS Safari ამჟამად არ იძლევა სრულ Web Bluetooth მხარდაჭერას. ამიტომ აპლიკაცია მომხმარებელს აფრთხილებს თავსებადობაზე.")

h2("8.2", "ინიციალიზაციის ბრძანებები")
p("ELM327-ის ინიციალიზაცია რამდენიმე AT ბრძანებას მოიცავს. `ATZ` აბრუნებს ადაპტერს საწყის მდგომარეობაში; `ATE0` თიშავს echo-ს; `ATL0` — line feed-ს; `ATS0` — spaces-ს; `ATH0` — headers-ს; `ATSP0` — ირჩევს ავტომატურ პროტოკოლს. ბოლოს `0100` ითხოვს მხარდაჭერილ PID-ებს და ადასტურებს, რომ ECU პასუხობს.")
code_block([
    "const reset = await this.send('ATZ', RESET_TIMEOUT_MS);",
    "for (const cmd of ['ATE0','ATL0','ATS0','ATH0','ATSP0']) {",
    "  await this.send(cmd);",
    "}",
    "const supported = await this.send('0100', VEHICLE_TIMEOUT_MS);",
    "this.vehicleResponding.set(supported.includes('4100'));",
])
p("თუ `ATZ`-ის პასუხი არ შეიცავს `ELM`-ს, ადაპტერი არ არის ELM327-ის თავსებადი და კავშირი წყდება გასაგები შეტყობინებით. ეს იცავს მომხმარებელს გაუგებარი timeout-ებისგან.")

h2("8.3", "PID-ების კითხვა")
p("PID-ების კითხვა ხდება `send(pid)` მეთოდით, სადაც pid არის ოთხნიშნა hex კოდი (`010C`, `010D`, `0105`, `0142`). პასუხი მოდის hex ტექსტის სახით; `parsePidBytes` ამოიღებს payload-ს, `decodePid` კი იძლევა ფიზიკურ მნიშვნელობას. LiveData კომპონენტი ყოველ 500 ms-ში იმეორებს კითხვას და აახლებს სიგნალებს.")
code_block([
    "export function decodePid(raw: string, definition: PidDefinition) {",
    "  const bytes = parsePidBytes(raw, definition.pid);",
    "  return bytes?.length ? definition.decode(bytes) : null;",
    "}",
])

h2("8.4", "DTC სკანირება")
p("DtcScanService აგზავნის `0101`-ს readiness მონიტორებისთვის, შემდეგ `03`, `07` და `0A` რეჟიმებს. თითოეული პასუხი გადამუშავდება `parseDtcResponse`-ით, რომელიც ითვალისწინებს CAN frame-ებს, count byte-სა და padding-ს. კოდები დედუპლიკაციით ინახება `DtcRecord`-ებში, ხოლო VIN მიიღება `0902`-ით.")
code_block([
    "const isCan = this.adapter.isCan();",
    "const results: DtcResults = { '03': [], '07': [], '0A': [] };",
    "for (const mode of Object.keys(results) as DtcMode[]) {",
    "  const raw = await this.adapter.send(mode, SCAN_TIMEOUT_MS);",
    "  results[mode] = await this.describe(",
    "    parseDtcResponse(raw, mode, isCan)",
    "  );",
    "}",
    "await this.saveScan(startedAt, results);",
])

h2("8.5", "პასუხის ფორმატი და პარსერი")
p("ELM327 აბრუნებს ტექსტურ hex პასუხს. რეჟიმ 03-ის პასუხის პირველი ბაიტი არის `43` (0x40 + 0x03), 07-ისა — `47`, 0A-ისა — `4A`. DTC შედგება ორი ბაიტისგან; მაგალითად `01 33` არის P0133. CAN-ის შემთხვევაში პასუხს აქვს count byte და შეიძლება რამდენიმე frame-ად იყოს გაყოფილი; პარსერი frame-ებს აერთიანებს.")
table(
    ["მოთხოვნა", "პასუხის პრეფიქსი", "მნიშვნელობა"],
    [
        ("03", "43", "Stored DTC"),
        ("07", "47", "Pending DTC"),
        ("0A", "4A", "Permanent DTC"),
        ("0902", "49 02", "VIN"),
        ("0100", "41 00", "Supported PIDs"),
    ],
    [3.0, 4.5, 8.3],
)
p("პარსერი უგულებელყოფს `0000` padding-ს, ამუშავებს `NO DATA`-ს და ამოიღებს მხოლოდ ვალიდურ hex სტრიქონებს. კოდის გაშიფვრა ხდება `decodeDtc`-ით: პირველი nibble განსაზღვრავს P/C/B/U სისტემას, ხოლო დანარჩენი — კონკრეტულ კოდს.")
code_block([
    "export function decodeDtc(hex: string): string {",
    "  const first = parseInt(hex[0], 16);",
    "  return `${'PCBU'[first >> 2]}${first & 3}${hex.slice(1)}`;",
    "}",
])

h2("8.6", "კოდების გასუფთავება")
p("`clearCodes()` აგზავნის `04`-ს და ამოწმებს, რომ პასუხი შეიცავს `44`-ს. წარმატებისას ხდება ხელახალი სკანირება, რათა UI-ში აისახოს განახლებული მდგომარეობა. ოპერაცია საშიშია, რადგან შლის freeze frame-სა და readiness მონიტორებს; ამიტომ UI ითხოვს დადასტურებას და ცალკე აჩვენებს გაფრთხილებას.")
callout("მნიშვნელოვანი", "კოდების გასუფთავება არ არის ხარვეზის შეკეთება. თუ ხარვეზი გრძელდება, კოდი დროთა განმავლობაში დაბრუნდება. OBD360 მომხმარებელს ამის შესახებ აფრთხილებს.")

# ================================================================ 9. DTC CATALOG
h1("9", "DTC კატალოგი")
h2("9.1", "მოცულობა და წყარო")
p("კატალოგი შეიცავს 13 629 DTC ჩანაწერს. თითოეულ ჩანაწერს აქვს კოდი, ქართული და ინგლისური სახელი, აღწერა, სისტემა, სირთულე, სავარაუდო ღირებულება და სამუშაო საათები. კატალოგი გამოიყენება სკანირების შედეგების გასაგებად, AI prompt-ის გასამდიდრებლად და საძიებო ინტერფეისისთვის.")
table(
    ["ველი", "აღწერა"],
    [
        ("Code", "P0300, P0420, P0A80..."),
        ("TitleKa / TitleEn", "მოკლე სახელი ორ ენაზე"),
        ("Description", "ტექნიკური ახსნა"),
        ("System", "P/B/C/U კატეგორია"),
        ("Severity", "Low / Medium / High"),
        ("EstimatedCost", "სავარაუდო ღირებულება"),
        ("LaborHours", "სამუშაო საათები"),
    ],
    [4.5, 11.3],
)

h2("9.2", "კატალოგის გამოყენება")
p("სკანირების შემდეგ `DtcScanService` თითოეულ კოდს ეძებს კატალოგში. თუ კოდი მოიძებნა, UI აჩვენებს სახელს, აღწერას, სირთულესა და ღირებულებას; თუ არა — ნაჩვენებია მხოლოდ კოდი და ზოგადი რეკომენდაცია. DTC catalog API მხარდაჭერილია ძებნას, გვერდიანობასა და კონკრეტული კოდის დეტალებს.")
figure(SLIDE_ASSETS / "garage.png", "ნახ. 9. ავტომობილის პროფილი — სკანირება იწყება არჩეული მანქანიდან.", 13.5)

# ================================================================ 10. AI
h1("10", "AI ასისტენტი — n8n და Gemini")
h2("10.1", "ნაკადი")
p("AI ასისტენტი არ არის პირდაპირ Angular-იდან Gemini-ზე დაკავშირებული. მოთხოვნა მიდის API-ზე (`POST /api/v1/ai/ask`), API ამდიდრებს მას მანქანის, ბოლო სკანირებისა და DTC კოდების კონტექსტით და გადასცემს n8n workflow-ს. n8n იძახებს Google Gemini-ს, იღებს პასუხს და აბრუნებს API-ს. საუბარი ინახება `AiConversation`/`AiMessage` ჩანაწერებში.")
p("ასეთი გამიჯვნა იძლევა უპირატესობას: API key არ ვრცელდება კლიენტში, prompt-ის ლოგიკა ცენტრალიზებულია, ხოლო workflow-ის შეცვლა backend-ის განახლების გარეშე შეიძლება. კრიტიკული კოდებისთვის n8n-ს შეუძლია Telegram alert-ის გაგზავნა.")

h2("10.2", "Prompt და კონტექსტი")
p("Prompt Builder აერთიანებს მომხმარებლის კითხვას, ავტომობილის მონაცემებს (მწარმოებელი, მოდელი, წელი), ბოლო სკანირების კოდებს და კატალოგის აღწერებს. პასუხი ითხოვს ქართულ ენაზე, გასაგებ ტერმინოლოგიას, შესაძლო მიზეზებს, რეკომენდაციასა და გაფრთხილებას, რომ დიაგნოზი საბოლოო არ არის.")
table(
    ["ელემენტი", "დანიშნულება"],
    [
        ("Vehicle context", "მწარმოებელი/მოდელი/წელი"),
        ("Scan context", "ბოლო DTC კოდები"),
        ("Catalog context", "კოდის აღწერა და სირთულე"),
        ("Conversation", "წინა შეტყობინებები"),
        ("Safety instruction", "არ შეცვალოს ECU, არ მისცეს საბოლოო დიაგნოზი"),
    ],
    [5.0, 10.8],
)

h2("10.3", "კონფიგურაცია")
p("n8n მუშაობს ლოკალურად `http://localhost:5678`-ზე. API-ის `appsettings.Development.json` შეიცავს n8n webhook-ის მისამართს. Gemini-ის API key ინახება n8n-ის credential-ში და არა Git-ში. თუ n8n გამორთულია, AI endpoint აბრუნებს გასაგებ შეცდომას; აპლიკაციის დანარჩენი ნაწილი მუშაობს.")

# ================================================================ 11. REMINDERS
h1("11", "შეხსენებები და ელფოსტა")
h2("11.1", "ფონური სერვისი")
p("ReminderNotificationService მუშაობს როგორც `BackgroundService`. ის იწყებს შემოწმებას API-ის გაშვებისას და შემდეგ ყოველ 6 საათში. სერვისი პოულობს იმ შეხსენებებს, რომელთა `DueAtDate <= today` და სტატუსი არ არის დასრულებული, აჯგუფებს მათ მომხმარებლის მიხედვით და უგზავნის ერთ digest მეილს დღეში.")
p("დუბლიკატის თავიდან ასაცილებლად გამოიყენება `NotificationLogs`: თუ მომხმარებელზე დღეს უკვე გაგზავნილია `MaintenanceReminder` + `Email` ლოგი `Sent` სტატუსით, მეორე მეილი არ იგზავნება. წარუმატებელი გაგზავნა ინახება `Failed` სტატუსით და შესაძლებელია ხელახალი ცდა.")

h2("11.2", "SMTP კონფიგურაცია")
table(
    ["პარამეტრი", "მნიშვნელობა"],
    [
        ("Smtp:Host", "smtp.gmail.com"),
        ("Smtp:Port", "587"),
        ("Smtp:UserName", "გამგზავნის ელფოსტა"),
        ("Smtp:Password", "Gmail App Password (user-secrets)"),
        ("Reminders:Enabled", "true"),
        ("Reminders:CheckIntervalMinutes", "360"),
    ],
    [6.0, 9.8],
)
p("SMTP პაროლი ინახება .NET user-secrets-ში და არასოდეს ხვდება Git-ში. თუ SMTP არ არის კონფიგურირებული, Development გარემოში კოდი იბეჭდება ლოგში, ხოლო პაროლის აღდგენის კოდი ბრუნდება `devCode`-ში. ეს აადგილებს ლოკალურ ტესტირებას.")

# ================================================================ 12. SECURITY
h1("12", "უსაფრთხოება")
h2("12.1", "ავტორიზაცია და სესიები")
p("პაროლები ინახება ASP.NET Identity-ის hash-ით. access token არის ხელმოწერილი JWT 15 წუთის ვადით; refresh token — 30 დღის, HttpOnly, Secure და SameSite=Strict cookie. refresh token ბაზაში ინახება მხოლოდ SHA-256 hash-ის სახით, რაც ბაზის გაჟონვის შემთხვევაში ხელს უშლის token-ის პირდაპირ გამოყენებას.")
table(
    ["კონტროლი", "რეალიზაცია"],
    [
        ("Password hashing", "ASP.NET Identity"),
        ("Access token", "JWT, 15 წუთი, HS256"),
        ("Refresh token", "30 დღე, HttpOnly, Secure, SameSite=Strict"),
        ("Rotation", "ყოველი refresh-ისას ძველი უქმდება"),
        ("Logout/reset", "ყველა refresh session იუქმება"),
        ("Roles", "User/Admin, [Authorize]"),
        ("CORS", "მხოლოდ http://localhost:4200"),
        ("Secrets", "user-secrets, appsettings მხოლოდ placeholder"),
    ],
    [5.0, 10.8],
)

h2("12.2", "როლები და ადმინის დაცვა")
p("Admin API დაცულია `[Authorize(Roles = \"Admin\")]`-ით. ადმინს არ შეუძლია საკუთარი ანგარიშის წაშლა ან საკუთარი Admin როლის მოხსნა; ასევე დაბლოკილია ბოლო Admin-ის წაშლა/დაქვეითება. ეს იცავს სისტემას სრული ადმინისტრირების დაკარგვისგან.")
code_block([
    "[ApiController]",
    "[Authorize(Roles = \"Admin\")]",
    "[Route(\"api/v1/admin\")]",
    "public class AdminController : ControllerBase { ... }",
])

h2("12.3", "პაროლის აღდგენა")
p("6-ციფრიანი კოდი ინახება ფაილურ საცავში, მოქმედებს 10 წუთი და აქვს 5 მცდელობა. კოდი ერთჯერადია და წარმატებული reset-ის შემდეგ იშლება. პაროლის შეცვლისას ან reset-ისას ყველა refresh session უქმდება, რაც აიძულებს სხვა მოწყობილობებს ხელახლა ავტორიზაციას.")

h2("12.4", "შეზღუდვები")
for item in [
    "JWT არ ამოწმებს security stamp-ს; პაროლის შეცვლის შემდეგ ძველი access token 15 წუთამდე მოქმედებს.",
    "არ არის rate limiting/brute-force დაცვა login-სა და reset-ზე.",
    "არ არის email confirmation.",
    "Development გარემოში reset კოდი შეიძლება დაბრუნდეს პასუხში (`devCode`) — პროდუქციაში ეს გამორთულია.",
]:
    bullet(item)

# ================================================================ 13. TESTS
h1("13", "ტესტირება და ხარისხი")
h2("13.1", "ავტომატური ტესტები")
table(
    ["დონე", "რაოდენობა", "ინსტრუმენტი", "ფარგლები"],
    [
        ("Backend", "29", "xUnit", "auth, vehicles, reminders, scans, DTC, AI, admin"),
        ("Frontend", "19", "Vitest", "services, guards, decoding, components"),
        ("სულ", "48", "—", "—"),
    ],
    [3.0, 3.0, 4.0, 6.0],
)
p("Backend ტესტები მოიცავს ავტორიზაციის ნაკადებს, CRUD ოპერაციებს, ownership შემოწმებებს, DTC კატალოგის ძებნასა და AI endpoint-ის ქცევას. Frontend ტესტები ამოწმებს OBD decoder-ს, auth service-ს, guards-სა და ძირითად კომპონენტებს. ტესტების გაშვება:")
code_block([
    "cd backend",
    "dotnet test",
    "",
    "cd frontend",
    "npm test -- --run",
])

h2("13.2", "ხელით ტესტირება")
for item in [
    "რეგისტრაცია, login, logout, refresh და პაროლის აღდგენა.",
    "მანქანის დამატება/რედაქტირება/წაშლა და ownership შემოწმება.",
    "DTC სკანირება, კოდების კატალოგში მოძიება და ისტორიაში შენახვა.",
    "ადმინის users/scans/role/delete სცენარები; საკუთარი თავის წაშლის ბლოკირება.",
    "რესპონსიულობა 390×844, 768×1024 და 1440×900 ეკრანებზე.",
    "SMTP რემაინდერის გაგზავნა და NotificationLogs სტატუსი.",
]:
    bullet(item)

h2("13.3", "ხარისხის შეფასება")
p("კოდი ორგანიზებულია ფენებად და იყენებს ტიპიზებულ კონტრაქტებს. ძლიერი მხარეებია ავტორიზაციის სქემა, სუფთა Angular სტრუქტურა, Signals, ტესტები და C4 დოკუმენტაცია. სუსტი მხარეებია: არასრული rate limiting, ზოგიერთი დიდი კომპონენტი, Swagger-ის არასრული აღწერები და Docker კონფიგურაციის არატესტირება. ეს პუნქტები მოცემულია მომავალი სამუშაოს განყოფილებაში.")

# ================================================================ 14. RUN
h1("14", "გაშვება და ინსტალაცია")
h2("14.1", "წინაპირობები")
for item in [
    ".NET 10 SDK",
    "Node.js 20+ და npm",
    "SQL Server 2019+ ან LocalDB",
    "Chrome ან Edge (Web Bluetooth)",
    "სურვილისამებრ: n8n, Docker Desktop",
]:
    bullet(item)

h2("14.2", "ბაზა და კონფიგურაცია")
p("Connection string იწერება `backend/Obd360.Api/appsettings.Development.json`-ში ან user-secrets-ში. JWT signing key, SMTP პაროლი და n8n URL ასევე user-secrets-ში ინახება. აპლიკაციის გაშვებისას API ავტომატურად ცდილობს მიგრაციების გამოყენებას და DTC კატალოგის ინიციალიზაციას.")
code_block([
    "cd backend/Obd360.Api",
    "dotnet user-secrets set \"Jwt:SigningKey\" \"<long-random-key>\"",
    "dotnet user-secrets set \"Smtp:Password\" \"<gmail-app-password>\"",
    "dotnet run",
])
p("Frontend:")
code_block([
    "cd frontend",
    "npm install",
    "npm start",
])
p("შემდეგ გახსენი `http://localhost:4200`. API მუშაობს `http://localhost:5269`-ზე, Swagger — `/swagger`.")

h2("14.3", "Docker")
p("პროექტში არის `docker-compose.yml`, `backend/Obd360.Api/Dockerfile`, `frontend/Dockerfile` და `frontend/nginx.conf`. Docker კონფიგურაცია განკუთვნილია API-ს, frontend-ისა და SQL Server-ის ერთ კონტეინერებად გასაშვებად, მაგრამ ამ გარემოში ის არ არის გატესტილი Docker Desktop-ის არარსებობის გამო. ამიტომ Docker ნაწილი მოითხოვს დამატებით ვალიდაციას.")

# ================================================================ 15. USER GUIDE
h1("15", "მომხმარებლის გზამკვლევი")
h2("15.1", "რეგისტრაცია და შესვლა")
p("გახსენი `/register`, შეიყვანე სახელი, ელფოსტა და პაროლი (მინიმუმ 8 სიმბოლო). რეგისტრაციის შემდეგ ავტომატურად ხდება login. პაროლის დავიწყებისას გამოიყენე `/forgot-password`: შეიყვანე ელფოსტა, მიიღე 6-ციფრიანი კოდი და დააყენე ახალი პაროლი. კოდი მოქმედებს 10 წუთი.")

h2("15.2", "მანქანის დამატება")
p("გადადი Garage-ში და დაამატე ავტომობილი: მწარმოებელი, მოდელი, წელი, VIN და სანომრე ნიშანი. VIN-ის შეყვანა სავალდებულო არ არის, მაგრამ ის ეხმარება სკანირების იდენტიფიკაციას. მანქანის ბარათზე შეგიძლია რედაქტირება ან წაშლა.")

h2("15.3", "ადაპტერთან დაკავშირება")
p("გახსენი Bluetooth Adapter, ჩართე OBD-II ადაპტერი და დააჭირე დაკავშირებას. ბრაუზერი მოგთხოვს მოწყობილობის არჩევას. აირჩიე ELM327-ის ტიპის ადაპტერი. წარმატებული კავშირის შემდეგ გამოჩნდება პროტოკოლი და ავტომობილის პასუხი. თუ ადაპტერი არ ჩანს, შეამოწმე Bluetooth, ადაპტერის კვება და ბრაუზერის თავსებადობა.")

h2("15.4", "სკანირება და კოდების გაგება")
p("გახსენი DTC Scanner და დააჭირე სკანირებას. აპლიკაცია კითხულობს stored, pending და permanent კოდებს. შედეგი დაჯგუფებულია სისტემის მიხედვით; თითო კოდზე ჩანს კატალოგის ახსნა, სირთულე და სავარაუდო ღირებულება. კოდების გასუფთავებამდე წაიკითხე გაფრთხილება: ეს არ არის შეკეთება და შეიძლება readiness მონიტორები განულდეს.")

h2("15.5", "Live Data, შეხსენებები და AI")
p("Live Data აჩვენებს RPM-ს, სიჩქარეს, გამაგრილებლის ტემპერატურასა და ძაბვას 500 ms განახლებით. Reminders-ში შექმენი ტექნიკური შეხსენება თარიღით; ვადის მოახლოებისას სისტემა ელფოსტით გამოგიგზავნის digest-ს. AI Assistant-ში დასვი კითხვა ქართულად — პასუხი ეფუძნება შენი მანქანის ბოლო სკანირებას.")

h2("15.6", "ადმინის პანელი")
p("Admin როლის მქონე მომხმარებელი ხედავს Administration → Admin ბმულს. პანელი აჩვენებს სტატისტიკას, მომხმარებლებს, როლებსა და სკანირებებს. როლის შეცვლა და მომხმარებლის წაშლა ხდება დადასტურებით; საკუთარი თავის ან ბოლო Admin-ის წაშლა დაბლოკილია. როლის ცვლილების შემდეგ მომხმარებელმა თავიდან უნდა გაიაროს login, რადგან JWT-ში ძველი როლია.")

# ================================================================ 16. LIMITS
h1("16", "შეზღუდვები და მომავალი სამუშაო")
h2("16.1", "მიმდინარე შეზღუდვები")
for item in [
    "რეალური OBD-II აპარატურის ტესტირება დამოკიდებულია კონკრეტულ ადაპტერსა და მანქანაზე.",
    "Web Bluetooth არ არის სრულად მხარდაჭერილი iOS Safari-ში.",
    "რემაინდერები მხოლოდ თარიღით მუშაობს; გარბენით რემაინდერი არ არის.",
    "AI საჭიროებს გამართულ n8n-სა და Gemini credential-ს.",
    "Docker კონფიგურაცია არ არის გატესტილი ამ გარემოში.",
    "Swagger-ის XML აღწერები ყველა controller-ს არ ფარავს.",
    "არ არის rate limiting და email confirmation.",
]:
    bullet(item)

h2("16.2", "მომავალი სამუშაო")
for item in [
    "გარბენით რემაინდერები და ოდომეტრის ისტორია.",
    "PDF რეპორტების გენერაცია და ექსპორტი.",
    "DTC კატალოგის ადმინისტრირება (CRUD).",
    "მობილური აპლიკაცია ან PWA iOS-ისთვის.",
    "GitHub Actions CI/CD და Docker-ის ავტომატური ტესტირება.",
    "Rate limiting, email confirmation და security stamp-ის ვალიდაცია.",
    "მეტი OBD-II ადაპტერის პროფილი და მწარმოებლის სპეციფიკური PID-ები.",
]:
    bullet(item)

# ================================================================ 17. CONCLUSION
h1("17", "დასკვნა")
p("პროექტის შედეგად შეიქმნა სრულფასოვანი ვებ-პლატფორმა, რომელიც აერთიანებს OBD-II დიაგნოსტიკას, მონაცემთა ბაზას, ავტორიზაციას, AI ასისტენტს, შეხსენებებსა და ადმინისტრირებას. სისტემა აჩვენებს, რომ ტექნიკურად რთული OBD-II მონაცემები შეიძლება იყოს მძღოლისთვის გასაგები და სასარგებლო, თუ მათ სწორად გავაერთიანებთ კატალოგს, ისტორიასა და AI ახსნას.")
p("მიღწეულია 32 REST endpoint, 15 მონაცემთა მოდელი, 13 629 DTC ჩანაწერი, 29 backend და 19 frontend ტესტი. C4 დიაგრამები, Swagger, ლოგირება და დოკუმენტაცია ქმნის საფუძველს, რომ პროექტი გაფართოვდეს როგორც სასწავლო, ისე პრაქტიკული პროდუქტის მიმართულებით. ძირითადი შემდეგი ნაბიჯებია რეალურ აპარატურაზე ტესტირება, გარბენით რემაინდერები, რეპორტები და CI/CD.")

# ================================================================ REFERENCES
doc.add_page_break()
doc.add_paragraph(style="Heading 1").add_run("ბიბლიოგრაფია").font.name = "Sylfaen"
references = [
    "ISO 15765-4: Road vehicles — Diagnostic communication over Controller Area Network (CAN).",
    "SAE J1979: E/E Diagnostic Test Modes.",
    "SAE J1962: Diagnostic Connector.",
    "ISO 14230-4: Diagnostic communication over K-Line.",
    "U.S. Environmental Protection Agency. OBD-II regulations and technical information.",
    "Angular. Official documentation. https://angular.dev",
    "Microsoft. ASP.NET Core documentation. https://learn.microsoft.com/aspnet/core",
    "Microsoft. Entity Framework Core documentation. https://learn.microsoft.com/ef/core",
    "n8n. Documentation. https://docs.n8n.io",
    "Google. Gemini API documentation. https://ai.google.dev",
    "Jones, M., Bradley, J., Sakimura, N. JSON Web Token (JWT), RFC 7519, 2015.",
    "OWASP. Application Security Verification Standard.",
]
for index, reference in enumerate(references, start=1):
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(4)
    paragraph.paragraph_format.left_indent = Cm(0.8)
    paragraph.paragraph_format.first_line_indent = Cm(-0.8)
    run = paragraph.add_run(f"[{index}]  {reference}")
    run.font.name = "Sylfaen"
    run.font.size = Pt(9.5)
    run.font.color.rgb = INK

# ================================================================ APPENDIX A
h1("A", "დანართი A — REST API")
p("ცხრილში მოცემულია ყველა ძირითადი endpoint. ავტორიზაცია საჭიროა ყველგან, გარდა auth-ის საჯარო endpoint-ებისა და DTC კატალოგის ნაწილისა.")
endpoints = [
    ("POST", "/api/v1/auth/register", "რეგისტრაცია"),
    ("POST", "/api/v1/auth/login", "ავტორიზაცია"),
    ("POST", "/api/v1/auth/refresh", "token-ის განახლება"),
    ("POST", "/api/v1/auth/logout", "გასვლა"),
    ("POST", "/api/v1/auth/forgot-password", "reset კოდის გაგზავნა"),
    ("POST", "/api/v1/auth/reset-password", "ახალი პაროლი"),
    ("POST", "/api/v1/auth/change-password", "პაროლის შეცვლა"),
    ("GET", "/api/v1/preferences", "პარამეტრები"),
    ("PUT", "/api/v1/preferences", "პარამეტრების განახლება"),
    ("GET", "/api/v1/vehicles", "მანქანების სია"),
    ("GET", "/api/v1/vehicles/{id}", "მანქანის დეტალები"),
    ("POST", "/api/v1/vehicles", "მანქანის დამატება"),
    ("PUT", "/api/v1/vehicles/{id}", "მანქანის რედაქტირება"),
    ("DELETE", "/api/v1/vehicles/{id}", "მანქანის წაშლა"),
    ("GET", "/api/v1/reminders", "შეხსენებები"),
    ("POST", "/api/v1/reminders", "შეხსენების დამატება"),
    ("PUT", "/api/v1/reminders/{id}", "რედაქტირება"),
    ("DELETE", "/api/v1/reminders/{id}", "წაშლა"),
    ("POST", "/api/v1/reminders/{id}/complete", "დასრულება"),
    ("GET", "/api/v1/scans", "სკანირების ისტორია"),
    ("POST", "/api/v1/scans", "სკანირების შენახვა"),
    ("GET", "/api/v1/dtc-catalog", "კატალოგი"),
    ("GET", "/api/v1/dtc-catalog/{code}", "კოდის დეტალები"),
    ("GET", "/api/v1/ai/status", "AI სტატუსი"),
    ("POST", "/api/v1/ai/latest-scan-report", "ბოლო სკანირების რეპორტი"),
    ("POST", "/api/v1/ai/ask", "AI კითხვა"),
    ("GET", "/api/v1/ai/conversation", "საუბრის ისტორია"),
    ("GET", "/api/v1/admin/overview", "ადმინის სტატისტიკა"),
    ("GET", "/api/v1/admin/users", "მომხმარებლები"),
    ("DELETE", "/api/v1/admin/users/{id}", "მომხმარებლის წაშლა"),
    ("POST", "/api/v1/admin/users/{id}/toggle-role", "როლის გადართვა"),
    ("GET", "/api/v1/admin/scans", "ყველა სკანირება"),
]
table(["მეთოდი", "მისამართი", "აღწერა"], endpoints, [2.2, 8.8, 4.8], font_size=8.2)

# ================================================================ APPENDIX B
h1("B", "დანართი B — პროექტის სტრუქტურა")
code_block([
    "backend/",
    "  Obd360.Api/            Web API, controllers, n8n, services",
    "  Obd360.Core/           entities, enums, interfaces",
    "  Obd360.Infrastructure/ DbContext, migrations, Identity, SMTP",
    "  Obd360.Tests/          xUnit tests",
    "frontend/",
    "  src/app/core/          services, guards, interceptors",
    "  src/app/features/      dashboard, garage, reminders, admin...",
    "  src/app/layout/        main-layout, responsive drawer",
    "  src/app/shared/        UI helpers",
    "database/",
    "  schema.sql             SQL schema",
    "  seed.sql               initial data",
    "docs/",
    "  c4/                    C4 PDF",
    "  slides/                presentation",
    "n8n/                     workflow and setup",
])

doc.save(OUT)
print(f"saved {OUT}")
