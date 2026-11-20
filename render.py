#!/usr/bin/env python3
"""Render entry.png: one image summing up the world's news of
Thursday 19 November 2026. Deterministic: no random, no time, no network,
fixed fonts. Run: python3 render.py  ->  entry.png beside this file."""

import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (247, 243, 234)
NAVY = (20, 33, 61)
NAVY_DARK = (13, 22, 42)
RED = (192, 57, 43)
RED_DARK = (160, 44, 32)
GOLD = (232, 184, 75)
INK = (26, 26, 26)
MUTED = (88, 88, 88)
WHITE = (255, 255, 255)
BORDER = (222, 214, 198)
PANEL = (255, 255, 255)
CREAM = (255, 244, 214)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def fb(size):
    return ImageFont.truetype(FONT_BOLD, size)


def fr(size):
    return ImageFont.truetype(FONT_REG, size)


def fit_font(draw, text, path, max_size, max_w):
    """Largest font size up to max_size whose text fits max_w on one line."""
    size = max_size
    while size > 10:
        fnt = ImageFont.truetype(path, size)
        if draw.textlength(text, font=fnt) <= max_w:
            return fnt
        size -= 1
    return ImageFont.truetype(path, 10)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, fill, max_w, leading=None):
    """Draw wrapped text; return y just below the last line."""
    lh = leading or int(fnt.size * 1.28)
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


# ---------------------------------------------------------------- icons
def icon_flags3(d, x, y, w, h, pole_len=70):
    """Three flat flags (China / USA / Russia) on short poles, in a row."""
    fw = (w - 2 * 18) // 3
    fh = int(fw * 0.62)
    for i, flag in enumerate(("cn", "us", "ru")):
        fx = x + i * (fw + 18)
        # pole
        d.line([(fx + fw // 2, y + fh), (fx + fw // 2, y + fh + pole_len)],
               fill=CREAM, width=5)
        d.ellipse([fx + fw // 2 - 4, y + fh - 4, fx + fw // 2 + 4,
                   y + fh + 4], fill=GOLD)
        if flag == "cn":
            d.rectangle([fx, y, fx + fw, y + fh], fill=(222, 41, 16))
            d.ellipse([fx + 8, y + 7, fx + 20, y + 19], fill=GOLD)
            for sx, sy in ((fx + 26, y + 6), (fx + 32, y + 12),
                           (fx + 26, y + 20), (fx + 20, y + 14)):
                d.ellipse([sx, sy, sx + 5, sy + 5], fill=GOLD)
        elif flag == "us":
            for j in range(7):
                col = (179, 25, 34) if j % 2 == 0 else WHITE
                d.rectangle([fx, y + j * fh // 7,
                             fx + fw, y + (j + 1) * fh // 7], fill=col)
            d.rectangle([fx, y, fx + int(fw * 0.42), y + fh // 2],
                        fill=(28, 49, 107))
            for r in range(2):
                for c in range(3):
                    d.ellipse([fx + 4 + c * 9, y + 3 + r * 8,
                               fx + 8 + c * 9, y + 7 + r * 8], fill=WHITE)
        else:
            d.rectangle([fx, y, fx + fw, y + fh // 3], fill=WHITE)
            d.rectangle([fx, y + fh // 3, fx + fw, y + 2 * fh // 3],
                        fill=(0, 57, 166))
            d.rectangle([fx, y + 2 * fh // 3, fx + fw, y + fh],
                        fill=(213, 0, 50))


def icon_scales(d, cx, cy, s, col):
    """Scales of justice: pillar, beam, two pans."""
    d.line([(cx, cy - s // 2), (cx, cy + s // 2)], fill=col,
           width=max(3, s // 22))
    d.line([(cx - s // 2, cy - s // 3), (cx + s // 2, cy - s // 3)],
           fill=col, width=max(3, s // 22))
    d.ellipse([cx - s // 14, cy - s // 2 - s // 14,
               cx + s // 14, cy - s // 2 + s // 14], fill=col)
    for sx in (cx - s // 2, cx + s // 2):
        d.line([(sx, cy - s // 3), (sx - s // 7, cy + s // 12)],
               fill=col, width=max(2, s // 40))
        d.line([(sx, cy - s // 3), (sx + s // 7, cy + s // 12)],
               fill=col, width=max(2, s // 40))
        d.arc([sx - s // 7, cy - s // 12, sx + s // 7, cy + s // 4],
              0, 180, fill=col, width=max(2, s // 30))
    d.line([(cx - s // 4, cy + s // 2), (cx + s // 4, cy + s // 2)],
           fill=col, width=max(3, s // 22))


def icon_tower(d, cx, cy, s, col):
    """Skyscraper with a blast burst at its top."""
    bw = s // 3
    x0, x1 = cx - bw // 2, cx + bw // 2
    d.rectangle([x0, cy - s // 3, x1, cy + s // 2], fill=col)
    for i in range(4):
        wy = cy - s // 4 + i * s // 6
        d.line([(x0 + 4, wy), (x1 - 4, wy)], fill=WHITE,
               width=max(2, s // 40))
    # blast star above the tower
    bx, by = cx, cy - s // 2 + 4
    for ang in range(0, 360, 45):
        import math
        r1 = s // 5
        x2 = bx + r1 * math.cos(math.radians(ang))
        y2 = by + r1 * math.sin(math.radians(ang))
        d.line([(bx, by), (x2, y2)], fill=RED, width=max(3, s // 24))
    d.ellipse([bx - s // 12, by - s // 12, bx + s // 12, by + s // 12],
              fill=RED)


def icon_capitol(d, cx, cy, s, col):
    """US Capitol dome: dome, drum, base, flag."""
    d.rectangle([cx - s // 2, cy + s // 6, cx + s // 2, cy + s // 2],
                fill=col)
    d.rectangle([cx - s // 3, cy, cx + s // 3, cy + s // 6], fill=col)
    d.pieslice([cx - s // 4, cy - s // 2, cx + s // 4, cy + s // 10],
               180, 360, fill=col)
    d.line([(cx, cy - s // 2), (cx, cy - s // 2 - s // 8)], fill=col,
           width=max(2, s // 30))
    d.polygon([(cx, cy - s // 2 - s // 8), (cx + s // 10, cy - s // 2),
               (cx, cy - s // 2 + s // 16)], fill=RED)
    for i in range(3):
        d.line([(cx - s // 2 + i * s // 4, cy + s // 6),
                (cx - s // 2 + i * s // 4, cy + s // 2)], fill=WHITE,
               width=max(2, s // 40))


def icon_chart(d, cx, cy, s, col):
    """Rising stock chart: axes, line, arrowhead."""
    d.line([(cx - s // 2, cy + s // 2), (cx + s // 2, cy + s // 2)],
           fill=col, width=max(3, s // 22))
    d.line([(cx - s // 2, cy + s // 2), (cx - s // 2, cy - s // 2)],
           fill=col, width=max(3, s // 22))
    pts = [(cx - s // 2 + 4, cy + s // 4),
           (cx - s // 6, cy + s // 12),
           (cx + s // 12, cy - s // 12),
           (cx + s // 2 - 6, cy - s // 3)]
    d.line(pts, fill=RED, width=max(4, s // 18))
    # arrowhead
    d.polygon([(cx + s // 2 - 6, cy - s // 3),
               (cx + s // 2 - s // 5, cy - s // 3 - 2),
               (cx + s // 2 - s // 5 + 2, cy - s // 6)], fill=RED)


# ---------------------------------------------------------------- layout
PANELS = [
    ("WORLD COURT · THE HAGUE", "MYANMAR GUILTY OF GENOCIDE",
     "ICJ rules 9\u20136 \u2014 the first state ever found guilty of "
     "genocide; about 10,000 Rohingya killed in 2017.",
     icon_scales),
    ("SAUDI ARABIA · WAR", "MISSILE HITS RIYADH'S TALLEST TOWER",
     "Houthi missile strikes the PIF Tower, HQ of Saudi Arabia's $900bn "
     "fund; windows blown out, no injuries.",
     icon_tower),
    ("USA · CONGRESS", "SENATE VOTES TO KEEP IRAN WAR GOING",
     "Senate rejects a bid to end the war 51\u201348; first Iran vote "
     "since the midterms; the war has cost $48.3bn.",
     icon_capitol),
    ("MARKETS · AI", "BIGGEST IPO EVER: $81BN AI DEBUT",
     "Anthropic raised $81.3bn at $83 a share; debuted on Nasdaq and "
     "closed up 17% at $97.17.",
     icon_chart),
]

ALSO = ("Van Gogh sells for a record $190.4m  \u00b7  "
        "Bangladesh unrest: 4 killed, Yunus home torched  \u00b7  "
        "M5.7 quake jolts Kumamoto, 2 hurt, no tsunami")


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- header band
    d.rectangle([0, 0, W, 148], fill=NAVY)
    d.rectangle([0, 148, W, 154], fill=GOLD)
    d.text((48, 22), "T H E   W O R L D   I N   O N E   P I C T U R E",
           font=fb(25), fill=GOLD)
    date_fnt = fit_font(d, "THURSDAY 19 NOVEMBER 2026", FONT_BOLD, 62,
                        W - 96)
    d.text((48, 56), "THURSDAY 19 NOVEMBER 2026",
           font=date_fnt, fill=WHITE)

    # ---- lead panel: full-width red block
    lx, ly, lw, lh = 24, 168, W - 48, 344
    d.rounded_rectangle([lx, ly, lx + lw, ly + lh], radius=16, fill=RED)
    d.text((lx + 28, ly + 18), "LEAD STORY  \u00b7  SHENZHEN  \u00b7  DIPLOMACY",
           font=fb(21), fill=GOLD)
    # three flags, left column (short poles, centred on the headline)
    icon_flags3(d, lx + 28, ly + 95, 236, 110)
    tx = lx + 292
    tw = lw - 292 - 28
    head1 = fit_font(d, "XI \u00b7 TRUMP \u00b7 PUTIN", FONT_BOLD, 66, tw)
    d.text((tx, ly + 62), "XI \u00b7 TRUMP \u00b7 PUTIN", font=head1,
           fill=WHITE)
    head2 = fit_font(d, "SIGN \u2018PEACE DECLARATION\u2019", FONT_BOLD, 66,
                     tw)
    d.text((tx, ly + 62 + 76), "SIGN \u2018PEACE DECLARATION\u2019",
           font=head2, fill=WHITE)
    d.line([(tx, ly + 62 + 76 + 78), (tx + tw, ly + 62 + 76 + 78)],
           fill=GOLD, width=4)
    draw_wrapped(d, tx, ly + 62 + 76 + 96,
                 "First-ever three-way summit \u2014 about 90 minutes at "
                 "Kylin Villa \u2014 but no word on Ukraine or Iran.",
                 fr(24), CREAM, tw, leading=31)

    # ---- 2x2 grid of panels
    gx, gy = 24, 528
    cw, chh, gap = 480, 168, 14
    for i, (kick, head, body, icon) in enumerate(PANELS):
        col, row = i % 2, i // 2
        px = gx + col * (cw + gap)
        py = gy + row * (chh + gap)
        d.rounded_rectangle([px, py, px + cw, py + chh], radius=12,
                            fill=PANEL, outline=BORDER, width=2)
        icon(d, px + 56, py + chh // 2, 80, NAVY)
        tx = px + 114
        d.text((tx, py + 13), kick, font=fb(15), fill=RED)
        y = draw_wrapped(d, tx, py + 36, head, fb(25), INK,
                         cw - 114 - 16, leading=30)
        lines = wrap(d, body, fr(17), cw - 114 - 16)[:3]
        by = y + 4
        for line in lines:
            d.text((tx, by), line, font=fr(17), fill=MUTED)
            by += 21

    # ---- footer strip: three more stories
    fy = 890
    d.rounded_rectangle([24, fy, W - 24, fy + 76], radius=10, fill=NAVY)
    d.text((40, fy + 8), "ALSO TODAY", font=fb(17), fill=GOLD)
    draw_wrapped(d, 40, fy + 31, ALSO, fr(16), WHITE, W - 80, leading=20)

    # ---- footer credit
    fy2 = 976
    d.text((24, fy2),
           "Compiled from wire reports \u00b7 All events happened or were "
           "first reported on 19 November 2026",
           font=fr(18), fill=MUTED)
    d.text((24, fy2 + 24), "19 NOV 2026  \u00b7  THE WORLD IN ONE PICTURE",
           font=fb(16), fill=NAVY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, format="PNG")
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
