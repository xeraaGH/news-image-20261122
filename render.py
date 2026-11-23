#!/usr/bin/env python3
"""Render the front page for Sunday 22 November 2026.

Draws ONE 1024x1024 PNG newspaper front page with PIL only, from the
verified story list below. No network, no randomness, no timestamps:
the same input always produces the same bytes.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 244, 234)
INK = (17, 17, 17)
RED = (179, 32, 44)
NAVY = (18, 57, 91)
GREY = (90, 90, 86)
HAIR = (150, 145, 130)
CARD = (255, 253, 246)

F = "/usr/share/fonts/truetype/liberation/"
SERIF_B = F + "LiberationSerif-Bold.ttf"
SERIF = F + "LiberationSerif-Regular.ttf"
SANS_B = F + "LiberationSans-Bold.ttf"
SANS = F + "LiberationSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_h(draw, lines, fnt, lh):
    return len(lines) * lh


# ---------------------------------------------------------------- stories
LEAD_HEAD = "COP31 ENDS WITH NO DEAL"
LEAD_SUB = ("The EU rejects a draft that never mentions fossil fuels, and the "
            "longest climate summit in history closes in failure.")
LEAD_ITEMS = [
    ('"Deeply disappointed"',
     "UN chief Antonio Guterres blames fossil-fuel interests for blocking action."),
    ("Small wins survive",
     "A just-transition deal is agreed; 80+ nations back 35% electricity by 2035."),
]

# (section title, band colour, stories[(headline, summary)])
SECTIONS = [
    ("MIDDLE EAST", (122, 30, 30), [
        ("IRAN SAYS IT HIT A US F-16",
         "Tehran claims a missile exploded near the jet over the Gulf; Washington denies any hit."),
        ("IRAN STRIKES BAHRAIN",
         "An industrial site is hit and two people hurt; Guards claim two US Patriot radars destroyed."),
        ("TANKERS ABLAZE NEAR HORMUZ",
         "Six tankers attacked in a week; shipping through the strait is 65% below pre-war levels."),
        ('IRAN SHOWS OFF "MISSILE CITY"',
         "State TV airs an underground base; a new launcher fires two missiles at once."),
        ("IRAN POWER CUTS FROM SUNDAY",
         "Rolling blackouts begin as war damage deepens the energy crunch."),
        ("WEST BANK ARSON WAVE",
         'Settlers burn 12 Palestinian vehicles; an opposition leader calls it "Jewish terrorism".'),
        ("GAZA TOLL SINCE CEASEFIRE: 1,671",
         "Nine more Palestinians killed in 48 hours, the health ministry says."),
    ]),
    ("EUROPE & UKRAINE", (18, 57, 91), [
        ("DRONE KILLS 3 NEAR KYIV",
         "A five-storey block in Dymer collapses; 11 people are feared trapped in the rubble."),
        ("186 DRONES IN ONE NIGHT",
         "Ukraine says 161 were shot down; 30 people are hurt in attacks across the country."),
        ("RUSSIAN SHIP ABLAZE IN BALTIC",
         "The Sparta II is hit by drones; its crew of 16 is evacuated as Finland points at Ukraine."),
        ('NO BAN ON "KILLER ROBOTS"',
         "Geneva talks fail to agree binding rules for autonomous weapons."),
        ("UN TROOPS HAND OVER IN LEBANON",
         "UNIFIL starts leaving its southern posts to the Lebanese army."),
        ("LISBON MARCHES ON LIVING COSTS",
         "Thousands protest as rising prices fuel anger across Portugal."),
        ("LONDON MARCHES FOR AI RULES",
         "Protesters demand tighter curbs on artificial intelligence."),
    ]),
    ("ASIA-PACIFIC", (0, 96, 68), [
        ("KOREA MINISTER QUITS OVER AI CHEATING",
         "The education chief resigns after exam chaos in the Suneung university test."),
        ("BANGLADESH UNREST TURNS DEADLY",
         "Four killed as Hasina supporters protest her planned return; troops deploy."),
        ("NEPAL PM IN DELHI",
         "Balendra Shah makes his first India visit since taking office; meets Modi on Monday."),
        ("INDIA: MORE META PROTESTS WARNED",
         "An opposition youth wing threatens fresh action after clashes with police."),
        ("EU-INDONESIA TRADE DEAL",
         "Ten years of talks end; 98.5% of tariffs go in a deal for 280 million people."),
        ("24 BODIES AFTER JAVA FACTORY FIRE",
         "Rescuers recover victims of a candy-factory blaze in Cikande; dozens missing."),
    ]),
    ("AFRICA", (146, 90, 0), [
        ("DRONES HIT KHARTOUM HOMES",
         "Strikes damage a UN building and kill children; Sudan's army blames Ethiopia."),
        ("NIGERIA BOAT DISASTER: 24 DEAD",
         "A boat carrying funeral mourners capsizes; the death toll keeps rising."),
        ("AFRICA AT COP31: LEFT WAITING",
         'Ghana, for the African Group, says climate finance got "a single generic sentence".'),
    ]),
    ("AMERICAS", (90, 30, 110), [
        ('"EL CHAPO ISIDRO" CAPTURED',
         "FBI Top 10 fugitive seized in Sinaloa; 11 killed as cartel gunmen fight troops."),
        ('TRUMP VOWS "PERMANENT" IRAN DEAL',
         "He says no future president should let Tehran get a nuclear weapon."),
        ("US HEALTH ALERT",
         "A bird-flu case is confirmed in a dairy worker as respiratory illness surges."),
        ("US AND CHINA: HUMANS KEEP MILITARY AI",
         "Leaders agree people must stay in command of AI weapons."),
        ("CANADA SEES NO US MILITARY RIFT",
         "The defence minister dismisses a reported memo on curbs to cooperation."),
    ]),
    ("SCIENCE & SPORT", (0, 90, 110), [
        ('RIEMANN PROOF "CHECKS OUT"',
         "Independent groups verify an AI-assisted proof; mathematicians urge caution."),
        ("BEPICOLOMBO REACHES MERCURY",
         "ESA confirms orbit after an eight-year trip; a software glitch cut the burn short."),
        ("LIVERPOOL 4-0 MAN UTD",
         "Pochettino's reign starts in nightmare at Anfield; Yoro sees red after 8 minutes."),
        ("HULL 2-0 BRIGHTON",
         "McBurnie scores twice in stoppage time at the MKM Stadium."),
        ("BARCELONA 3-2 VILLARREAL",
         "Barca edge a five-goal thriller in La Liga."),
        ("JUVENTUS WIN 4-0",
         "Juve cruise in Serie A on a day of goals across Europe."),
    ]),
]

NUMBERS = [
    ("186", "drones fired at Ukraine in a single night"),
    ("24", "killed as a boat capsizes in Nigeria"),
    ("98.5%", "of tariffs cut by the EU-Indonesia deal"),
    ("4-0", "Liverpool's win over Manchester Utd"),
]


def draw_star(d, cx, cy, r, colour):
    import math
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=colour)


def section_icon(d, idx, x, y, colour):
    """Small white pictogram in the section title bar."""
    cx, cy = x + 14, y + 14
    white = (255, 255, 255)
    if idx == 0:  # crescent
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=white)
        d.ellipse([cx - 4, cy - 8, cx + 11, cy + 8], fill=colour)
    elif idx == 1:  # star
        draw_star(d, cx, cy, 9, white)
    elif idx == 2:  # sun
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=white)
        for a in range(0, 360, 45):
            import math
            r1, r2 = 9, 12
            x1 = cx + r1 * math.cos(math.radians(a))
            y1 = cy + r1 * math.sin(math.radians(a))
            x2 = cx + r2 * math.cos(math.radians(a))
            y2 = cy + r2 * math.sin(math.radians(a))
            d.line([x1, y1, x2, y2], fill=white, width=2)
    elif idx == 3:  # mountain
        d.polygon([(cx - 10, cy + 7), (cx, cy - 8), (cx + 10, cy + 7)], fill=white)
        d.polygon([(cx - 2, cy - 4), (cx + 2, cy - 4), (cx, cy)], fill=colour)
    elif idx == 4:  # globe
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], outline=white, width=2)
        d.ellipse([cx - 3, cy - 8, cx + 3, cy + 8], outline=white, width=1)
        d.line([cx - 8, cy, cx + 8, cy], fill=white, width=1)
    else:  # ball
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], outline=white, width=2)
        d.polygon([(cx, cy - 4), (cx + 4, cy - 1), (cx + 2, cy + 4),
                   (cx - 2, cy + 4), (cx - 4, cy - 1)], fill=white)


def draw_section(d, idx, title, colour, stories, x, y, w, h, hf, sf):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=(120, 115, 100), width=1)
    d.rectangle([x, y, x + w, y + 30], fill=colour)
    section_icon(d, idx, x, y, colour)
    d.text((x + 30, y + 7), title, font=font(SANS_B, 14), fill=(255, 255, 255))
    n = len(stories)
    d.text((x + w - 26, y + 8), str(n), font=font(SANS_B, 13), fill=(255, 255, 255))
    inner_w = w - 20
    # auto-fit: try progressively smaller sizes until the stories fit
    combos = [(13, 11, 16, 14, 10), (12, 10, 15, 13, 8),
              (11, 10, 14, 12, 6), (11, 9, 14, 12, 5)]
    avail = h - 30 - 8
    for hl, sl, lh_h, lh_s, pad in combos:
        heights = []
        for head, summ in stories:
            hlines = wrap(d, head, font(SANS_B, hl), inner_w)
            slines = wrap(d, summ, font(SANS, sl), inner_w)
            heights.append(len(hlines) * lh_h + len(slines) * lh_s + pad)
        if sum(heights) + 6 <= avail:
            break
    total = sum(heights) + 6
    cy = y + 34
    for i, (head, summ) in enumerate(stories):
        hlines = wrap(d, head, font(SANS_B, hl), inner_w)
        ty = cy
        for ln in hlines:
            d.text((x + 10, ty), ln, font=font(SANS_B, hl), fill=INK)
            ty += lh_h
        slines = wrap(d, summ, font(SANS, sl), inner_w)
        for ln in slines:
            d.text((x + 10, ty), ln, font=font(SANS, sl), fill=(40, 40, 38))
            ty += lh_s
        cy += heights[i]
        if i < len(stories) - 1:
            d.line([x + 10, cy - 5, x + w - 10, cy - 5], fill=(220, 215, 200), width=1)
    return total


def draw_numbers(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 57, 91))
    d.text((x + 12, y + 8), "BY THE NUMBERS", font=font(SANS_B, 13),
           fill=(255, 255, 255))
    d.line([x + 12, y + 30, x + w - 12, y + 30], fill=(120, 160, 200), width=1)
    cy = y + 38
    for big, small in NUMBERS:
        d.text((x + 12, cy), big, font=font(SERIF_B, 23), fill=(255, 210, 90))
        bw = d.textlength(big, font=font(SERIF_B, 23))
        lines = wrap(d, small, font(SANS, 11), w - 24 - bw - 10)
        ty = cy + 5
        for ln in lines:
            d.text((x + 12 + bw + 10, ty), ln, font=font(SANS, 11),
                   fill=(235, 235, 230))
            ty += 13
        cy += 29
    return cy


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # ---- masthead
    d.rectangle([0, 0, W, 8], fill=NAVY)
    d.text((16, 18), "ONE DAY  •  ONE PAGE  •  THE WHOLE WORLD",
           font=font(SANS_B, 11), fill=GREY)
    d.text((W - 16 - d.textlength("No. 326  •  SUNDAY EDITION", font=font(SANS_B, 11)),
            18), "No. 326  •  SUNDAY EDITION", font=font(SANS_B, 11), fill=GREY)
    title = "THE WORLD IN ONE DAY"
    tf = font(SERIF_B, 56)
    d.text(((W - d.textlength(title, font=tf)) / 2, 30), title,
           font=tf, fill=INK)
    date = "SUNDAY, 22 NOVEMBER 2026"
    df = font(SANS_B, 23)
    d.text(((W - d.textlength(date, font=df)) / 2, 94), date,
           font=df, fill=RED)
    d.line([16, 120, W - 16, 120], fill=INK, width=2)
    d.line([16, 124, W - 16, 124], fill=INK, width=1)

    # ---- lead story: COP31
    lx, ly, lw, lh = 16, 132, W - 32, 132
    d.rectangle([lx, ly, lx + lw, ly + lh], fill=CARD,
                outline=(120, 115, 100), width=1)
    d.text((lx + 14, ly + 8), "CLIMATE  •  ANTALYA, TURKIYE",
           font=font(SANS_B, 13), fill=RED)
    d.text((lx + 14, ly + 28), LEAD_HEAD, font=font(SERIF_B, 40), fill=INK)
    sub_lines = wrap(d, LEAD_SUB, font(SANS, 14), 640)
    ty = ly + 76
    for ln in sub_lines:
        d.text((lx + 14, ty), ln, font=font(SANS, 14), fill=(40, 40, 38))
        ty += 18
    # right-hand mini items
    ix = lx + 668
    d.line([ix - 10, ly + 10, ix - 10, ly + lh - 10], fill=HAIR, width=1)
    ty = ly + 10
    for head, summ in LEAD_ITEMS:
        d.text((ix, ty), head, font=font(SANS_B, 12), fill=INK)
        ty += 16
        for ln in wrap(d, summ, font(SANS, 11), lw - 668 - 28):
            d.text((ix, ty), ln, font=font(SANS, 11), fill=(40, 40, 38))
            ty += 14
        ty += 8
    # ---- section grid: 3 cols x 2 rows
    cols_x = [16, 352, 688]
    col_w = 320
    rows_y = [276, 640]
    row_h = [352, 352]
    for r, y in enumerate(rows_y):
        for c, x in enumerate(cols_x):
            idx = r * 3 + c
            title, colour, stories = SECTIONS[idx]
            draw_section(d, idx, title, colour, stories, x, y, col_w,
                         row_h[r], 13, 11)
    # numbers panel inside the Africa box (row 2, col 1), below its 3 stories
    ax, ay = cols_x[0], rows_y[1]
    panel_y = ay + 196
    draw_numbers(d, ax + 1, panel_y, col_w - 2, ay + row_h[1] - panel_y - 1)

    # ---- footer
    d.line([16, 1006, W - 16, 1006], fill=INK, width=1)
    foot = ("Every story happened, or was first reported, on Sunday 22 November 2026  •  "
            "Sources: Reuters, BBC, AP, UN News, Al Jazeera, The Guardian, Yonhap, AFP")
    ff = font(SANS, 10)
    d.text(((W - d.textlength(foot, font=ff)) / 2, 1011), foot,
           font=ff, fill=GREY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
