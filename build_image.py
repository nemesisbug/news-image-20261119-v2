#!/usr/bin/env python3
"""Render 'One Day, Everywhere' - news-image-20261119 v2 renewal.

Draws a dense one-page newspaper front page summing up Thursday
19 November 2026, using only the Python standard library + PIL.
All text, layout and the world map (coarse lon/lat outlines authored
here from general knowledge) are produced by this script. Deterministic:
same input always yields the same PNG bytes.
"""
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

INK = (18, 18, 18)
RED = (178, 24, 24)
DARKRED = (140, 16, 16)
PAPER = (252, 250, 244)
GREY = (90, 90, 88)
LIGHT = (238, 234, 226)
MIDLINE = (200, 194, 182)
NAVY = (24, 48, 84)
TEAL = (14, 90, 86)
GOLD = (176, 128, 20)
BLUE = (30, 80, 160)


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, width):
    """Wrap text to fit pixel width; returns list of lines."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        cur = ""
        for w in words:
            trial = (cur + " " + w).strip()
            if draw.textlength(trial, font=font) <= width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, font, width, fill=INK, leading=None):
    lh = leading or int(font.size * 1.22)
    lines = wrap(draw, text, font, width)
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def tag_chip(draw, x, y, tag):
    """Small REPORTED / CLAIM / FORECAST chip. Returns width used."""
    cols = {"REPORTED": (20, 110, 60), "CLAIM": (176, 110, 10),
            "FORECAST": (120, 70, 160)}
    c = cols.get(tag, GREY)
    f = F(SANS_B, 8)
    w = int(draw.textlength(tag, font=f)) + 8
    draw.rounded_rectangle([x, y, x + w, y + 11], radius=2, fill=c)
    draw.text((x + 4, y + 1), tag, font=f, fill=(255, 255, 255))
    return w


# ---------------------------------------------------------------- map data
# Coarse continent outlines (lon, lat), authored from general knowledge.
CONTINENTS = {
    "N America": [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69),
                  (-85, 66), (-80, 73), (-65, 62), (-55, 52), (-60, 47),
                  (-70, 42), (-75, 35), (-80, 26), (-85, 20), (-90, 15),
                  (-95, 18), (-105, 20), (-115, 28), (-125, 40), (-125, 49),
                  (-140, 60), (-155, 58), (-165, 60)],
    "S America": [(-78, 8), (-72, 11), (-60, 8), (-52, 5), (-50, 0),
                  (-42, -5), (-35, -8), (-40, -20), (-48, -28), (-55, -35),
                  (-62, -41), (-68, -50), (-70, -54), (-73, -44), (-73, -30),
                  (-70, -18), (-77, -12), (-80, -4), (-80, 2)],
    "Africa": [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31),
               (35, 28), (43, 12), (51, 11), (48, -2), (40, -10), (35, -18),
               (32, -26), (26, -34), (18, -34), (14, -22), (12, -8),
               (9, 4), (-8, 5)],
    "Europe": [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 51), (5, 53),
               (8, 57), (10, 59), (18, 56), (21, 55), (24, 58), (30, 60),
               (28, 70), (40, 68), (45, 66), (40, 55), (35, 50), (28, 45),
               (23, 40), (19, 42), (12, 44), (8, 44), (3, 42), (-1, 38)],
    "Asia": [(40, 68), (60, 70), (80, 73), (100, 77), (120, 73), (140, 72),
             (160, 70), (178, 66), (170, 60), (158, 52), (142, 50),
             (140, 40), (135, 34), (127, 35), (122, 31), (120, 23),
             (110, 20), (105, 10), (100, 8), (95, 15), (90, 22), (80, 15),
             (75, 8), (70, 22), (60, 25), (55, 26), (50, 29), (43, 12),
             (40, 20), (35, 28), (30, 36), (28, 41), (35, 45), (40, 50),
             (45, 55), (50, 60), (45, 66)],
    "Australia": [(114, -22), (122, -14), (132, -12), (137, -12), (142, -11),
                  (146, -19), (150, -23), (153, -27), (150, -37), (140, -38),
                  (135, -35), (130, -32), (124, -33), (115, -35), (113, -26)],
}


def project(lon, lat, x0, y0, w, h):
    # equirectangular over lon -170..190, lat -58..78
    x = x0 + (lon + 170.0) / 360.0 * w
    y = y0 + (78.0 - lat) / 136.0 * h
    return (x, y)


def draw_map(draw, x0, y0, w, h, pins):
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(214, 230, 240),
                   outline=INK, width=2)
    # graticule
    for lon in range(-150, 181, 30):
        x = x0 + (lon + 170.0) / 360.0 * w
        draw.line([(x, y0), (x, y0 + h)], fill=(190, 208, 220), width=1)
    for lat in range(-40, 61, 20):
        y = y0 + (78.0 - lat) / 136.0 * h
        draw.line([(x0, y), (x0 + w, y)], fill=(190, 208, 220), width=1)
    for name, pts in CONTINENTS.items():
        poly = [project(lo, la, x0, y0, w, h) for lo, la in pts]
        draw.polygon(poly, fill=(240, 236, 222), outline=(70, 70, 66))
    # pins: (lon, lat, number, label, label_pos) label_pos: 'below' default
    fnum = F(SANS_B, 11)
    flab = F(SANS_B, 9)
    for pin in pins:
        lon, lat, num, label = pin[0], pin[1], pin[2], pin[3]
        pos = pin[4] if len(pin) > 4 else "below"
        px, py = project(lon, lat, x0, y0, w, h)
        r = 10
        draw.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                     outline=(255, 255, 255), width=2)
        tw = draw.textlength(str(num), font=fnum)
        draw.text((px - tw / 2, py - 8), str(num), font=fnum,
                  fill=(255, 255, 255))
        if label:
            lw = draw.textlength(label, font=flab)
            lx = min(max(px - lw / 2, x0 + 2), x0 + w - lw - 2)
            ly = py + r + 2 if pos == "below" else py - r - 12
            draw.rectangle([lx - 2, ly - 1, lx + lw + 2, ly + 10],
                           fill=(255, 255, 255))
            draw.text((lx, ly), label, font=flab, fill=INK)


# ---------------------------------------------------------------- heroes art
def art_shenzhen(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(250, 220, 180))
    d.ellipse([x + w - 62, y + 6, x + w - 14, y + 54], fill=(214, 60, 40))
    # skyline
    base = y + h
    for i, (bx, bw, bh) in enumerate([(0, 34, 40), (38, 26, 54), (68, 40, 32),
                                     (112, 30, 58), (146, 34, 42), (184, 30, 50),
                                     (218, 36, 36), (258, 30, 56)]):
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=NAVY)
        for wy in range(base - bh + 6, base - 4, 12):
            for wx in range(x + bx + 5, x + bx + bw - 4, 10):
                d.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 214, 120))
    # three leaders as a row of heads above the table line
    d.rectangle([x, y + h - 8, x + w, y + h], fill=DARKRED)
    for cx, col in [(x + 95, RED), (x + w // 2, (255, 255, 255)),
                    (x + w - 95, TEAL)]:
        d.ellipse([cx - 11, y + h - 26, cx + 11, y + h - 8], fill=col,
                  outline=INK)


def art_icj(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 228, 238))
    # courthouse
    cx = x + w // 2
    d.polygon([(cx - 95, y + 30), (cx + 95, y + 30), (cx, y + 6)],
              fill=DARKRED)
    d.rectangle([x + 40, y + 30, x + w - 40, y + 36], fill=INK)
    for i in range(5):
        px = x + 52 + i * 52
        d.rectangle([px, y + 36, px + 14, y + h - 6], fill=(245, 245, 240),
                    outline=INK)
    d.rectangle([x + 40, y + h - 6, x + w - 40, y + h - 2], fill=INK)


def art_anthropic(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 28, 44))
    # grid
    for gy in range(y + 12, y + h - 6, 16):
        d.line([(x + 8, gy), (x + w - 8, gy)], fill=(50, 66, 96), width=1)
    # rising chart line, kept below the title text
    pts = [(x + 12, y + h - 16), (x + 60, y + h - 24), (x + 110, y + h - 20),
           (x + 160, y + h - 34), (x + 210, y + h - 30), (x + 260, y + h - 48),
           (x + w - 14, y + 34)]
    d.line(pts, fill=(90, 220, 120), width=4, joint="curve")
    for px, py in pts:
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(90, 220, 120))
    d.text((x + 12, y + 6), "ANT  $97.17  +17%", font=F(SANS_B, 15),
           fill=(255, 255, 255))


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 14
    CW = W - 2 * M  # 996

    # ---- masthead
    d.text((M, 6), "THE WORLD IN ONE DAY", font=F(SERIF, 46), fill=INK)
    d.text((M, 56), "DAY 323 OF 2026  \u00b7  ONE-PAGE EDITION  \u00b7  EVERY STORY BELOW HAPPENED ON THIS DAY",
           font=F(SANS_B, 11), fill=GREY)
    # date box
    bx, by, bw, bh = W - M - 208, 4, 208, 64
    d.rectangle([bx, by, bx + bw, by + bh], fill=RED)
    d.text((bx + 10, by + 4), "THURSDAY", font=F(SANS_B, 15), fill=(255, 255, 255))
    d.text((bx + 10, by + 22), "19 NOVEMBER 2026", font=F(SERIF, 21), fill=(255, 255, 255))
    d.text((bx + 10, by + 48), "THE DAY IN FULL", font=F(SANS_B, 9), fill=(255, 220, 200))
    d.line([(M, 74), (W - M, 74)], fill=INK, width=2)

    # ---- red subhead: 3 biggest stories
    y = 80
    d.text((M, y), "SHENZHEN: THREE LEADERS, ONE PEACE DECLARATION   \u00b7   THE HAGUE: MYANMAR GUILTY OF GENOCIDE   \u00b7   NEW YORK: ANTHROPIC SOARS ON DEBUT",
           font=F(SANS_B, 12), fill=RED)

    # ---- banner
    y = 102
    d.rectangle([M, y, W - M, y + 22], fill=INK)
    d.text((M + 8, y + 4), "42 STORIES  \u00b7  ONE DAY  \u00b7  EVERY CONTINENT",
           font=F(SANS_B, 13), fill=(255, 255, 255))
    d.text((W - M - 8 - d.textlength("ASIA-PACIFIC 14  \u00b7  EUROPE 7  \u00b7  MIDDLE EAST 8  \u00b7  AMERICAS 8  \u00b7  AFRICA 2  \u00b7  WORLD 3", font=F(SANS_B, 11)), y + 5),
           "ASIA-PACIFIC 14  \u00b7  EUROPE 7  \u00b7  MIDDLE EAST 8  \u00b7  AMERICAS 8  \u00b7  AFRICA 2  \u00b7  WORLD 3",
           font=F(SANS_B, 11), fill=(255, 214, 120))

    # ---- stat strip
    y = 130
    stats = [("3", "LEADERS AT ONE TABLE"),
             ("9\u20136", "WORLD COURT VOTE"),
             ("$81.3bn", "ANTHROPIC IPO, RECORD"),
             ("551,864", "KOREA EXAM TAKERS"),
             ("109\u20130", "DENMARK ARCTIC VOTE"),
             ("\u22121,101", "DOW POINTS, THURSDAY")]
    sw = CW / 6
    for i, (num, lab) in enumerate(stats):
        x = M + i * sw
        d.rectangle([x + 2, y, x + sw - 2, y + 40], fill=LIGHT, outline=MIDLINE)
        nf = F(SERIF, 21)
        tw = d.textlength(num, font=nf)
        d.text((x + sw / 2 - tw / 2, y + 2), num, font=nf, fill=RED)
        lf = F(SANS_B, 8)
        lw = d.textlength(lab, font=lf)
        d.text((x + sw / 2 - lw / 2, y + 27), lab, font=lf, fill=INK)
    y = 176

    # ---- timeline
    d.text((M, y), "THE DAY BY HOURS", font=F(SANS_B, 12), fill=INK)
    d.line([(M + 150, y + 8), (W - M, y + 8)], fill=MIDLINE, width=1)
    y += 18
    hours = [("00:00", "AUCKLAND", "GTA VI unlocks"),
             ("08:40", "SEOUL", "Exam begins"),
             ("10:00", "THE HAGUE", "Ruling read"),
             ("13:10", "SEOUL", "Flights pause"),
             ("P.M.", "SHENZHEN", "Declaration"),
             ("16:00", "NEW YORK", "Dow \u22121,101")]
    hw = CW / 6
    for i, (t, place, txt) in enumerate(hours):
        x = M + i * hw
        d.ellipse([x + 2, y + 2, x + 12, y + 12], fill=RED)
        d.text((x + 16, y), t, font=F(SANS_B, 11), fill=RED)
        yy = draw_wrapped(d, x + 2, y + 15, place + " \u2014 " + txt,
                          F(SANS, 10), hw - 10, leading=12)
    y = 228

    # ---- heroes
    heroes = [
        (1, "SHENZHEN \u2014 DIPLOMACY", "Three leaders, one table, a first",
         "Trump, Xi and Putin meet for the first time as a trio at APEC in "
         "Shenzhen and sign a four-point declaration: no nuclear war, "
         "nuclear-risk talks, more oil, UN reform.",
         "REPORTED", art_shenzhen),
        (2, "THE HAGUE \u2014 JUSTICE", "Myanmar guilty of genocide",
         "The World Court rules 9\u20136 that Myanmar committed genocide in "
         "2017 \u2014 the first state ever held liable. About 10,000 killed; "
         "700,000+ fled; return ordered.",
         "REPORTED", art_icj),
        (3, "NEW YORK \u2014 MARKETS", "Anthropic's $81bn debut defies the sell-off",
         "The AI firm lists on Nasdaq as ANT: priced at $83, opens at "
         "$111.50, closes at $97.17, up 17% \u2014 the biggest IPO on record. "
         "The wider market falls hard the same day.",
         "REPORTED", art_anthropic),
    ]
    hcol = CW / 3
    hy = y
    for i, (num, kick, head, body, tag, art) in enumerate(heroes):
        x = int(M + i * hcol)
        wcol = int(hcol) - (8 if i < 2 else 0)
        d.rectangle([x, hy, x + wcol, hy + 136], outline=INK, width=1)
        d.rectangle([x, hy, x + wcol, hy + 20], fill=INK)
        d.text((x + 6, hy + 3), f"{num}  {kick}", font=F(SANS_B, 11),
               fill=(255, 255, 255))
        tag_chip(d, x + wcol - 66, hy + 4, tag)
        art(d, x + 1, hy + 21, wcol - 2, 54)
        yy = draw_wrapped(d, x + 6, hy + 79, head, F(SERIF, 15), wcol - 12,
                          leading=17)
        draw_wrapped(d, x + 6, yy + 2, body, F(SANS, 10), wcol - 12, leading=11.5)
    y = hy + 142

    # ---- secondary cards 4-15
    d.text((M, y), "MORE FROM THE DAY", font=F(SANS_B, 12), fill=INK)
    d.line([(M + 150, y + 8), (W - M, y + 8)], fill=MIDLINE, width=1)
    y += 18
    cards = [
        (4, "LOS SANTOS \u2014 GAMES", "GTA VI is out, 13 years on",
         "Rockstar's sequel launches at midnight, country by country, on PS5 "
         "and Xbox Series X|S. Vice City returns; standard edition $79.99.",
         "REPORTED"),
        (5, "ANTALYA \u2014 CLIMATE", "COP31 draft drops fossil-fuel exit",
         "Thursday's draft removes the fossil-fuel phase-out language and the "
         "$120bn adaptation target. Talks run to Friday's deadline.",
         "REPORTED"),
        (6, "COPENHAGEN \u2014 ARCTIC", "Denmark backs Greenland deal 109\u20130",
         "Parliament approves the US\u2013Denmark\u2013Greenland security pact, "
         "the last approval needed. Wider US military access follows.",
         "REPORTED"),
        (7, "NEW YORK \u2014 MARKETS", "Wall Street sinks; Dow loses 1,101",
         "Dow closes at 49,097, below 50,000. S&P 500 falls 2.02%, its sixth "
         "straight loss; Nasdaq drops 2.25%. Only one Dow stock rises.",
         "REPORTED"),
        (8, "CANBERRA \u2014 JOBS", "Australia jobless rate hits 4.9%",
         "Employment falls 43,500 in October, the second sharp drop in a row. "
         "Joblessness is at its highest since October 2021.",
         "REPORTED"),
        (9, "SEOUL \u2014 EDUCATION", "A nation hushes for one exam",
         "551,864 students sit the CSAT at 1,312 sites. Offices open late; "
         "flights are retimed 1:10\u20131:35pm for the listening test.",
         "REPORTED"),
        (10, "ODISHA \u2014 WEATHER", "Nearly 300,000 flee Cyclone Akvan",
         "Odisha moves about 299,000 people to shelters as severe cyclone "
         "Akvan nears. Landfall is expected around Friday noon.",
         "FORECAST"),
        (11, "BENTONVILLE \u2014 RETAIL", "Walmart beats and raises outlook",
         "Revenue $188.8bn, up 5.2%; adjusted earnings $0.65 a share. "
         "E-commerce grows 17%; full-year guidance lifted again.",
         "REPORTED"),
        (12, "KERCH \u2014 WAR", "Bridge rail link hit a third time",
         "Ukraine strikes the Crimea bridge for the third time in a week, "
         "halting rail traffic, Kyiv says. Russia confirms an attack.",
         "CLAIM"),
        (13, "GAZA \u2014 WAR", "Israel operates in central Gaza",
         "Israeli forces launch a ground operation near Nuseirat despite the "
         "ceasefire, after evacuation orders to residents.",
         "REPORTED"),
        (14, "THE GULF \u2014 WAR", "Strikes spread across the Gulf",
         "The US hits Qeshm island; Iran answers with strikes on US bases in "
         "Kuwait and Bahrain. A Houthi missile damages a Riyadh tower.",
         "REPORTED"),
        (15, "DHAKA \u2014 UNREST", "Yunus family home set ablaze",
         "Four people are killed amid political unrest in Bangladesh as the "
         "ancestral home of ex-leader Muhammad Yunus is torched.",
         "REPORTED"),
    ]
    ccol = CW / 4
    crow_h = 82
    for idx, (num, kick, head, body, tag) in enumerate(cards):
        r, c = divmod(idx, 4)
        x = M + c * ccol
        cy = y + r * (crow_h + 6)
        wcol = ccol - 6
        d.rectangle([x, cy, x + wcol, cy + crow_h], fill=(255, 255, 255),
                    outline=MIDLINE)
        d.rectangle([x, cy, x + 4, cy + crow_h], fill=RED)
        d.text((x + 10, cy + 3), f"{num}  {kick}", font=F(SANS_B, 9),
               fill=RED)
        tag_chip(d, x + wcol - 62, cy + 3, tag)
        yy = draw_wrapped(d, x + 10, cy + 18, head, F(SERIF, 12.5),
                          wcol - 16, leading=14)
        draw_wrapped(d, x + 10, yy + 1, body, F(SANS, 10), wcol - 16,
                     leading=11.5)
    y = y + 3 * (crow_h + 6) + 4

    # ---- map + briefs
    map_x, map_y, map_w, map_h = M, y, 396, 222
    d.text((map_x, map_y), "WHERE IT HAPPENED", font=F(SANS_B, 12), fill=INK)
    pins = [(122, 22, 1, "Shenzhen"), (5, 52, 2, "The Hague", "above"),
            (-74, 41, 3, "New York"), (127, 37, 9, "Seoul"),
            (86, 20, 10, "Odisha"), (10, 55, 6, "Copenhagen", "below"),
            (33, 36, 5, ""), (151, -34, 8, "Sydney"),
            (90, 23, 15, ""), (47, 25, 14, ""), (34, 31, 13, "")]
    draw_map(d, map_x, map_y + 18, map_w, map_h - 18, pins)

    bx = M + map_w + 12
    bw = W - M - bx
    d.text((bx, map_y), "ALSO ON THURSDAY 19 NOVEMBER \u2014 27 MORE STORIES",
           font=F(SANS_B, 12), fill=INK)
    briefs = [
        (16, "APEC adopts the Shenzhen Outlook on trade, data and AI risks."),
        (17, "Japan's Takaichi meets Putin in Shenzhen; talks to continue."),
        (18, "South Korea's Lee renews his call for dialogue with Pyongyang."),
        (19, "IAEA: North Korea is expanding its Yongbyon enrichment site."),
        (20, "Macron urges allies to reopen Ukraine's NATO membership."),
        (21, "European leaders unite in Berlin behind Ukraine."),
        (22, "Russian strikes kill at least 5 in Ukraine; power cut in 5 regions."),
        (23, "US Senate rejects a war-powers bill to halt the Iran fighting."),
        (24, "Hegseth announces a US\u2013Venezuela military pact in Caracas."),
        (25, "Trump: US will \u201csee what happens\u201d on Iran after 1 Jan 2027."),
        (26, "US security chief dismisses the Iran \u201cdirty bomb\u201d report."),
        (27, "TSMC and Samsung halt some chip shipments to China under US curbs."),
        (28, "Winter rains damage 40,000+ Gaza shelters; 1.7m still displaced."),
        (29, "JPMorgan, Visa, Mastercard confirm a vendor hack; emails exposed."),
        (30, "Rio Tinto pledges $250m for a Papua New Guinea mine fund."),
        (31, "Voyager 1 phones home from a record one light-day away."),
        (32, "Pakistan cuts petrol by Rs3 to Rs322 a litre from today."),
        (33, "Google puts AI chat on its homepage."),
        (34, "Meta's Muse Charm tipped to cost $300."),
        (35, "Fetterman backs Schumer and weighs a 2028 re-election run."),
        (36, "Cornyn blocks a Trump judicial nominee after a clash with Cruz."),
        (37, "Dog rescued from a mineshaft \u2014 its owner's second such rescue."),
        (38, "T\u00fcrkiye proposes a joint Gaza aid initiative at COP31."),
        (39, "USS Theodore Roosevelt redeploys to the Gulf; a third carrier group."),
        (40, "Saudi-led strikes hit Houthi areas; Houthis say 17 killed."),
        (41, "UK publishes real-time economic indicators for 19 November."),
        (42, "ASX set to drop after Wall Street's sell-off; Asia futures slip."),
    ]
    fb = F(SANS, 10)
    fbn = F(SANS_B, 10)
    byy = map_y + 18
    col_w = bw / 2
    for i, (num, txt) in enumerate(briefs):
        col = 0 if i < 14 else 1
        row = i if i < 14 else i - 14
        x = bx + col * col_w
        yy = byy + row * 15
        d.text((x, yy), f"{num}.", font=fbn, fill=RED)
        # truncate at a word boundary with an ellipsis
        t = txt
        while d.textlength(t + "\u2026", font=fb) > col_w - 26 and " " in t:
            t = t.rsplit(" ", 1)[0]
        if len(t) < len(txt):
            t += "\u2026"
        d.text((x + 24, yy), t, font=fb, fill=INK)
    y = map_y + map_h + 14

    # ---- bottom band: verdict / markets / legend
    d.line([(M, y), (W - M, y)], fill=INK, width=2)
    y += 6
    vy = y
    vw = 470
    d.rectangle([M, vy, M + vw, vy + 62], fill=(245, 232, 226), outline=RED)
    d.text((M + 8, vy + 4), "THE VERDICT", font=F(SANS_B, 11), fill=RED)
    draw_wrapped(d, M + 8, vy + 20,
                 "The World Court's 9\u20136 genocide ruling is the day's "
                 "landmark: the first time a state has been held liable. "
                 "Myanmar must allow safe return and pay reparations \u2014 "
                 "but the court cannot enforce it.",
                 F(SANS, 10.5), vw - 16, leading=12)
    mx = M + vw + 10
    mw = 250
    d.rectangle([mx, vy, mx + mw, vy + 62], fill=LIGHT, outline=MIDLINE)
    d.text((mx + 8, vy + 4), "MARKETS & MONEY", font=F(SANS_B, 11), fill=INK)
    mk = [("Dow", "49,097  \u22121,101 (\u22122.2%)"),
          ("S&P 500", "7,176  \u2212148 (\u22122.0%)  6th loss in a row"),
          ("Nasdaq", "23,879  \u2212551 (\u22122.3%)"),
          ("ANT", "$97.17  +17% on debut")]
    myy = vy + 20
    for k, v in mk:
        d.text((mx + 8, myy), k, font=F(SANS_B, 10), fill=INK)
        d.text((mx + 78, myy), v, font=F(SANS, 10), fill=INK)
        myy += 11
    lx = mx + mw + 10
    lw = W - M - lx
    d.rectangle([lx, vy, lx + lw, vy + 62], fill=(255, 255, 255), outline=MIDLINE)
    d.text((lx + 8, vy + 4), "HOW SURE ARE WE?", font=F(SANS_B, 11), fill=INK)
    leg = [("REPORTED", "confirmed by named sources"),
           ("CLAIM", "one side says it, unverified"),
           ("FORECAST", "scheduled, expected, or a draft")]
    lyy = vy + 20
    for t, desc in leg:
        tag_chip(d, lx + 8, lyy, t)
        d.text((lx + 76, lyy + 1), desc, font=F(SANS, 9.5), fill=INK)
        lyy += 15
    y = vy + 68

    # ---- date check + sources footer
    d.rectangle([M, y, W - M, y + 28], fill=(255, 240, 240), outline=RED)
    d.text((M + 8, y + 3), "DATE CHECK \u2014 LEFT OFF ON PURPOSE: NOT 19 NOVEMBER NEWS",
           font=F(SANS_B, 10), fill=RED)
    d.text((M + 8, y + 16),
           "Anthropic's $83 IPO pricing (Wed 18 Nov)  \u00b7  Target & Lowe's earnings (Wed 18)  \u00b7  Fed October minutes (Wed 18)  \u00b7  COP31 final deal (due Fri 20)  \u00b7  Cyclone Akvan landfall (due Fri 20 noon)",
           font=F(SANS, 9.5), fill=INK)
    y += 33
    draw_wrapped(d, M, y,
                 "Every story on this page happened, or was first reported, on Thursday 19 November 2026. "
                 "Disputed claims are attributed, not stated as fact. Times are local. "
                 "Drawn from reporting by Reuters, AP, AFP, BBC, Al Jazeera, Yonhap, Xinhua, the ABS and the ICJ.",
                 F(SANS, 9.5), CW, fill=GREY, leading=11)

    img.save(OUT, "PNG", optimize=True)
    print("saved", OUT, img.size)


if __name__ == "__main__":
    build()
