from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(r"C:\Users\zukal\OneDrive\Desktop\OBD2 WEB\docs\report\assets")
BASE.mkdir(parents=True, exist_ok=True)

BG = (247, 245, 240)
INK = (32, 37, 31)
MUTED = (114, 119, 110)
SAGE = (63, 93, 78)
SAGE_SOFT = (233, 239, 233)
WHITE = (255, 255, 255)
LINE = (228, 224, 215)

FONT = "C:/Windows/Fonts/Sylfaen.ttf"
FONT_BOLD = "C:/Windows/Fonts/Sylfaen.ttf"


def f(size):
    return ImageFont.truetype(FONT, size)


def fb(size):
    return ImageFont.truetype(FONT_BOLD, size)


def center_text(draw, box, value, font, fill=INK):
    left, top, right, bottom = box
    bbox = draw.textbbox((0, 0), value, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    draw.text(
        (left + (right - left - width) / 2, top + (bottom - top - height) / 2 - bbox[1]),
        value,
        font=font,
        fill=fill,
    )


# ------------------------------------------------------------------ connector
image = Image.new("RGB", (1600, 900), BG)
draw = ImageDraw.Draw(image)
draw.rounded_rectangle((80, 120, 790, 800), radius=36, fill=(45, 53, 48))
draw.text((120, 165), "OBD-II  ·  16-PIN", font=fb(30), fill=WHITE)
draw.text((120, 210), "Diagnostic connector", font=f(20), fill=SAGE_SOFT)

for row in range(2):
    for column in range(8):
        x = 145 + column * 76
        y = 330 + row * 150
        draw.ellipse((x, y, x + 38, y + 38), fill=SAGE_SOFT)
        draw.ellipse((x + 9, y + 9, x + 29, y + 29), fill=(45, 53, 48))

draw.text((120, 650), "4/5 GND   ·   6 CAN-H   ·   14 CAN-L   ·   16 +12V", font=f(18), fill=SAGE_SOFT)

labels = [
    ("16 PIN", "სტანდარტული დიაგნოსტიკური პორტი"),
    ("CAN 500 kbps", "6 / 14 პინები — მონაცემთა გაცვლა"),
    ("K-line", "ძველი მოდელების პროტოკოლი"),
]
for index, (title, note) in enumerate(labels):
    top = 200 + index * 185
    draw.rounded_rectangle((900, top, 1520, top + 145), radius=18, fill=WHITE, outline=LINE, width=2)
    draw.text((935, top + 25), title, font=fb(28), fill=INK)
    draw.text((935, top + 75), note, font=f(19), fill=MUTED)

image.save(BASE / "obd-connector.png")

# ------------------------------------------------------------------ flow
image = Image.new("RGB", (1800, 720), BG)
draw = ImageDraw.Draw(image)
draw.text((70, 45), "OBD360 — კავშირის ნაკადი", font=fb(38), fill=INK)
draw.text((70, 105), "ECU -> OBD-II პორტი -> ELM327 -> Web Bluetooth -> OBD360", font=f(23), fill=MUTED)

boxes = [
    ("ECU", "ძრავის მართვის\nბლოკი", SAGE, WHITE),
    ("OBD-II", "16-pin\nპორტი", WHITE, INK),
    ("ELM327", "BLE\nადაპტერი", WHITE, INK),
    ("Web Bluetooth", "ბრაუზერი\nChrome / Edge", (232, 238, 240), INK),
    ("OBD360", "Angular\nაპლიკაცია", SAGE_SOFT, SAGE),
]
positions = [70, 410, 750, 1090, 1430]
for (title, subtitle, fill, color), left in zip(boxes, positions):
    draw.rounded_rectangle((left, 250, left + 280, 455), radius=20, fill=fill, outline=LINE, width=2)
    draw.text((left + 24, 280), title, font=fb(25), fill=color)
    draw.text((left + 24, 335), subtitle, font=f(19), fill=MUTED if fill != SAGE else SAGE_SOFT)

for left in [355, 695, 1035, 1375]:
    draw.polygon([(left, 340), (left + 40, 352), (left, 364)], fill=SAGE)

draw.rounded_rectangle((70, 535, 1715, 640), radius=16, fill=(31, 41, 36))
draw.text((100, 558), "ATZ  ->  ATE0  ->  ATL0  ->  ATS0  ->  ATH0  ->  ATSP0  ->  0100", font=f(24), fill=(232, 239, 233))
draw.text((100, 600), "03 / 07 / 0A  ->  DTC   ·   0902  ->  VIN   ·   04  ->  clear", font=f(19), fill=SAGE_SOFT)

image.save(BASE / "obd-flow.png")

# ------------------------------------------------------------------ data model core
image = Image.new("RGB", (1800, 850), BG)
draw = ImageDraw.Draw(image)
draw.text((70, 45), "მონაცემთა მოდელის ბირთვი", font=fb(38), fill=INK)
draw.text((70, 105), "15 მოდელი · 21 ცხრილი · EF Core migrations", font=f(22), fill=MUTED)

entities = [
    ("ApplicationUser", "Id · Email · DisplayName", 100, 230, 390, 320),
    ("Vehicle", "Make · Model · VIN", 700, 230, 990, 320),
    ("ScanSession", "StartedAt · EndedAt", 1300, 230, 1670, 320),
    ("MaintenanceReminder", "DueAtDate · Status", 100, 580, 450, 680),
    ("DtcRecord", "Code · Severity", 700, 580, 990, 680),
    ("DtcCatalogEntry", "Code · Description", 1300, 580, 1670, 680),
]
for title, note, left, top, right, bottom in entities:
    draw.rounded_rectangle((left, top, right, bottom), radius=16, fill=WHITE, outline=LINE, width=2)
    draw.text((left + 18, top + 18), title, font=fb(20), fill=INK)
    draw.text((left + 18, top + 55), note, font=f(16), fill=MUTED)


def connector(start, end):
    draw.line([start, end], fill=SAGE, width=4)
    draw.ellipse((end[0] - 6, end[1] - 6, end[0] + 6, end[1] + 6), fill=SAGE)


connector((490, 275), (700, 275))
connector((990, 275), (1300, 275))
connector((295, 320), (295, 580))
connector((845, 320), (845, 580))
connector((1450, 320), (1450, 580))
connector((450, 630), (700, 630))

image.save(BASE / "data-model.png")

print("assets written")
