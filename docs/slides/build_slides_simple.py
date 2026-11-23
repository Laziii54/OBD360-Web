from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

BASE = Path(r"C:\Users\zukal\OneDrive\Desktop\OBD2 WEB\docs\slides")
ASSETS = BASE / "assets"
OUT = BASE / "OBD2-Web-Presentation-Simple.pptx"

BG = RGBColor(0xF7, 0xF5, 0xF0)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
INK = RGBColor(0x20, 0x25, 0x1F)
MUTED = RGBColor(0x72, 0x77, 0x6E)
SAGE = RGBColor(0x3F, 0x5D, 0x4E)
SAGE_SOFT = RGBColor(0xE9, 0xEF, 0xE9)
LINE = RGBColor(0xE4, 0xE0, 0xD7)
CODE_BG = RGBColor(0x1F, 0x29, 0x24)
CODE_FG = RGBColor(0xE8, 0xEF, 0xE9)
BLUE_SOFT = RGBColor(0xE8, 0xEE, 0xF0)

FONT = "Sylfaen"
MONO = "Consolas"


def add_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = BG
    return slide


def text(slide, left, top, width, height, value, size=18, bold=False,
         color=INK, font=FONT, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
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
    run = paragraph.add_run()
    run.text = value
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def bullets(slide, left, top, width, height, items, size=16, spacing=12):
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
        marker = paragraph.add_run()
        marker.text = "•  "
        marker.font.name = FONT
        marker.font.size = Pt(size)
        marker.font.bold = True
        marker.font.color.rgb = SAGE
        run = paragraph.add_run()
        run.text = item
        run.font.name = FONT
        run.font.size = Pt(size)
        run.font.color.rgb = INK
    return box


def rect(slide, left, top, width, height, fill=WHITE, line=LINE):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line
    shape.line.width = Pt(1)
    shape.adjustments[0] = 0.08
    return shape


def header(slide, kicker, title, subtitle=None, number=None):
    text(slide, Inches(0.6), Inches(0.38), Inches(11), Inches(0.25), kicker.upper(), 9, True, SAGE)
    text(slide, Inches(0.6), Inches(0.67), Inches(12.1), Inches(0.62), title, 30, True, INK)
    if subtitle:
        text(slide, Inches(0.6), Inches(1.27), Inches(11.7), Inches(0.4), subtitle, 13, False, MUTED)
    if number is not None:
        text(slide, Inches(12.2), Inches(0.38), Inches(0.6), Inches(0.3), f"{number:02d}", 9, True, MUTED, align=PP_ALIGN.RIGHT)


def footer(slide, number):
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(7.02), Inches(12.13), Inches(0.01))
    line.fill.solid()
    line.fill.fore_color.rgb = LINE
    line.line.fill.background()
    text(slide, Inches(0.6), Inches(7.1), Inches(8), Inches(0.2), "OBD2 Web  ·  2026", 8, False, MUTED)
    text(slide, Inches(12.1), Inches(7.1), Inches(0.6), Inches(0.2), f"{number:02d}", 8, True, SAGE, align=PP_ALIGN.RIGHT)


def code_block(slide, left, top, width, height, lines, size=12):
    rect(slide, left, top, width, height, CODE_BG, CODE_BG)
    box = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.35), height - Inches(0.25))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = False
    frame.margin_left = 0
    frame.margin_right = 0
    frame.margin_top = 0
    frame.margin_bottom = 0
    for index, line in enumerate(lines):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.space_after = Pt(3)
        run = paragraph.add_run()
        run.text = line
        run.font.name = MONO
        run.font.size = Pt(size)
        run.font.color.rgb = CODE_FG


def picture_fit(slide, path, left, top, width, height):
    with Image.open(path) as image:
        image_width, image_height = image.size
    scale = min(width / image_width, height / image_height)
    new_width = int(image_width * scale)
    new_height = int(image_height * scale)
    slide.shapes.add_picture(str(path), left + (width - new_width) // 2, top + (height - new_height) // 2, new_width, new_height)


prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# 1 TITLE
slide = add_slide(prs)
rect(slide, Inches(8.75), Inches(0.6), Inches(3.95), Inches(6.3), SAGE, SAGE)
text(slide, Inches(9.1), Inches(1.0), Inches(3.2), Inches(0.3), "OBD-II  ·  Web", 10, True, SAGE_SOFT)
text(slide, Inches(9.1), Inches(1.45), Inches(3.2), Inches(1.2), "OBD2", 44, True, WHITE)
text(slide, Inches(9.1), Inches(3.55), Inches(3.0), Inches(1.1), "მანქანის\nდიაგნოსტიკა\nმარტივად", 20, True, WHITE)
text(slide, Inches(9.1), Inches(5.9), Inches(3.1), Inches(0.3), "Angular · .NET · SQL Server", 8, False, SAGE_SOFT)
text(slide, Inches(0.65), Inches(1.0), Inches(7.7), Inches(0.3), "სადიპლომო პროექტი", 11, True, SAGE)
text(slide, Inches(0.65), Inches(1.6), Inches(8.0), Inches(1.2), "OBD2 Web", 54, True, INK)
text(slide, Inches(0.65), Inches(2.9), Inches(7.5), Inches(0.6), "მანქანის დიაგნოსტიკა მარტივ ენაზე", 22, False, SAGE)
text(slide, Inches(0.65), Inches(3.8), Inches(7.4), Inches(0.8), "OBD-II → ECU → კოდები → გასაგები ახსნა", 15, False, MUTED)
text(slide, Inches(0.65), Inches(6.2), Inches(7.0), Inches(0.3), "ზურაბ ლაზაშვილი  ·  2026", 11, True, INK)

# 2 PROBLEM
slide = add_slide(prs)
header(slide, "პრობლემა", "რატომ გვჭირდება OBD2?", "მანქანა კოდს გაჩვენებს — ახსნას არა.", 2)
bullets(slide, Inches(0.6), Inches(1.8), Inches(6.4), Inches(3.3), [
    "მძღოლი ხედავს P0300-ს და ვერ ხვდება, რა ნიშნავს.",
    "სერვისამდე არ იცის, რა ხდება და რა ღირს.",
    "სკანირებები და შეხსენებები იკარგება.",
], 18, 14)
rect(slide, Inches(7.6), Inches(1.8), Inches(5.1), Inches(3.5))
text(slide, Inches(7.9), Inches(2.05), Inches(4.5), Inches(0.25), "მაგალითი", 9, True, SAGE)
text(slide, Inches(7.9), Inches(2.45), Inches(4.5), Inches(0.6), "P0300", 38, True, INK, font=MONO)
text(slide, Inches(7.9), Inches(3.25), Inches(4.5), Inches(0.4), "ცილინდრის გამოტოვება", 18, True, INK)
text(slide, Inches(7.9), Inches(3.8), Inches(4.5), Inches(0.7), "OBD2 ამას ხსნის და ინახავს ისტორიას.", 12, False, MUTED)
text(slide, Inches(0.6), Inches(5.8), Inches(12), Inches(0.4), "13,629 კოდი · 15 მოდელი · 32 API endpoint", 15, True, SAGE)
footer(slide, 2)

# 3 OBD-II
slide = add_slide(prs)
header(slide, "OBD-II", "რა არის OBD-II?", "მანქანის დიაგნოსტიკის სტანდარტი.", 3)
rect(slide, Inches(0.7), Inches(1.9), Inches(3.9), Inches(2.8), RGBColor(0x2D, 0x35, 0x30), RGBColor(0x2D, 0x35, 0x30))
text(slide, Inches(1.0), Inches(2.1), Inches(3.3), Inches(0.3), "OBD-II  16-PIN", 12, True, WHITE)
for row in range(2):
    for column in range(8):
        pin = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(1.1 + column * 0.4), Inches(2.85 + row * 0.7), Inches(0.17), Inches(0.17))
        pin.fill.solid()
        pin.fill.fore_color.rgb = SAGE_SOFT
        pin.line.fill.background()
text(slide, Inches(1.0), Inches(4.2), Inches(3.3), Inches(0.3), "16 პინი · CAN · K-line", 9, False, SAGE_SOFT)

for index, (title, note) in enumerate([
    ("16 PIN", "დიაგნოსტიკური პორტი"),
    ("PID", "ცოცხალი მონაცემები"),
    ("DTC", "შეცდომის კოდი"),
]):
    top = Inches(1.95 + index * 0.95)
    rect(slide, Inches(5.2), top, Inches(7.1), Inches(0.78), WHITE)
    text(slide, Inches(5.45), top + Inches(0.18), Inches(1.2), Inches(0.3), title, 14, True, SAGE)
    text(slide, Inches(6.65), top + Inches(0.19), Inches(5.2), Inches(0.3), note, 14, False, INK)
text(slide, Inches(5.2), Inches(4.95), Inches(7.1), Inches(0.6), "ELM327 ადაპტერი კითხულობს ECU-ს და პასუხს ბრაუზერს უბრუნებს.", 13, False, MUTED)
footer(slide, 3)

# 4 CONNECTION
slide = add_slide(prs)
header(slide, "კავშირი", "როგორ მუშაობს?", "ECU → პორტი → ადაპტერი → ბრაუზერი → OBD2.", 4)
boxes = [("ECU", "მანქანის ტვინი", SAGE, WHITE), ("OBD-II", "16-pin პორტი", WHITE, INK), ("ELM327", "BLE ადაპტერი", WHITE, INK), ("ბრაუზერი", "Web Bluetooth", BLUE_SOFT, INK), ("OBD2", "Angular", SAGE_SOFT, SAGE)]
positions = [0.55, 3.05, 5.55, 8.05, 10.55]
for (title, note, fill, color), left in zip(boxes, positions):
    rect(slide, Inches(left), Inches(2.0), Inches(2.05), Inches(1.25), fill)
    text(slide, Inches(left + 0.14), Inches(2.2), Inches(1.8), Inches(0.3), title, 13, True, color)
    text(slide, Inches(left + 0.14), Inches(2.6), Inches(1.8), Inches(0.4), note, 9, False, MUTED if fill != SAGE else SAGE_SOFT)
for left in [2.62, 5.12, 7.62, 10.12]:
    arrow = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(left), Inches(2.5), Inches(0.3), Inches(0.18))
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = SAGE
    arrow.line.fill.background()
text(slide, Inches(0.6), Inches(3.8), Inches(12), Inches(0.3), "აპლიკაციის ბრძანებები", 10, True, SAGE)
code_block(slide, Inches(0.6), Inches(4.2), Inches(12.1), Inches(1.0), [
    "ATZ → ATE0 → ATSP0 → 0100",
    "03 / 07 / 0A → DTC     ·     0902 → VIN     ·     04 → clear",
], 13)
text(slide, Inches(0.6), Inches(5.55), Inches(12), Inches(0.5), "ECU პასუხობს hex-ით; OBD2 მას გასაგებ ტექსტად აქცევს.", 13, False, MUTED)
footer(slide, 4)

# 5 ECU + DTC
slide = add_slide(prs)
header(slide, "ECU + DTC", "რას ნიშნავს კოდი?", "ECU ინახავს ხარვეზს, OBD2 ხსნის.", 5)
rect(slide, Inches(0.6), Inches(1.8), Inches(4.2), Inches(3.8), SAGE, SAGE)
text(slide, Inches(0.9), Inches(2.0), Inches(3.6), Inches(0.5), "ECU", 30, True, WHITE)
text(slide, Inches(0.9), Inches(2.5), Inches(3.6), Inches(0.3), "მანქანის ელექტრონული ტვინი", 11, False, SAGE_SOFT)
for index, module in enumerate(["Engine", "ABS", "Airbag", "BCM"]):
    rect(slide, Inches(0.9), Inches(3.05 + index * 0.52), Inches(3.6), Inches(0.36), SAGE_SOFT, SAGE_SOFT)
    text(slide, Inches(1.05), Inches(3.12 + index * 0.52), Inches(3.2), Inches(0.2), module, 10, True, SAGE)

text(slide, Inches(5.3), Inches(1.8), Inches(7.2), Inches(0.65), "P0300", 32, True, INK, font=MONO)
text(slide, Inches(5.3), Inches(2.35), Inches(7.2), Inches(0.4), "P = Powertrain · 0 = generic · 300 = misfire", 13, False, INK)
text(slide, Inches(5.3), Inches(2.9), Inches(7.2), Inches(1.1), "P — ძრავი\nB — ძარა\nC — შასი\nU — ქსელი", 13, False, MUTED)
code_block(slide, Inches(5.3), Inches(4.2), Inches(7.2), Inches(0.9), ["43 01 33 00 00  ->  P0133"], 13)
text(slide, Inches(5.3), Inches(5.35), Inches(7.2), Inches(0.3), "03 stored · 07 pending · 0A permanent · 04 clear", 12, True, SAGE)
footer(slide, 5)

# 6 ARCHITECTURE
slide = add_slide(prs)
header(slide, "არქიტექტურა", "სამი ნაწილი", "ეკრანი · ლოგიკა · მონაცემები.", 6)
for title, note, left in [
    ("Angular", "ეკრანი\nWeb Bluetooth", 0.6),
    ("ASP.NET Core API", "ლოგიკა\nREST · JWT", 4.8),
    ("SQL Server", "მონაცემები\nEF Core", 9.0),
]:
    rect(slide, Inches(left), Inches(2.0), Inches(3.3), Inches(1.6), WHITE)
    text(slide, Inches(left + 0.2), Inches(2.2), Inches(2.9), Inches(0.3), title, 15, True, INK)
    text(slide, Inches(left + 0.2), Inches(2.65), Inches(2.9), Inches(0.6), note, 11, False, MUTED)
for left in [4.0, 8.2]:
    arrow = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(left), Inches(2.7), Inches(0.5), Inches(0.2))
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = SAGE
    arrow.line.fill.background()
rect(slide, Inches(4.8), Inches(4.4), Inches(3.3), Inches(1.1), SAGE_SOFT)
text(slide, Inches(5.0), Inches(4.6), Inches(2.9), Inches(0.25), "n8n", 16, True, SAGE)
text(slide, Inches(5.0), Inches(4.95), Inches(2.9), Inches(0.3), "AI workflow", 10, False, MUTED)
rect(slide, Inches(9.0), Inches(4.4), Inches(3.3), Inches(1.1), BLUE_SOFT)
text(slide, Inches(9.2), Inches(4.6), Inches(2.9), Inches(0.25), "Gemini", 16, True, INK)
text(slide, Inches(9.2), Inches(4.95), Inches(2.9), Inches(0.3), "ახსნები", 10, False, MUTED)
text(slide, Inches(0.6), Inches(6.0), Inches(12), Inches(0.3), "32 endpoint · JWT · refresh cookie · 15 მოდელი", 12, True, SAGE)
footer(slide, 6)

# 7 DATA
slide = add_slide(prs)
header(slide, "მონაცემები", "რა ინახება?", "15 მოდელი · 21 ცხრილი · 13,629 DTC.", 7)
for title, value, left in [
    ("მოდელი", "15", 0.6),
    ("ცხრილი", "21", 3.7),
    ("DTC", "13,629", 6.8),
    ("Endpoint", "32", 9.9),
]:
    rect(slide, Inches(left), Inches(1.8), Inches(2.8), Inches(1.2), WHITE)
    text(slide, Inches(left + 0.2), Inches(1.95), Inches(2.4), Inches(0.2), title.upper(), 8, True, MUTED)
    text(slide, Inches(left + 0.2), Inches(2.2), Inches(2.4), Inches(0.5), value, 24, True, SAGE)
text(slide, Inches(0.6), Inches(3.3), Inches(12.1), Inches(0.3), "მთავარი მოდელები", 10, True, SAGE)
models = ["User", "Vehicle", "ScanSession", "DtcRecord", "DtcCatalogEntry", "Reminder", "AiConversation", "NotificationLog"]
for index, model in enumerate(models):
    row, column = divmod(index, 4)
    left = 0.6 + column * 3.05
    top = 3.75 + row * 0.72
    rect(slide, Inches(left), Inches(top), Inches(2.8), Inches(0.5), WHITE)
    text(slide, Inches(left + 0.12), Inches(top + 0.12), Inches(2.5), Inches(0.2), model, 10, True, INK, font=MONO)
text(slide, Inches(0.6), Inches(5.5), Inches(12), Inches(0.3), "SQL Server · EF Core migrations · schema.sql", 11, False, MUTED)
footer(slide, 7)

# 8 SCAN CODE
slide = add_slide(prs)
header(slide, "კოდი", "სკანირება მარტივად", "ბრაუზერი → ადაპტერი → ECU → ბაზა.", 8)
code_block(slide, Inches(0.6), Inches(1.8), Inches(7.4), Inches(3.2), [
    "await obd.connect();",
    "await obd.send('ATZ');",
    "await obd.send('0100');",
    "",
    "const stored = await obd.send('03');",
    "const pending = await obd.send('07');",
    "const permanent = await obd.send('0A');",
    "",
    "await scansApi.save({ vin, codes });",
], 11)
bullets(slide, Inches(8.3), Inches(1.9), Inches(4.4), Inches(3.6), [
    "ატარებს ადაპტერის ინიციალიზაციას.",
    "კითხულობს stored/pending/permanent კოდებს.",
    "შედეგი ინახება ისტორიაში.",
], 13, 14)
text(slide, Inches(0.6), Inches(5.4), Inches(12), Inches(0.4), "03 = stored · 07 = pending · 0A = permanent · 04 = clear", 11, True, SAGE)
footer(slide, 8)

# 9 SECURITY
slide = add_slide(prs)
header(slide, "უსაფრთხოება", "ავტორიზაცია", "JWT + refresh + reset + Admin.", 9)
for label, value, note, left in [
    ("ACCESS", "15 წთ", "JWT", 0.6),
    ("REFRESH", "30 დღე", "HttpOnly cookie", 3.7),
    ("RESET", "6 ციფრი", "10 წუთი", 6.8),
    ("ADMIN", "Role", "დაცული API", 9.9),
]:
    rect(slide, Inches(left), Inches(1.8), Inches(2.8), Inches(1.3), WHITE)
    text(slide, Inches(left + 0.2), Inches(1.95), Inches(2.4), Inches(0.2), label, 8, True, MUTED)
    text(slide, Inches(left + 0.2), Inches(2.25), Inches(2.4), Inches(0.5), value, 24, True, INK)
    text(slide, Inches(left + 0.2), Inches(2.8), Inches(2.4), Inches(0.2), note, 9, False, MUTED)
bullets(slide, Inches(0.6), Inches(3.6), Inches(5.8), Inches(2.4), [
    "პაროლი ინახება hash-ით.",
    "Refresh token ბაზაში ჰეშირებულია.",
    "პაროლის შეცვლისას სესიები უქმდება.",
], 13)
bullets(slide, Inches(6.8), Inches(3.6), Inches(5.8), Inches(2.4), [
    "Admin API — [Authorize(Roles=\"Admin\")].",
    "საკუთარი თავის წაშლა დაბლოკილია.",
    "CORS მხოლოდ ჩვენი origin.",
], 13)
footer(slide, 9)

# 10 AI + REMINDERS
slide = add_slide(prs)
header(slide, "AI + შეხსენებები", "დამატებითი ფუნქციები", "AI ახსნა და email შეხსენება.", 10)
rect(slide, Inches(0.6), Inches(1.8), Inches(5.9), Inches(3.4), WHITE)
text(slide, Inches(0.9), Inches(2.0), Inches(5.3), Inches(0.3), "AI ასისტენტი", 14, True, SAGE)
text(slide, Inches(0.9), Inches(2.45), Inches(5.3), Inches(2.2), "Angular → API → n8n → Gemini\n\nპასუხი ინახება ისტორიაში.\nკრიტიკული კოდი → Telegram.", 13, False, INK)
rect(slide, Inches(6.8), Inches(1.8), Inches(5.9), Inches(3.4), WHITE)
text(slide, Inches(7.1), Inches(2.0), Inches(5.3), Inches(0.3), "შეხსენებები", 14, True, SAGE)
text(slide, Inches(7.1), Inches(2.45), Inches(5.3), Inches(2.2), "თარიღი → BackgroundService\n→ SMTP → NotificationLogs\n\nერთი digest მეილი დღეში.", 13, False, INK)
footer(slide, 10)

# 11 DEMO
slide = add_slide(prs)
header(slide, "დემო", "ეკრანები", "Dashboard · Garage · Reminders.", 11)
for index, (file_name, title) in enumerate([
    ("dashboard-crop.png", "Dashboard"),
    ("garage-crop.png", "Garage"),
    ("reminders-crop.png", "Reminders"),
]):
    left = 0.6 + index * 4.15
    rect(slide, Inches(left), Inches(1.8), Inches(3.85), Inches(3.9), WHITE)
    picture_fit(slide, ASSETS / file_name, Inches(left + 0.15), Inches(1.95), Inches(3.55), Inches(3.2))
    text(slide, Inches(left + 0.2), Inches(5.25), Inches(3.4), Inches(0.3), title, 13, True, INK)
footer(slide, 11)

# 12 TESTS
slide = add_slide(prs)
header(slide, "შედეგი", "ტესტები და ხარისხი", "48 ტესტი · Swagger · logging.", 12)
for label, value, note, left in [
    ("BACKEND", "29", "passed", 0.6),
    ("FRONTEND", "19", "passed", 3.7),
    ("API", "32", "endpoint", 6.8),
    ("MODELS", "15", "მოდელი", 9.9),
]:
    rect(slide, Inches(left), Inches(1.8), Inches(2.8), Inches(1.3), WHITE)
    text(slide, Inches(left + 0.2), Inches(1.95), Inches(2.4), Inches(0.2), label, 8, True, MUTED)
    text(slide, Inches(left + 0.2), Inches(2.2), Inches(2.4), Inches(0.5), value, 24, True, SAGE)
    text(slide, Inches(left + 0.2), Inches(2.8), Inches(2.4), Inches(0.2), note, 9, False, MUTED)
bullets(slide, Inches(0.6), Inches(3.6), Inches(12), Inches(2.4), [
    "Swagger: /swagger — ყველა endpoint.",
    "HTTP logging + auth/reminder ლოგები.",
    "C4, README, სრული დოკუმენტაცია.",
], 14, 12)
footer(slide, 12)

# 13 THANK YOU
slide = add_slide(prs)
header(slide, "დასკვნა", "მადლობა", None, 13)
text(slide, Inches(0.6), Inches(1.6), Inches(10.5), Inches(0.9), "OBD2 Web", 46, True, INK)
text(slide, Inches(0.6), Inches(2.55), Inches(8.5), Inches(0.5), "მანქანის დიაგნოსტიკა — მარტივად.", 20, False, SAGE)
text(slide, Inches(0.6), Inches(4.0), Inches(8.0), Inches(0.5), "კითხვები?", 26, True, INK)
text(slide, Inches(0.6), Inches(5.6), Inches(8.0), Inches(0.3), "GitHub: Laziii54", 12, True, SAGE)
text(slide, Inches(0.6), Inches(6.1), Inches(8.0), Inches(0.3), "ზურაბ ლაზაშვილი · 2026", 10, False, MUTED)
footer(slide, 13)

prs.save(OUT)
print(f"saved {OUT} with {len(prs.slides)} slides")
