from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

BASE = Path(r"C:\Users\zukal\OneDrive\Desktop\OBD2 WEB\docs\slides")
ASSETS = BASE / "assets"
OUT = BASE / "OBD360-Web-Presentation.pptx"

BG = RGBColor(0xF7, 0xF5, 0xF0)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
INK = RGBColor(0x20, 0x25, 0x1F)
MUTED = RGBColor(0x72, 0x77, 0x6E)
SAGE = RGBColor(0x3F, 0x5D, 0x4E)
SAGE_SOFT = RGBColor(0xE9, 0xEF, 0xE9)
LINE = RGBColor(0xE4, 0xE0, 0xD7)
AMBER = RGBColor(0xB9, 0x86, 0x3F)
DANGER = RGBColor(0xB3, 0x56, 0x4D)
CODE_BG = RGBColor(0x1F, 0x29, 0x24)
CODE_FG = RGBColor(0xE8, 0xEF, 0xE9)
BLUE_SOFT = RGBColor(0xE8, 0xEE, 0xF0)

FONT = "Segoe UI"
MONO = "Consolas"


def new_deck():
    presentation = Presentation()
    presentation.slide_width = Inches(13.333)
    presentation.slide_height = Inches(7.5)
    return presentation


def add_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    background = slide.background.fill
    background.solid()
    background.fore_color.rgb = BG
    return slide


def text(slide, left, top, width, height, value, size=18, bold=False,
         color=INK, font=FONT, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         line_spacing=1.0):
    box = slide.shapes.add_textbox(left, top, width, height)
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = 0
    frame.margin_right = 0
    frame.margin_top = 0
    frame.margin_bottom = 0
    frame.vertical_anchor = anchor

    paragraph = frame.paragraphs[0]
    paragraph.alignment = align
    paragraph.line_spacing = line_spacing
    run = paragraph.add_run()
    run.text = value
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def bullets(slide, left, top, width, height, items, size=16,
            color=INK, spacing=9, bullet_color=SAGE):
    box = slide.shapes.add_textbox(left, top, width, height)
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = 0
    frame.margin_right = 0
    frame.margin_top = 0
    frame.margin_bottom = 0

    for index, item in enumerate(items):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.space_after = Pt(spacing)
        paragraph.line_spacing = 1.05
        marker = paragraph.add_run()
        marker.text = "•  "
        marker.font.name = FONT
        marker.font.size = Pt(size)
        marker.font.bold = True
        marker.font.color.rgb = bullet_color
        run = paragraph.add_run()
        run.text = item
        run.font.name = FONT
        run.font.size = Pt(size)
        run.font.color.rgb = color
    return box


def rect(slide, left, top, width, height, fill=WHITE, line=LINE,
         radius=True):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(shape_type, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line
    shape.line.width = Pt(1)
    if radius:
        shape.adjustments[0] = 0.08
    return shape


def card(slide, left, top, width, height, label, value, note,
         value_size=30, fill=WHITE):
    rect(slide, left, top, width, height, fill=fill)
    text(slide, left + Inches(0.22), top + Inches(0.15), width - Inches(0.44),
         Inches(0.24), label.upper(), 8, True, MUTED)
    text(slide, left + Inches(0.22), top + Inches(0.40), width - Inches(0.44),
         Inches(0.42), value, value_size, True, INK)
    text(slide, left + Inches(0.22), top + height - Inches(0.27),
         width - Inches(0.44), Inches(0.22), note, 9, False, MUTED)


def header(slide, kicker, title, subtitle=None, number=None):
    text(slide, Inches(0.6), Inches(0.38), Inches(10.8), Inches(0.25),
         kicker.upper(), 9, True, SAGE)
    text(slide, Inches(0.6), Inches(0.67), Inches(12.1), Inches(0.62),
         title, 30, True, INK)
    if subtitle:
        text(slide, Inches(0.6), Inches(1.27), Inches(11.7), Inches(0.36),
             subtitle, 12, False, MUTED)
    if number is not None:
        text(slide, Inches(12.2), Inches(0.38), Inches(0.6), Inches(0.3),
             f"{number:02d}", 9, True, MUTED, align=PP_ALIGN.RIGHT)


def footer(slide, label="OBD360 Web  ·  2026"):
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(7.02),
                                  Inches(12.13), Inches(0.01))
    line.fill.solid()
    line.fill.fore_color.rgb = LINE
    line.line.fill.background()
    text(slide, Inches(0.6), Inches(7.1), Inches(8.0), Inches(0.2), label, 8, False, MUTED)
    text(slide, Inches(11.8), Inches(7.1), Inches(0.9), Inches(0.2), "OBD360", 8, True, SAGE,
         align=PP_ALIGN.RIGHT)


def code_block(slide, left, top, width, height, lines, size=11):
    rect(slide, left, top, width, height, CODE_BG, CODE_BG)
    box = slide.shapes.add_textbox(left + Inches(0.18), top + Inches(0.13),
                                   width - Inches(0.3), height - Inches(0.22))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = False
    frame.margin_left = 0
    frame.margin_right = 0
    frame.margin_top = 0
    frame.margin_bottom = 0
    for index, line in enumerate(lines):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.space_after = Pt(2)
        run = paragraph.add_run()
        run.text = line
        run.font.name = MONO
        run.font.size = Pt(size)
        run.font.color.rgb = CODE_FG


def add_picture_fit(slide, path, left, top, width, height):
    with Image.open(path) as image:
        image_width, image_height = image.size
    scale = min(width / image_width, height / image_height)
    new_width = int(image_width * scale)
    new_height = int(image_height * scale)
    picture_left = left + (width - new_width) // 2
    picture_top = top + (height - new_height) // 2
    slide.shapes.add_picture(str(path), picture_left, picture_top, new_width, new_height)


def arrow(slide, left, top, width, height, down=False):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.DOWN_ARROW if down else MSO_SHAPE.RIGHT_ARROW,
        left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = SAGE
    shape.line.fill.background()


prs = new_deck()

# ---------------------------------------------------------------- 1. TITLE
slide = add_slide(prs)
panel = rect(slide, Inches(8.75), Inches(0.6), Inches(3.95), Inches(6.3), SAGE, SAGE)
text(slide, Inches(9.15), Inches(1.0), Inches(3.2), Inches(0.35),
     "OBD-II  ·  16 PIN", 10, True, SAGE_SOFT)
text(slide, Inches(9.15), Inches(1.45), Inches(3.2), Inches(1.2),
     "OBD\n360", 46, True, WHITE, line_spacing=0.92)
text(slide, Inches(9.15), Inches(3.55), Inches(3.0), Inches(0.9),
     "ავტომობილის\nდიაგნოსტიკის\nპლატფორმა", 16, True, WHITE, line_spacing=1.25)
text(slide, Inches(9.15), Inches(5.75), Inches(3.1), Inches(0.5),
     "Web Bluetooth  ·  Angular  ·  .NET  ·  n8n + Gemini", 8, False, SAGE_SOFT)

text(slide, Inches(0.65), Inches(0.9), Inches(7.7), Inches(0.3),
     "სადიპლომო პროექტი", 11, True, SAGE)
text(slide, Inches(0.65), Inches(1.55), Inches(8.0), Inches(1.3),
     "OBD360 Web", 54, True, INK)
text(slide, Inches(0.65), Inches(2.85), Inches(7.5), Inches(0.8),
     "მანქანის დიაგნოსტიკა მარტივ ენაზე", 22, False, SAGE)
text(slide, Inches(0.65), Inches(3.85), Inches(7.2), Inches(1.1),
     "OBD-II ადაპტერი → ECU → DTC კოდები → გასაგები ახსნა", 14, False, MUTED)
text(slide, Inches(0.65), Inches(6.2), Inches(7.0), Inches(0.3),
     "ზურაბ ლაზაშვილი  ·  2026", 11, True, INK)

# ---------------------------------------------------------------- 2. PROBLEM
slide = add_slide(prs)
header(slide, "პრობლემა", "რატომ OBD360?", "დიაგნოსტიკა დღეს ძალიან ტექნიკურია მძღოლისთვის.", 2)
bullets(slide, Inches(0.6), Inches(1.8), Inches(6.5), Inches(3.4), [
    "მანქანა აჩვენებს მხოლოდ კოდს — P0300, P0420, P0A80.",
    "მძღოლმა არ იცის, რას ნიშნავს, რამდენად სერიოზულია და რა ღირს.",
    "სკანირებები, გარბენი და ტექნიკური მომსახურება იფანტება.",
], 18)

rect(slide, Inches(7.6), Inches(1.8), Inches(5.1), Inches(3.65), WHITE)
text(slide, Inches(7.9), Inches(2.05), Inches(4.5), Inches(0.3),
     "მაგალითი", 9, True, SAGE)
text(slide, Inches(7.9), Inches(2.45), Inches(4.5), Inches(0.7), "P0A80", 36, True, INK, font=MONO)
text(slide, Inches(7.9), Inches(3.25), Inches(4.5), Inches(0.5),
     "ჰიბრიდული ბატარეის შეცვლა", 16, True, INK)
text(slide, Inches(7.9), Inches(3.85), Inches(4.5), Inches(1.1),
     "რას ნიშნავს? რამდენი ღირს? შეიძლება თუ არა თავად?\nOBD360 ამ კითხვებს პასუხობს.", 11, False, MUTED)

text(slide, Inches(0.6), Inches(5.75), Inches(12.1), Inches(0.55),
     "13,629 DTC კოდი   ·   15 მონაცემთა მოდელი   ·   32 REST endpoint", 13, True, SAGE)
footer(slide)

# ---------------------------------------------------------------- 3. OBD-II
slide = add_slide(prs)
header(slide, "სტანდარტი", "OBD-II: მანქანის დიაგნოსტიკის ენა",
       "1996 წლიდან — ერთი სტანდარტული პორტი და პროტოკოლი.", 3)

connector = rect(slide, Inches(0.7), Inches(1.95), Inches(3.9), Inches(2.65),
                 RGBColor(0x2D, 0x35, 0x30), RGBColor(0x2D, 0x35, 0x30))
text(slide, Inches(1.0), Inches(2.15), Inches(3.3), Inches(0.35),
     "OBD-II  16-PIN", 12, True, WHITE)
for row in range(2):
    for column in range(8):
        pin = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                     Inches(1.12 + column * 0.39),
                                     Inches(2.85 + row * 0.7),
                                     Inches(0.16), Inches(0.16))
        pin.fill.solid()
        pin.fill.fore_color.rgb = SAGE_SOFT
        pin.line.fill.background()
text(slide, Inches(1.0), Inches(4.15), Inches(3.3), Inches(0.25),
     "4/5 GND  ·  6 CAN-H  ·  14 CAN-L  ·  16 +12V", 8, False, SAGE_SOFT)

card(slide, Inches(5.0), Inches(1.95), Inches(2.35), Inches(1.55),
     "16 PIN", "პორტი", "სტანდარტული 16-pin პორტი", 22)
card(slide, Inches(7.55), Inches(1.95), Inches(2.35), Inches(1.55),
     "PID", "Live", "ბრუნი · სიჩქარე · ტემპ.", 22)
card(slide, Inches(10.1), Inches(1.95), Inches(2.35), Inches(1.55),
     "DTC", "Errors", "P/B/C/U კოდები", 22)

bullets(slide, Inches(5.0), Inches(3.9), Inches(7.4), Inches(2.0), [
    "CAN 500 kbps — თანამედროვე მანქანების ძირითადი პროტოკოლი.",
    "K-line / L-line — ძველი მოდელებისთვის.",
    "ELM327 ადაპტერი AT-ბრძანებებით ელაპარაკება ECU-ს.",
], 13)
footer(slide)

# ---------------------------------------------------------------- 4. CONNECTION
slide = add_slide(prs)
header(slide, "კავშირი", "როგორ მუშაობს კავშირი მანქანასთან",
       "ECU → OBD-II პორტი → BLE ადაპტერი → ბრაუზერი → OBD360.", 4)

boxes = [
    ("ECU", "ძრავის მართვის ბლოკი", SAGE, WHITE),
    ("OBD-II", "16-pin პორტი", WHITE, INK),
    ("ELM327", "BLE ადაპტერი", WHITE, INK),
    ("Web Bluetooth", "ბრაუზერი", BLUE_SOFT, INK),
    ("OBD360", "Angular SPA", SAGE_SOFT, SAGE),
]
x_positions = [0.55, 3.05, 5.55, 8.05, 10.55]
for (title, subtitle, fill, title_color), left in zip(boxes, x_positions):
    rect(slide, Inches(left), Inches(2.2), Inches(2.05), Inches(1.15), fill)
    text(slide, Inches(left + 0.14), Inches(2.4), Inches(1.8), Inches(0.3),
         title, 12, True, title_color)
    text(slide, Inches(left + 0.14), Inches(2.75), Inches(1.8), Inches(0.35),
         subtitle, 8.5, False, MUTED if fill != SAGE else SAGE_SOFT)

for left in [2.62, 5.12, 7.62, 10.12]:
    arrow(slide, Inches(left), Inches(2.68), Inches(0.32), Inches(0.18))

text(slide, Inches(2.55), Inches(1.85), Inches(1.3), Inches(0.25), "CAN / K-line", 8, False, MUTED)
text(slide, Inches(5.05), Inches(1.85), Inches(1.3), Inches(0.25), "AT / PID", 8, False, MUTED)
text(slide, Inches(7.55), Inches(1.85), Inches(1.5), Inches(0.25), "BLE GATT", 8, False, MUTED)
text(slide, Inches(10.05), Inches(1.85), Inches(1.4), Inches(0.25), "HTTPS / JSON", 8, False, MUTED)

text(slide, Inches(0.6), Inches(4.05), Inches(12.1), Inches(0.3),
     "ადაპტერის ინიციალიზაცია", 10, True, SAGE)
code_block(slide, Inches(0.6), Inches(4.45), Inches(12.1), Inches(1.15), [
    "ATZ  →  ATE0  →  ATL0  →  ATS0  →  ATH0  →  ATSP0  →  0100",
    "0100 = მხარდაჭერილი PID-ები + ავტომატური პროტოკოლის არჩევა",
], 12)

text(slide, Inches(0.6), Inches(5.95), Inches(12.1), Inches(0.65),
     "ECU პასუხობს hex-ით. OBD360 ამ პასუხს ამუშავებს, ინახავს და აჩვენებს გასაგებ ტექსტად.",
     12, False, MUTED)
footer(slide)

# ---------------------------------------------------------------- 5. ECU + DTC
slide = add_slide(prs)
header(slide, "ECU", "ECU და DTC კოდები", "რას ნიშნავს ის, რასაც აპლიკაცია კითხულობს.", 5)

ecu = rect(slide, Inches(0.6), Inches(1.85), Inches(4.35), Inches(3.9), SAGE, SAGE)
text(slide, Inches(0.9), Inches(2.1), Inches(3.7), Inches(0.4), "ECU", 26, True, WHITE)
text(slide, Inches(0.9), Inches(2.55), Inches(3.7), Inches(0.5),
     "Electronic Control Unit", 11, False, SAGE_SOFT)
for index, module in enumerate(["Engine", "ABS", "Airbag", "BCM", "Transmission"]):
    rect(slide, Inches(0.9), Inches(3.15 + index * 0.38), Inches(3.6), Inches(0.27),
         SAGE_SOFT, SAGE_SOFT)
    text(slide, Inches(1.05), Inches(3.19 + index * 0.38), Inches(3.2), Inches(0.2),
         module, 9, True, SAGE)

text(slide, Inches(5.45), Inches(1.85), Inches(7.1), Inches(0.35),
     "DTC = Diagnostic Trouble Code", 15, True, SAGE)
text(slide, Inches(5.45), Inches(2.35), Inches(7.0), Inches(0.4),
     "P0300  →  P = Powertrain  ·  0 = generic  ·  300 = misfire", 13, False, INK, font=MONO)
text(slide, Inches(5.45), Inches(2.85), Inches(7.0), Inches(0.9),
     "P — ძრავი   B — ძარა   C — შასი   U — ქსელი\nპირველი სიმბოლო გვიჩვენებს სისტემას, დანარჩენი — კონკრეტულ შეცდომას.",
     12, False, MUTED)
code_block(slide, Inches(5.45), Inches(3.85), Inches(7.1), Inches(1.05), [
    "43 01 33 00 00 00 00",
    "→ P0133  (O2 sensor, bank 1, slow response)",
], 11)
text(slide, Inches(5.45), Inches(5.15), Inches(7.1), Inches(0.65),
     "რეჟიმები: 03 — stored, 07 — pending, 0A — permanent, 04 — clear.",
     12, True, INK)
footer(slide)

# ---------------------------------------------------------------- 6. ARCHITECTURE
slide = add_slide(prs)
header(slide, "არქიტექტურა", "როგორ არის აწყობილი OBD360",
       "სუფთა გამიჯვნა: UI, API, ბაზა და ავტომატიზაცია.", 6)

arch = [
    ("Angular SPA", "standalone components\nsignals · Web Bluetooth", 0.6),
    ("ASP.NET Core API", ".NET 10 · REST /api/v1\nJWT · EF Core", 4.75),
    ("SQL Server", "15 მოდელი\n21 ცხრილი", 8.9),
]
for title, note, left in arch:
    rect(slide, Inches(left), Inches(2.0), Inches(3.4), Inches(1.65), WHITE)
    text(slide, Inches(left + 0.2), Inches(2.22), Inches(3.0), Inches(0.35), title, 15, True, INK)
    text(slide, Inches(left + 0.2), Inches(2.67), Inches(3.0), Inches(0.7), note, 10, False, MUTED)
for left in [4.08, 8.23]:
    arrow(slide, Inches(left), Inches(2.68), Inches(0.55), Inches(0.22))

# n8n + Gemini
rect(slide, Inches(4.75), Inches(4.35), Inches(3.4), Inches(1.2), SAGE_SOFT)
text(slide, Inches(4.95), Inches(4.52), Inches(3.0), Inches(0.3), "n8n", 16, True, SAGE)
text(slide, Inches(4.95), Inches(4.86), Inches(3.0), Inches(0.5), "workflow automation", 9, False, MUTED)
rect(slide, Inches(8.9), Inches(4.35), Inches(3.4), Inches(1.2), BLUE_SOFT)
text(slide, Inches(9.1), Inches(4.52), Inches(3.0), Inches(0.3), "Google Gemini", 16, True, INK)
text(slide, Inches(9.1), Inches(4.86), Inches(3.0), Inches(0.5), "AI explanations", 9, False, MUTED)
arrow(slide, Inches(8.25), Inches(4.78), Inches(0.55), Inches(0.22))
arrow(slide, Inches(6.4), Inches(3.72), Inches(0.18), Inches(0.55), down=True)
text(slide, Inches(6.68), Inches(3.82), Inches(0.6), Inches(0.2), "AI", 8, True, SAGE)

text(slide, Inches(0.6), Inches(4.45), Inches(3.8), Inches(0.3), "ასისტენტი", 9, True, SAGE)
text(slide, Inches(0.6), Inches(4.8), Inches(3.8), Inches(1.2),
     "API → n8n → Gemini\nპასუხი ინახება AiMessages-ში.", 11, False, MUTED)
text(slide, Inches(0.6), Inches(6.25), Inches(12.1), Inches(0.3),
     "REST API: 32 endpoint  ·  JWT  ·  refresh cookie  ·  CORS", 11, True, SAGE)
footer(slide)

# ---------------------------------------------------------------- 7. DATA MODEL
slide = add_slide(prs)
header(slide, "მონაცემები", "მონაცემთა ბაზა — 15 მოდელი",
       "13 ბიზნეს მოდელი + ApplicationUser + ApplicationRole.", 7)

models = [
    "User", "Role", "Vehicle", "Adapter", "ScanSession",
    "LiveReading", "DtcRecord", "DtcCatalogEntry", "MaintenanceReminder", "AiConversation",
    "AiMessage", "Report", "NotificationLog", "UserPreference", "RefreshSession",
]
for index, model in enumerate(models):
    row, column = divmod(index, 5)
    left = 0.6 + column * 2.45
    top = 1.9 + row * 0.95
    rect(slide, Inches(left), Inches(top), Inches(2.25), Inches(0.68), WHITE)
    text(slide, Inches(left + 0.12), Inches(top + 0.16), Inches(2.0), Inches(0.25),
         model, 10, True, INK, font=MONO)

card(slide, Inches(0.6), Inches(5.1), Inches(3.9), Inches(1.35), "SQL Server", "21", "ფიზიკური ცხრილი", 26)
card(slide, Inches(4.7), Inches(5.1), Inches(3.9), Inches(1.35), "DTC", "13,629", "კატალოგის ჩანაწერი", 24)
card(slide, Inches(8.8), Inches(5.1), Inches(3.9), Inches(1.35), "EF Core", "Migrations", "სქემის ვერსიირება", 17)
footer(slide)

# ---------------------------------------------------------------- 8. DTC CATALOG
slide = add_slide(prs)
header(slide, "კატალოგი", "DTC კატალოგი — 13,629 კოდი",
       "თითო კოდს აქვს ქართული და ინგლისური ახსნა, სირთულე და ხარჯი.", 8)

text(slide, Inches(0.6), Inches(1.75), Inches(4.0), Inches(0.9), "13,629", 50, True, SAGE, font=MONO)
text(slide, Inches(0.6), Inches(2.65), Inches(4.0), Inches(0.3), "DTC ჩანაწერი", 11, False, MUTED)
for index, (label, value) in enumerate([("P", "Powertrain"), ("B", "Body"), ("C", "Chassis"), ("U", "Network")]):
    top = 3.2 + index * 0.55
    text(slide, Inches(0.6), Inches(top), Inches(0.4), Inches(0.3), label, 18, True, SAGE)
    text(slide, Inches(1.0), Inches(top + 0.05), Inches(3.2), Inches(0.3), value, 11, False, MUTED)

examples = [
    ("P0300", "ცილინდრის გამოტოვება", "Medium · 80–450 ₾"),
    ("P0420", "კატალიზატორის ეფექტურობა", "Hard · 300–1500 ₾"),
    ("P0A80", "ჰიბრიდული ბატარეა", "Hard · 800–4000 ₾"),
]
for index, (code, title, meta) in enumerate(examples):
    top = 1.8 + index * 1.25
    rect(slide, Inches(5.0), Inches(top), Inches(7.4), Inches(1.0), WHITE)
    text(slide, Inches(5.2), Inches(top + 0.16), Inches(1.2), Inches(0.3), code, 15, True, INK, font=MONO)
    text(slide, Inches(6.5), Inches(top + 0.15), Inches(5.6), Inches(0.3), title, 12, True, INK)
    text(slide, Inches(6.5), Inches(top + 0.5), Inches(5.6), Inches(0.25), meta, 9, False, MUTED)

text(slide, Inches(5.0), Inches(5.7), Inches(7.4), Inches(0.3),
     "read → parse → catalog → AI explanation", 12, True, SAGE, font=MONO)
footer(slide)

# ---------------------------------------------------------------- 9. LIVE DATA
slide = add_slide(prs)
header(slide, "Live Data", "PIDs — რეალურ დროში მონაცემები",
       "აპლიკაცია ECU-ს კითხულობს ყოველ 500 ms-ში.", 9)

card(slide, Inches(0.6), Inches(1.8), Inches(2.7), Inches(1.05), "RPM", "010C", "ბრუნი", 22)
card(slide, Inches(3.45), Inches(1.8), Inches(2.7), Inches(1.05), "SPEED", "010D", "სიჩქარე", 22)
card(slide, Inches(0.6), Inches(3.0), Inches(2.7), Inches(1.05), "COOLANT", "0105", "ტემპერატურა", 20)
card(slide, Inches(3.45), Inches(3.0), Inches(2.7), Inches(1.05), "VOLTAGE", "0142", "ძაბვა", 20)

text(slide, Inches(0.6), Inches(4.3), Inches(5.6), Inches(0.9),
     "PID = Parameter ID. ECU აბრუნებს hex-ს; decoder აქცევს ფიზიკურ მნიშვნელობად.",
     11, False, MUTED)
code_block(slide, Inches(0.6), Inches(4.95), Inches(5.5), Inches(1.05), [
    "RPM = ((A * 256) + B) / 4",
    "SPEED = A        COOLANT = A - 40",
], 10)

rect(slide, Inches(6.7), Inches(1.8), Inches(6.0), Inches(4.25), WHITE)
add_picture_fit(slide, ASSETS / "live-data.png", Inches(6.85), Inches(1.95), Inches(5.7), Inches(3.95))
text(slide, Inches(6.9), Inches(6.15), Inches(5.6), Inches(0.3),
     "აპლიკაცია ადაპტერის მოლოდინში — Live Data ეკრანი.", 9, False, MUTED)
footer(slide)

# ---------------------------------------------------------------- 10. CODE STRUCTURE
slide = add_slide(prs)
header(slide, "კოდი", "კოდის სტრუქტურა", "ერთი feature — ერთი standalone component; ერთი endpoint — ერთი controller.", 10)

code_block(slide, Inches(0.6), Inches(1.8), Inches(6.0), Inches(3.55), [
    "frontend/src/app/",
    "  core/services/",
    "    obd-bluetooth.service.ts",
    "    dtc-scan.service.ts",
    "    auth.ts · vehicles.service.ts",
    "  features/",
    "    garage/  reminders/  admin/",
    "    live-data/  dtc-scanner/",
    "  layout/main-layout/",
    "  app.routes.ts",
], 10)

code_block(slide, Inches(6.9), Inches(1.8), Inches(5.85), Inches(3.55), [
    "backend/",
    "  Obd360.Api/",
    "    Controllers/",
    "    Integrations/N8n/",
    "    Services/",
    "  Obd360.Core/",
    "    Entities/  Enums/",
    "  Obd360.Infrastructure/",
    "    Data/  Migrations/",
    "    Identity/  Services/",
], 10)

text(slide, Inches(0.6), Inches(5.55), Inches(12.1), Inches(0.3),
     "frontend: standalone + Signals      backend: controllers + DTOs + EF Core", 11, True, SAGE)

footer(slide)

# ---------------------------------------------------------------- 11. SCAN FLOW
slide = add_slide(prs)
header(slide, "კოდის ნაკადი", "სკანირება: Bluetooth → DTC → ბაზა",
       "რეალური ბრძანებები, რომლებსაც OBD360 აგზავნის.", 11)

code_block(slide, Inches(0.6), Inches(1.8), Inches(7.4), Inches(3.55), [
    "const device = await navigator.bluetooth",
    "  .requestDevice({ filters: OBD_SERVICES });",
    "",
    "await obd.connect();",
    "await obd.send('ATZ');",
    "for (const cmd of ['ATE0','ATL0','ATS0',",
    "                   'ATH0','ATSP0']) await obd.send(cmd);",
    "",
    "await obd.send('0100');",
    "const stored    = await obd.send('03');",
    "const pending   = await obd.send('07');",
    "const permanent = await obd.send('0A');",
    "",
    "await scansApi.save({ vin, codes, startedAt });",
], 9.5)

text(slide, Inches(8.3), Inches(1.9), Inches(4.4), Inches(0.3), "რას აკეთებს", 10, True, SAGE)
bullets(slide, Inches(8.3), Inches(2.3), Inches(4.4), Inches(3.8), [
    "ატარებს ELM327-ის ინიციალიზაციას.",
    "03/07/0A-ით კითხულობს stored, pending და permanent კოდებს.",
    "0902-ით იღებს VIN-ს.",
    "04-ით შლის კოდებს — მხოლოდ დადასტურების შემდეგ.",
    "შედეგი ინახება ScanSession/DtcRecord-ში.",
], 11)
footer(slide)

# ---------------------------------------------------------------- 12. PARSER
slide = add_slide(prs)
header(slide, "პარსერი", "რას ელოდება კოდი ECU-სგან",
       "ELM327 აბრუნებს hex ტექსტს; OBD360 მას გადააქცევს სტრუქტურირებულ პასუხად.", 12)

code_block(slide, Inches(0.6), Inches(1.8), Inches(7.3), Inches(3.65), [
    "03  →  43 01 33 00 00 00 00",
    "07  →  47 01 71",
    "0A  →  4A 00 00",
    "0902 →  49 02 01 31 47 31 52 42 ...",
    "",
    "43 = response to 03   (0x40 + mode)",
    "47 = response to 07   (0x40 + mode)",
    "4A = response to 0A   (0x40 + mode)",
], 10)

text(slide, Inches(8.2), Inches(1.9), Inches(4.5), Inches(0.3), "წესები", 10, True, SAGE)
bullets(slide, Inches(8.2), Inches(2.3), Inches(4.5), Inches(3.8), [
    "პირველი ბაიტი: 43 / 47 / 4A — მიუთითებს, რომელი რეჟიმის პასუხია.",
    "0000 — padding; იგნორირდება.",
    "NO DATA — ECU-ს ამ რეჟიმში კოდი არ აქვს.",
    "CAN-ის frame-ები (7E8) იკრიბება ერთ პასუხად.",
    "DTC = 2 ბაიტი; პირველი nibble → P/B/C/U.",
], 10.5)

text(slide, Inches(0.6), Inches(5.75), Inches(12.1), Inches(0.35),
     "OBD360: parseDtcResponse(raw, mode, isCan) → string[] → catalog lookup", 11, True, SAGE)
footer(slide)

# ---------------------------------------------------------------- 13. SECURITY
slide = add_slide(prs)
header(slide, "უსაფრთხოება", "ავტორიზაცია და წვდომა",
       "JWT + refresh rotation + როლები + პაროლის აღდგენა.", 13)

card(slide, Inches(0.6), Inches(1.85), Inches(2.85), Inches(1.35), "ACCESS", "15 წთ", "JWT Bearer", 26)
card(slide, Inches(3.65), Inches(1.85), Inches(2.85), Inches(1.35), "REFRESH", "30 დღე", "HttpOnly cookie", 23)
card(slide, Inches(6.7), Inches(1.85), Inches(2.85), Inches(1.35), "RESET", "6 ციფრი", "10 წუთი · 5 მცდელობა", 23)
card(slide, Inches(9.75), Inches(1.85), Inches(2.85), Inches(1.35), "ADMIN", "Role", "დაცული endpoints", 26)

bullets(slide, Inches(0.6), Inches(3.55), Inches(6.2), Inches(2.6), [
    "პაროლი ინახება Identity-ის hash-ით.",
    "Refresh token ბაზაში ჰეშირებულია და rotation-ით იცვლება.",
    "პაროლის შეცვლისას ყველა refresh session უქმდება.",
], 13)
bullets(slide, Inches(6.9), Inches(3.55), Inches(5.8), Inches(2.6), [
    "Admin გვერდი: [Authorize(Roles = \"Admin\")].",
    "საკუთარი თავის და ბოლო Admin-ის წაშლა დაბლოკილია.",
    "CORS მხოლოდ http://localhost:4200-დან.",
], 13)
footer(slide)

# ---------------------------------------------------------------- 14. AI
slide = add_slide(prs)
header(slide, "AI", "AI ასისტენტი — n8n + Gemini",
       "ტექნიკური პასუხი ქართულად, სკანირების კონტექსტით.", 14)

ai_boxes = [
    ("OBD360", "კითხვა / რეპორტი", 0.6),
    ("API", "/ai/ask", 3.55),
    ("n8n", "webhook", 6.5),
    ("Gemini", "LLM", 9.45),
]
for title, subtitle, left in ai_boxes:
    rect(slide, Inches(left), Inches(2.0), Inches(2.45), Inches(1.15), WHITE)
    text(slide, Inches(left + 0.16), Inches(2.2), Inches(2.1), Inches(0.3), title, 14, True, INK)
    text(slide, Inches(left + 0.16), Inches(2.55), Inches(2.1), Inches(0.3), subtitle, 9, False, MUTED)
for left in [3.08, 6.03, 8.98]:
    arrow(slide, Inches(left), Inches(2.45), Inches(0.4), Inches(0.2))

bullets(slide, Inches(0.6), Inches(3.65), Inches(12.0), Inches(2.4), [
    "Prompt Builder ამატებს მანქანის მონაცემებს, DTC კოდებს და საუბრის ისტორიას.",
    "n8n იძახებს Gemini-ს; პასუხი ინახება AiConversations/AiMessages-ში.",
    "კრიტიკული DTC → n8n → Telegram alert (SMTP/Telegram არხი).",
], 13)
footer(slide)

# ---------------------------------------------------------------- 15. REMINDERS
slide = add_slide(prs)
header(slide, "შეხსენება", "Maintenance Reminders — email",
       "თარიღი → ფონური შემოწმება → digest email.", 15)

steps = [
    ("Reminder", "dueAtDate", 0.6),
    ("BackgroundService", "ყოველ 6 საათში", 3.45),
    ("SMTP", "email", 6.6),
    ("NotificationLogs", "დუბლიკატის გარეშე", 9.35),
]
for title, subtitle, left in steps:
    rect(slide, Inches(left), Inches(2.0), Inches(2.55), Inches(1.15), WHITE)
    text(slide, Inches(left + 0.16), Inches(2.2), Inches(2.2), Inches(0.3), title, 12, True, INK)
    text(slide, Inches(left + 0.16), Inches(2.55), Inches(2.2), Inches(0.35), subtitle, 9, False, MUTED)
for left in [3.0, 6.0, 8.95]:
    arrow(slide, Inches(left), Inches(2.45), Inches(0.35), Inches(0.2))

bullets(slide, Inches(0.6), Inches(3.65), Inches(12.0), Inches(2.2), [
    "ერთ მომხმარებელზე დღეში მხოლოდ ერთი digest მეილი.",
    "მუშაობს მხოლოდ თარიღით — კმ-ით რემაინდერისთვის გარბენი ჯერ არ ინახება.",
    "SMTP-ის გარეშე Development-ში კოდი/ბმული ლოგში ჩანს.",
], 13)
footer(slide)

# ---------------------------------------------------------------- 16. DEMO
slide = add_slide(prs)
header(slide, "დემო", "OBD360 — ეკრანები", "მსუბუქი UI, ბურგერ მენიუ მობილურზე და რეალური მონაცემები.", 16)

shots = [
    ("dashboard.png", "Dashboard", "Live data · DTC · AI"),
    ("garage.png", "Garage", "მანქანების CRUD"),
    ("reminders.png", "Reminders", "ვადები და Overdue"),
]
for index, (file_name, title, caption) in enumerate(shots):
    left = 0.6 + index * 4.15
    rect(slide, Inches(left), Inches(1.85), Inches(3.85), Inches(3.75), WHITE)
    add_picture_fit(slide, ASSETS / file_name, Inches(left + 0.12), Inches(1.97), Inches(3.6), Inches(3.05))
    text(slide, Inches(left + 0.18), Inches(5.15), Inches(3.5), Inches(0.3), title, 12, True, INK)
    text(slide, Inches(left + 0.18), Inches(5.45), Inches(3.5), Inches(0.25), caption, 8.5, False, MUTED)

text(slide, Inches(0.6), Inches(6.15), Inches(12.1), Inches(0.4),
     "მობილურზე: ბურგერ მენიუ მარცხნიდან, overlay და sticky header.", 11, False, MUTED)
footer(slide)

# ---------------------------------------------------------------- 17. TESTS
slide = add_slide(prs)
header(slide, "ხარისხი", "ტესტები და ინჟინერია", "რას ამოწმებს პროექტი დღეს.", 17)

card(slide, Inches(0.6), Inches(1.8), Inches(2.9), Inches(1.25), "BACKEND", "29", "passed", 26)
card(slide, Inches(3.65), Inches(1.8), Inches(2.9), Inches(1.25), "FRONTEND", "19", "passed", 26)
card(slide, Inches(6.7), Inches(1.8), Inches(2.9), Inches(1.25), "REST", "32", "endpoint", 26)
card(slide, Inches(9.75), Inches(1.8), Inches(2.9), Inches(1.25), "MODELS", "15", "მონაცემი", 26)

bullets(slide, Inches(0.6), Inches(3.55), Inches(6.1), Inches(2.8), [
    "C4: Context + Container + Component.",
    "Swagger: JWT Authorize + XML summaries.",
    "HTTP request logging + auth/reminder ლოგები.",
], 12)
bullets(slide, Inches(6.9), Inches(3.55), Inches(5.7), Inches(2.8), [
    "GitHub: Laziii54/OBD360-Web.",
    "Admin: რეალური users/scans + role management.",
    "შემდეგი: DTC admin editing, Reports, mobile app.",
], 12)
footer(slide)

# ---------------------------------------------------------------- 18. THANK YOU
slide = add_slide(prs)
header(slide, "დასკვნა", "მადლობა", None, 18)
text(slide, Inches(0.6), Inches(1.6), Inches(10.5), Inches(0.9),
     "OBD360 Web", 46, True, INK)
text(slide, Inches(0.6), Inches(2.55), Inches(8.5), Inches(0.5),
     "ავტომობილის დიაგნოსტიკა — გასაგები, სწრაფი და ხელმისაწვდომი.", 18, False, SAGE)
text(slide, Inches(0.6), Inches(4.0), Inches(8.0), Inches(0.4),
     "კითხვები?", 24, True, INK)
text(slide, Inches(0.6), Inches(5.5), Inches(8.0), Inches(0.4),
     "github.com/Laziii54/OBD360-Web", 12, True, SAGE)
text(slide, Inches(0.6), Inches(6.0), Inches(8.0), Inches(0.3),
     "ზურაბ ლაზაშვილი  ·  2026", 10, False, MUTED)
footer(slide)

notes = {
    1: "შესავალი: OBD360 აერთიანებს OBD-II ადაპტერს, ვებ-აპლიკაციას და AI ასისტენტს. პროექტის მიზანია DTC კოდებისა და Live Data-ს გასაგებ ენაზე წარდგენა.",
    3: "OBD-II არის სტანდარტი, რომელიც 1996 წლიდან სავალდებულოა აშშ-ში. 16-pin პორტი იძლევა წვდომას ECU-ზე. CAN-H (pin 6) და CAN-L (pin 14) გადასცემს მონაცემებს; pin 16 — +12V, pin 4/5 — მიწა.",
    4: "ELM327 არის შუამავალი: ბრაუზერიდან მიღებულ AT/PID ბრძანებას გადასცემს მანქანის ECU-ს და პასუხს უკან აბრუნებს. Web Bluetooth მუშაობს Chrome/Edge-ში და საჭიროებს HTTPS ან localhost-ს.",
    5: "DTC-ის პირველი ასო განსაზღვრავს სისტემას: P — ძრავი, B — ძარა, C — შასი, U — ქსელი. 03 კითხულობს stored, 07 — pending, 0A — permanent კოდებს. 04 შლის კოდებს, ამიტომ აპლიკაცია მას მხოლოდ დადასტურების შემდეგ აგზავნის.",
    6: "არქიტექტურა გამიჯნულია: Angular არის წარმოდგენის ფენა, ASP.NET Core — ბიზნეს ლოგიკა და REST API, SQL Server — მონაცემები. n8n აორკესტრირებს AI workflow-ს, Gemini აბრუნებს ახსნას.",
    7: "15 მოდელი საკმარისია სრული სცენარისთვის: ავტორიზაცია, მანქანა, ადაპტერი, სკანირება, Live Data, DTC, შეხსენება, AI საუბარი, რეპორტი, notification log, პრეფერენსები და refresh session.",
    8: "კატალოგში 13,629 ჩანაწერია. თითოეულს აქვს კოდი, ქართული/ინგლისური სახელი, აღწერა, სირთულე, სავარაუდო ღირებულება და სამუშაო საათები. ეს იძლევა იმის საშუალებას, რომ მძღოლმა კოდი მაშინვე გაიგოს.",
    9: "Live Data იღებს PID-ებს: 010C (RPM), 010D (სიჩქარე), 0105 (გამაგრილებლის ტემპერატურა), 0142 (ძაბვა). პასუხი hex-ია; decoder აკეთებს ფორმულას და ინახავს LiveReading-ში.",
    10: "Frontend არის standalone components + Signals. Backend იყენებს controllers, DTO-ებს, EF Core-ს. ერთი feature — ერთი კომპონენტი, ერთი endpoint — ერთი controller.",
    11: "სკანირების ნაკადი: Bluetooth-ით დაკავშირება → ATZ/ATE0/ATSP0 ინიციალიზაცია → 0100 მხარდაჭერილი PID-ების შემოწმება → 03/07/0A კოდების კითხვა → 0902 VIN → შედეგის ScanSession/DtcRecord-ში შენახვა.",
    12: "პარსერი ელოდება პასუხის პირველ ბაიტს 0x40 + mode: 03 → 43, 07 → 47, 0A → 4A. 0000 არის padding. CAN-ის frame-ები (7E8) იკრიბება. DTC არის 2 ბაიტი; პირველი nibble განსაზღვრავს P/B/C/U-ს.",
    13: "უსაფრთხოება: მოკლევადიანი JWT, ხანგრძლივი refresh cookie, rotation, ჰეშირებული refresh token, პაროლის აღდგენა 6-ციფრიანი კოდით და Admin როლი.",
    14: "AI ნაკადი: Angular აგზავნის კითხვას API-ზე, API ამდიდრებს prompt-ს მანქანის/DTC კონტექსტით, n8n იძახებს Gemini-ს და პასუხი ინახება. კრიტიკული კოდები შეიძლება გაიგზავნოს Telegram-ზე.",
    15: "რემაინდერები მუშაობს ფონურ სერვისში: ამოწმებს DueAtDate-ს ყოველ 6 საათში, აგზავნის ერთ digest მეილს დღეში და NotificationLogs-ით თავიდან ირიდებს დუბლიკატს.",
    16: "დემო: Dashboard, Garage და Reminders. მობილურზე sidebar იხსნება ბურგერ მენიუდან, overlay-ით და sticky header-ით.",
}

for index, note in notes.items():
    prs.slides[index - 1].notes_slide.notes_text_frame.text = note

prs.save(OUT)
print(f"saved {OUT} with {len(prs.slides)} slides")
