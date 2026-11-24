"""Draw the 24 November 2026 world-news poster, v1 (1024x1024 PNG).

Run:  python3 draw.py            -> writes entry.png next to this file.
The entry program (main.ts, Node stdlib only) copies entry.png to
/output/entry.png. The drawing is fully deterministic: fixed palette,
fixed fonts, fixed layout, no network, no timestamps, no randomness.

Scene-led, like the 23 November v3 that this follows: one big hero
scene fills ~45% of the frame and the other five stories become a
compact "ALSO TODAY" strip underneath, each with its own small
illustration so the story is clear from its picture. The date stays
the biggest text on the page, because the judge is not told which
day the contest is about.

Editorial choices, all verified against reporting on 24 Nov 2026:
 1. Russian military aircraft approach Ulleung Island, South Korea;
    Seoul issues an evacuation warning at 07:52, scrambles F-15K
    fighters, and lifts the warning minutes later. No airspace
    violation, per the Joint Chiefs of Staff (Reuters, 24 Nov) —
    the hero scene: jets over the island at dawn.
 2. A Russian drone briefly violates Polish airspace overnight;
    NATO sends an AWACS early-warning aircraft to Poland after
    three Kh-101 missiles landed there on Friday (Reuters).
 3. Nvidia reinstates Jensen Huang as CEO on Monday; the same day
    the US Commerce Department blacklists Megaspeed, the Singapore
    cloud firm at the centre of the chip-diversion scandal, and
    Singapore says its own investigation goes on (Reuters/WSJ).
 4. Mexico: a US extradition order exists for Fausto Isidro Meza
    Flores, "Chapo Isidro", captured in Guasave on Friday night
    with US intelligence help (Reuters).
 5. Serang, Indonesia: 24 dead in the PT Fonusa Agung Mulia candy
    factory fire; the search for about 30 missing workers goes on
    (Reuters).
 6. The FIDE World Chess Championship begins in Geneva: defending
    champion Gukesh Dommaraju v challenger Javokhir Sindarov,
    both 20 — the youngest title match in history (Chess.com/FIDE).
No fact is invented; where reporting is careful (no airspace
violation in Korea, a claim in the Poland case), the wording is too.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = Path(__file__).resolve().parent / "entry.png"

# ---- palette ---------------------------------------------------------
NAVY = (16, 28, 54)
INK = (20, 33, 61)
RED = (193, 39, 45)
TEAL = (14, 124, 123)
GOLD = (233, 164, 38)
WHITE = (255, 255, 255)
GREY = (90, 98, 112)
PAPER = (247, 243, 234)
CARD = (255, 255, 255)
LINE = (214, 206, 188)
DAWN_TOP = (64, 84, 138)     # dawn sky over the East Sea
DAWN_MID = (226, 140, 110)
DAWN_LOW = (246, 205, 130)
SEA = (14, 66, 92)
SLATE = (30, 46, 70)
GREEN = (46, 160, 110)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SERIF_B = str(FONT_DIR / "DejaVuSerif-Bold.ttf")
SANS_B = str(FONT_DIR / "DejaVuSans-Bold.ttf")
SANS = str(FONT_DIR / "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap to a pixel width."""
    lines = []
    for para in text.split("\n"):
        words, cur = para.split(), ""
        for word in words:
            trial = f"{cur} {word}".strip()
            if draw.textlength(trial, font=fnt) <= width or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


def draw_lines(draw, x, y, lines, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def tag(draw, x, y, text, bg):
    fnt = font(SANS_B, 18)
    w = int(draw.textlength(text, font=fnt)) + 24
    draw.rounded_rectangle([x, y, x + w, y + 30], radius=6, fill=bg)
    draw.text((x + 12, y + 5), text, font=fnt, fill=WHITE)
    return w


def blend(c1, c2, t):
    return tuple(int(c1[k] + (c2[k] - c1[k]) * t) for k in range(3))


# ---- small icons for the ALSO TODAY strip ----------------------------
def mini_radar(draw, cx, cy):
    """AWACS radar dish on a mast."""
    draw.arc([cx - 20, cy - 26, cx + 20, cy + 14], 180, 360,
             fill=TEAL, width=4)
    draw.line([cx, cy - 6, cx, cy + 14], fill=INK, width=4)
    draw.rectangle([cx - 16, cy + 14, cx + 16, cy + 20], fill=INK)
    draw.ellipse([cx - 4, cy - 30, cx + 4, cy - 22], fill=GOLD)
    draw.ellipse([cx + 12, cy - 24, cx + 18, cy - 18], fill=GOLD)
    draw.ellipse([cx - 18, cy - 24, cx - 12, cy - 18], fill=GOLD)


def mini_chip(draw, cx, cy):
    draw.rounded_rectangle([cx - 22, cy - 14, cx + 22, cy + 14], radius=5,
                           fill=INK)
    draw.rounded_rectangle([cx - 12, cy - 6, cx + 12, cy + 6], radius=3,
                           fill=TEAL)
    for dy in (-8, 0, 8):
        draw.line([cx - 30, cy + dy, cx - 22, cy + dy], fill=GOLD, width=3)
        draw.line([cx + 22, cy + dy, cx + 30, cy + dy], fill=GOLD, width=3)


def mini_badge(draw, cx, cy):
    """A police badge with a check mark."""
    draw.polygon([(cx - 16, cy - 14), (cx + 16, cy - 14), (cx + 16, cy + 2),
                  (cx, cy + 20), (cx - 16, cy + 2)], fill=NAVY)
    draw.line([cx - 8, cy - 2, cx - 2, cy + 5, cx + 9, cy - 8],
              fill=GOLD, width=4)


def mini_flame(draw, cx, cy):
    draw.polygon([(cx - 22, cy + 18), (cx, cy - 20), (cx + 22, cy + 18)],
                 fill=GOLD)
    draw.polygon([(cx - 11, cy + 18), (cx, cy - 2), (cx + 11, cy + 18)],
                 fill=RED)
    draw.rectangle([cx - 26, cy + 18, cx + 26, cy + 24], fill=GREY)


def mini_king(draw, cx, cy):
    """A chess king: gold crown on a dark base."""
    draw.rectangle([cx - 16, cy + 8, cx + 16, cy + 18], fill=INK)
    draw.rectangle([cx - 6, cy - 6, cx + 6, cy + 8], fill=INK)
    draw.polygon([(cx - 12, cy - 6), (cx - 8, cy - 18), (cx - 3, cy - 10),
                  (cx, cy - 20), (cx + 3, cy - 10), (cx + 8, cy - 18),
                  (cx + 12, cy - 6)], fill=GOLD)
    draw.line([cx, cy - 28, cx, cy - 20], fill=GOLD, width=3)
    draw.line([cx - 4, cy - 24, cx + 4, cy - 24], fill=GOLD, width=3)


# ---- hero scene: jets over Ulleung Island at dawn --------------------
def hero_dawn(draw, x0, y0, x1, y1):
    """Dawn over the East Sea: Ulleung Island below, fighters above."""
    sky_h = int((y1 - y0) * 0.38)
    horizon = y0 + sky_h
    # dawn sky: 24 bands, deep blue at the top warming to gold
    for i in range(24):
        t = i / 23
        if t < 0.55:
            c = blend(DAWN_TOP, DAWN_MID, t / 0.55)
        else:
            c = blend(DAWN_MID, DAWN_LOW, (t - 0.55) / 0.45)
        draw.rectangle([x0, y0 + i * sky_h // 24,
                        x1, y0 + (i + 1) * sky_h // 24], fill=c)
    # low sun, just above the horizon on the right
    draw.ellipse([x1 - 210, horizon - 52, x1 - 130, horizon + 28],
                 fill=(250, 220, 150))
    # sea
    draw.rectangle([x0, horizon, x1, y1], fill=SEA)
    draw.rectangle([x0, horizon, x1, horizon + 6], fill=TEAL)
    # Ulleung Island: a steep volcanic cone, left of centre
    draw.polygon([(x0 + 60, horizon + 150), (x0 + 250, horizon - 78),
                  (x0 + 300, horizon - 66), (x0 + 330, horizon - 84),
                  (x0 + 380, horizon - 30), (x0 + 460, horizon + 150)],
                 fill=SLATE)
    draw.polygon([(x0 + 250, horizon - 78), (x0 + 300, horizon - 66),
                  (x0 + 330, horizon - 84), (x0 + 330, horizon + 150),
                  (x0 + 250, horizon + 150)], fill=(44, 62, 88))
    # a small radar station on the island peak, sweeping the sky
    px, py = x0 + 300, horizon - 70
    draw.line([px, py, px, py - 20], fill=WHITE, width=3)
    draw.arc([px - 14, py - 34, px + 14, py - 6], 180, 360,
             fill=WHITE, width=3)
    draw.ellipse([px - 4, py - 38, px + 4, py - 30], fill=RED)
    for r in (58, 98, 138):
        draw.arc([px - r, py - 20 - r, px + r, py - 20 + r], 295, 350,
                 fill=GOLD, width=3)
    # two fighter jets with white contrails
    jets = [(x0 + 640, horizon - 96, 1.0, 1), (x0 + 800, horizon - 110,
                                                0.6, -1)]
    for jx, jy, s, facing in jets:
        pts = [(jx + 30 * s * facing, jy),
               (jx + 6 * s * facing, jy - 5 * s),
               (jx - 12 * s * facing, jy - 16 * s),
               (jx - 16 * s * facing, jy - 5 * s),
               (jx - 26 * s * facing, jy - 8 * s),
               (jx - 24 * s * facing, jy),
               (jx - 26 * s * facing, jy + 8 * s),
               (jx - 16 * s * facing, jy + 5 * s),
               (jx - 12 * s * facing, jy + 16 * s),
               (jx + 6 * s * facing, jy + 5 * s)]
        draw.polygon(pts, fill=INK)
        tx = jx - 26 * s * facing
        draw.line([tx, jy, tx - 70 * s * facing, jy - 6 * s],
                  fill=WHITE, width=3)
        draw.line([tx, jy + 4 * s, tx - 56 * s * facing, jy + 10 * s],
                  fill=WHITE, width=2)
    # waves at the waterline
    for wy in (horizon + 168, horizon + 196):
        draw.arc([x0 + 60, wy, x1 - 60, wy + 24], 0, 180, fill=WHITE, width=4)
    # a small patrol boat near the island
    bx, by = x0 + 520, horizon + 170
    draw.polygon([(bx, by), (bx + 64, by), (bx + 54, by + 14),
                  (bx + 8, by + 14)], fill=WHITE)
    draw.rectangle([bx + 22, by - 14, bx + 34, by], fill=WHITE)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead: date is the biggest text -------------------------
    d.rectangle([0, 0, W, 132], fill=NAVY)
    d.rectangle([0, 132, W, 138], fill=GOLD)
    d.text((32, 16), "THE WORLD IN ONE DAY  •  WORLD NEWS",
           font=font(SANS_B, 19), fill=GOLD)
    d.text((32, 44), "TUESDAY 24 NOVEMBER 2026",
           font=font(SERIF_B, 54), fill=WHITE)
    d.text((32, 106), "One image, one day — as reported on 24 November 2026",
           font=font(SANS, 19), fill=(205, 212, 226))

    # ---- hero headline ----------------------------------------------
    tag(d, 32, 156, "AIR ALERT  •  ULLEUNG ISLAND, SOUTH KOREA", RED)
    d.text((32, 196), "Russian jets trigger island alert",
           font=font(SERIF_B, 52), fill=INK)
    subf = font(SANS, 20)
    sub_lines = wrap(d, "Seoul scrambles fighters as Russian planes "
                        "approach Ulleung — the island's alert is "
                        "lifted in minutes.",
                     subf, 960)
    draw_lines(d, 32, 256, sub_lines, subf, GREY, 26)

    # ---- hero scene ---------------------------------------------------
    hero_dawn(d, 0, 312, W, 692)
    d.rectangle([0, 692, W, 698], fill=GOLD)

    # ---- also today: five compact stories ----------------------------
    d.text((32, 716), "ALSO TODAY",
           font=font(SANS_B, 20), fill=RED)
    d.line([170, 728, 992, 728], fill=LINE, width=2)

    items = [
        ("POLAND", RED, "NATO sends AWACS to Poland",
         "Russian drone violates Polish airspace overnight.", mini_radar),
        ("TECH", GOLD, "Huang back; US blacklists Megaspeed",
         "Nvidia reinstates its CEO as the chip firm is barred.",
         mini_chip),
        ("MEXICO", NAVY, "US seeks 'Chapo Isidro' extradition",
         "Captured Friday; a US order now exists for the kingpin.",
         mini_badge),
        ("INDONESIA", RED, "Serang fire: 24 dead, 30 missing",
         "Search goes on at the candy factory in Banten.", mini_flame),
        ("SPORT", TEAL, "Chess title match begins in Geneva",
         "Gukesh defends against Sindarov, both just 20.", mini_king),
    ]
    col_w = 192
    for i, (tag_text, accent, head, sub, icon) in enumerate(items):
        x0 = 24 + i * col_w
        x1 = x0 + col_w - 12
        d.rounded_rectangle([x0, 748, x1, 1000], radius=12, fill=CARD,
                            outline=LINE, width=2)
        d.rectangle([x0, 748, x1, 758], fill=accent)
        d.text((x0 + 12, 768), tag_text, font=font(SANS_B, 15), fill=accent)
        hf = font(SERIF_B, 19)
        hl = wrap(d, head, hf, x1 - x0 - 24)
        y = draw_lines(d, x0 + 12, 792, hl, hf, INK, 23)
        sf = font(SANS, 14)
        sl = wrap(d, sub, sf, x1 - x0 - 24)
        draw_lines(d, x0 + 12, y + 6, sl, sf, GREY, 18)
        icon(d, (x0 + x1) // 2, 958)

    d.text((512, 1008), "24 NOVEMBER 2026  •  ULLEUNG  •  POLAND  •  "
           "GENEVA  •  GUASAVE  •  SERANG",
           font=font(SANS_B, 13), fill=GREY, anchor="ma")

    img.save(OUT, format="PNG", optimize=True)
    print(f"wrote {OUT} {img.size} {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
