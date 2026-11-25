"""Draw the 24 November 2026 world-news poster, v4 (1024x1024 PNG).

Run:  python3 draw.py            -> writes entry.png next to this file.
The entry program (main.ts, Node stdlib only) copies entry.png to
/output/entry.png. The drawing is fully deterministic: fixed palette,
fixed fonts, fixed layout, no network, no timestamps, no randomness.

v4 (round 2 ranked v3 1976 of 9,063, score 594,807 — DOWN from v2's
1320 of 7,302): the hero-only tweaks of v3 did not help. The round-2
audit found the top entries carry 30-46 stories with a picture each,
against v3's 6. So v4 tests coverage: the hero is kept, and the rest
of the frame becomes a dense 6x5 grid — 29 more stories, each with
its own mini scene band, for 30 stories total. Tile text is 12 px,
dense by design; full-size QA decides whether it reads, with a
24-story fallback (hero + 5 cards + 3x6 grid) if it does not.

Editorial choices, all verified against primary reporting on
24 Nov 2026 (Reuters/AP/AFP/BBC, checked 25 Nov):
 HERO: Russian military aircraft approach Ulleung Island, South
   Korea; Seoul scrambles F-15Ks, no airspace violation (Reuters).
 GRID (29): AWACS to Poland; Huang back + Megaspeed blacklisted;
   Mexico to try 'Chapo Isidro' at home despite a US extradition
   bid (Reuters — v3's "faces a US extradition order" was wrong);
   Serang fire, 24 dead, 30 missing; chess title match in Geneva;
   Huawei convicted on 10 of 12 counts; Iran says a 4th tanker hit
   a mine in Hormuz; IRGC says it hit a container ship in Hormuz
   (claim unconfirmed, no vessel named); Houthis 60 km from Aden;
   Houthi drone hits Riyadh's PIF Tower, 11 hurt; Israel kills
   Hamas internal security chief Naeem Abu Nahel; Zelenskyy
   CONFIRMS Ukraine hit Russian ships (attacks were 21-22 Nov,
   the 24 Nov news is the confirmation); Baghdad takes over
   Kurdish oilfields and borders; Hasina plans a Dec 16 return;
   Malaysia to send migrants home in Dec; Hanoi hotpot blast kills
   six; Haftar visits Turkey for the first time; Turkish
   helicopter crash kills five; 25 held hostage in a Cartagena
   supermarket; car bomb injures 23 in Villavicencio (blast Mon
   night, first reported Tue); Gaza declares a meningitis epidemic
   alert; UK sanctions the Houthis and four officials; Senegal
   reinstated as Africa Cup champions; Sanofi to buy Insmed for
   $41bn; Saudi strikes on Yemen buses leave 25 dead or missing
   (toll contested, attributed); Solomon Islands to scrap its
   China security pact; UK opens an inquiry into nuclear-test
   veterans; Lukashenko offers to fly with Zelenskyy to Moscow;
   China probes Politburo member Chen Jining.
 DROPPED after verification (wrong date for 24 Nov): ICJ Myanmar
   verdict (19 Nov), Prabowo's VP nominations (23 Nov),
   Zelenskyy's four-party call (23 Nov), Pentagon rebuke of Canada
   (22-23 Nov), China death sentence for spying (23 Nov, and
   sentenced not executed), DR Congo missing plane (22 Nov),
   measles elimination status (17 Nov), Bukele's Haiti deaths
   (20-22 Nov), COP31 collapse (22 Nov), Netanyahu urging Trump
   (22-23 Nov), Rutte's space-threat vow (23 Nov).
No fact is invented; where reporting is careful (Iran's claims,
the Yemen toll, a claim in the Poland case), the wording is too.
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


# ---- hero scene: jets over Ulleung Island at dawn --------------------
# Vertical offsets scale with the scene height (v3 used a 380 px hero;
# v4 uses ~310 px), so the island, waves and boat stay inside.
def hero_dawn(draw, x0, y0, x1, y1):
    """Dawn over the East Sea: Ulleung Island below, fighters above."""
    hgt = y1 - y0
    k = hgt / 380.0

    def sy(off):
        return int(off * k)

    sky_h = int(hgt * 0.38)
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
    draw.ellipse([x1 - 210, horizon - sy(52), x1 - 130, horizon + sy(28)],
                 fill=(250, 220, 150))
    # sea
    draw.rectangle([x0, horizon, x1, y1], fill=SEA)
    draw.rectangle([x0, horizon, x1, horizon + 6], fill=TEAL)
    # Ulleung Island: a steep volcanic cone, left of centre
    draw.polygon([(x0 + 60, horizon + sy(150)), (x0 + 250, horizon - sy(78)),
                  (x0 + 300, horizon - sy(66)), (x0 + 330, horizon - sy(84)),
                  (x0 + 380, horizon - sy(30)), (x0 + 460, horizon + sy(150))],
                 fill=SLATE)
    draw.polygon([(x0 + 250, horizon - sy(78)), (x0 + 300, horizon - sy(66)),
                  (x0 + 330, horizon - sy(84)), (x0 + 330, horizon + sy(150)),
                  (x0 + 250, horizon + sy(150))], fill=(44, 62, 88))
    # a small radar station on the island peak, sweeping the sky
    px, py = x0 + 300, horizon - sy(70)
    draw.line([px, py, px, py - 20], fill=WHITE, width=3)
    draw.arc([px - 14, py - 34, px + 14, py - 6], 180, 360,
             fill=WHITE, width=3)
    draw.ellipse([px - 4, py - 38, px + 4, py - 30], fill=RED)
    # radar arcs sweep right, toward the jets, and stay inside the
    # hero scene (an up-right sweep crosses the sub-headline text)
    for r in (60, 100, 140):
        draw.arc([px - r, py - 20 - r, px + r, py - 20 + r], 340, 360,
                 fill=GOLD, width=5)
        draw.arc([px - r, py - 20 - r, px + r, py - 20 + r], 0, 30,
                 fill=GOLD, width=5)
    # two fighter jets with white contrails, bigger than in v2 so the
    # island no longer dominates the hero
    jets = [(x0 + 640, horizon - sy(96), 1.45, 1),
            (x0 + 800, horizon - sy(110), 1.0, -1)]
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
    for wy in (horizon + sy(168), horizon + sy(196)):
        draw.arc([x0 + 60, wy, x1 - 60, wy + 24], 0, 180, fill=WHITE, width=4)
    # a small patrol boat near the island
    bx, by = x0 + 520, horizon + sy(170)
    draw.polygon([(bx, by), (bx + 64, by), (bx + 54, by + 14),
                  (bx + 8, by + 14)], fill=WHITE)
    draw.rectangle([bx + 22, by - 14, bx + 34, by], fill=WHITE)


# ---- mini scenes for the grid tiles ----------------------------------
# Each draws one flat pictogram inside a ~159x26 px band. All shapes
# stay inside the band (offsets within +-12 px of the centre), so a
# tile's picture never collides with its headline.
def mini_plane(d, x0, y0, x1, y1, bg):
    """A small AWACS-style plane: fuselage, nose, tail, radar dome."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.rounded_rectangle([cx - 42, cy - 4, cx + 38, cy + 4], radius=4,
                        fill=WHITE)
    d.polygon([(cx + 38, cy - 4), (cx + 50, cy), (cx + 38, cy + 4)],
              fill=WHITE)
    d.polygon([(cx - 42, cy - 4), (cx - 42, cy - 11), (cx - 30, cy - 4)],
              fill=WHITE)
    d.rectangle([cx - 2, cy - 10, cx + 2, cy - 4], fill=WHITE)
    d.ellipse([cx - 9, cy - 12, cx + 9, cy - 5], fill=WHITE)


def mini_chip(d, x0, y0, x1, y1, bg):
    """A chip with pins, barred by a red ring."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cx, cy = (x0 + x1) // 2 - 8, (y0 + y1) // 2
    d.rounded_rectangle([cx - 18, cy - 9, cx + 18, cy + 9], radius=3,
                        fill=INK)
    d.rounded_rectangle([cx - 9, cy - 4, cx + 9, cy + 4], radius=2,
                        fill=TEAL)
    for dy in (-5, 0, 5):
        d.line([cx - 24, cy + dy, cx - 18, cy + dy], fill=GOLD, width=2)
        d.line([cx + 18, cy + dy, cx + 24, cy + dy], fill=GOLD, width=2)
    rx = x1 - 22
    d.ellipse([rx - 11, cy - 11, rx + 11, cy + 11], outline=RED, width=3)
    d.line([rx - 7, cy + 7, rx + 7, cy - 7], fill=RED, width=3)


def mini_court(d, x0, y0, x1, y1, bg):
    """A courthouse: pediment, columns, steps."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cx = (x0 + x1) // 2
    base = y1 - 3
    d.polygon([(cx - 40, y0 + 11), (cx + 40, y0 + 11), (cx, y0 + 1)],
              fill=NAVY)
    d.rectangle([cx - 40, y0 + 11, cx + 40, base - 5], fill=(120, 130, 148))
    for col in (-26, 0, 26):
        d.rectangle([cx + col - 4, y0 + 13, cx + col + 4, base - 5],
                    fill=WHITE)
    d.rectangle([cx - 46, base - 5, cx + 46, base], fill=NAVY)


def mini_factory(d, x0, y0, x1, y1, bg):
    """A factory with flames on its sawtooth roof and smoke."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cx = (x0 + x1) // 2
    base = y1 - 3
    d.polygon([(cx - 48, base), (cx - 48, y0 + 16), (cx - 26, y0 + 8),
               (cx - 4, y0 + 16), (cx + 18, y0 + 8), (cx + 40, y0 + 16),
               (cx + 48, y0 + 16), (cx + 48, base)], fill=(70, 78, 92))
    for fx in (-34, -6, 22):
        d.polygon([(cx + fx - 8, y0 + 16), (cx + fx, y0 + 2),
                   (cx + fx + 8, y0 + 16)], fill=GOLD)
        d.polygon([(cx + fx - 4, y0 + 16), (cx + fx, y0 + 8),
                   (cx + fx + 4, y0 + 16)], fill=RED)
    d.ellipse([cx + 36, y0 + 2, cx + 48, y0 + 12], fill=(120, 126, 138))


def mini_chess(d, x0, y0, x1, y1, bg):
    """A chessboard strip with a gold king and a dark pawn."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cw = 12
    bx0 = (x0 + x1) // 2 - 36
    for r in range(2):
        for c in range(6):
            if (r + c) % 2 == 0:
                d.rectangle([bx0 + c * cw, y0 + 1 + r * 12,
                             bx0 + (c + 1) * cw, y0 + 13 + r * 12],
                            fill=(240, 235, 220))
    kx, ky = bx0 + 14, y0 + 20
    d.rectangle([kx - 7, ky, kx + 7, ky + 4], fill=GOLD)
    d.rectangle([kx - 3, ky - 6, kx + 3, ky], fill=GOLD)
    d.polygon([(kx - 6, ky - 6), (kx - 4, ky - 12), (kx - 2, ky - 8),
               (kx, ky - 13), (kx + 2, ky - 8), (kx + 4, ky - 12),
               (kx + 6, ky - 6)], fill=GOLD)
    px2, py2 = bx0 + 58, y0 + 21
    d.ellipse([px2 - 5, py2 - 7, px2 + 5, py2 + 3], fill=INK)
    d.rectangle([px2 - 7, py2 + 3, px2 + 7, py2 + 7], fill=INK)


def mini_gavel(d, x0, y0, x1, y1, bg):
    """A judge's gavel over its sound block."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.polygon([(cx - 34, cy - 11), (cx - 12, cy - 11), (cx - 20, cy - 3),
               (cx - 42, cy - 3)], fill=GOLD)
    d.line([cx - 20, cy - 3, cx + 6, cy + 9], fill=(120, 90, 40), width=4)
    d.rectangle([cx + 2, cy + 7, cx + 30, cy + 12], fill=NAVY)
    d.ellipse([cx + 34, cy - 8, cx + 44, cy + 2], fill=RED)


def mini_tanker(d, x0, y0, x1, y1, bg):
    """An oil tanker with containers and a plume of smoke."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.polygon([(cx - 52, cy + 2), (cx + 52, cy + 2), (cx + 44, cy + 11),
               (cx - 44, cy + 11)], fill=INK)
    for i, col in enumerate((RED, GOLD, TEAL)):
        d.rectangle([cx - 40 + i * 16, cy - 8, cx - 28 + i * 16, cy + 2],
                    fill=col)
    d.rectangle([cx + 30, cy - 10, cx + 36, cy + 2], fill=WHITE)
    d.ellipse([cx + 38, cy - 12, cx + 48, cy - 4], fill=(120, 126, 138))
    d.line([x0 + 8, cy + 11, x1 - 8, cy + 11], fill=WHITE, width=2)


def mini_ship(d, x0, y0, x1, y1, bg):
    """A container ship under small radar arcs."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.polygon([(cx - 48, cy + 2), (cx + 48, cy + 2), (cx + 40, cy + 11),
               (cx - 40, cy + 11)], fill=SLATE)
    d.rectangle([cx - 30, cy - 6, cx - 14, cy + 2], fill=WHITE)
    d.rectangle([cx - 6, cy - 6, cx + 10, cy + 2], fill=GOLD)
    d.line([cx + 26, cy + 2, cx + 26, cy - 8], fill=WHITE, width=2)
    for r in (8, 14):
        d.arc([cx + 26 - r, cy - 8 - r, cx + 26 + r, cy - 8 + r], 300, 30,
              fill=GOLD, width=2)


def mini_map(d, x0, y0, x1, y1, bg):
    """A map outline with an advance arrow and a red dot."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.rounded_rectangle([cx - 46, cy - 11, cx + 46, cy + 11], radius=5,
                        outline=WHITE, width=2)
    d.line([cx - 38, cy + 6, cx + 22, cy - 6], fill=GOLD, width=3)
    d.polygon([(cx + 22, cy - 6), (cx + 8, cy - 10), (cx + 12, cy - 2)],
              fill=GOLD)
    d.ellipse([cx + 30, cy - 9, cx + 40, cy + 1], fill=RED)


def mini_tower(d, x0, y0, x1, y1, bg):
    """A tall tower with an antenna and a small drone beside it."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.rectangle([cx - 12, cy - 9, cx + 12, cy + 12], fill=INK)
    d.rectangle([cx - 16, cy - 5, cx + 16, cy - 1], fill=WHITE)
    d.rectangle([cx - 16, cy + 3, cx + 16, cy + 7], fill=WHITE)
    d.line([cx, cy - 9, cx, cy - 13], fill=WHITE, width=2)
    d.ellipse([cx - 2, cy - 14, cx + 2, cy - 10], fill=RED)
    dx = cx + 38
    d.ellipse([dx - 6, cy - 9, dx + 6, cy - 3], fill=RED)
    d.line([dx - 12, cy - 11, dx + 12, cy - 11], fill=GOLD, width=2)


def mini_city(d, x0, y0, x1, y1, bg):
    """City blocks with a plume of smoke."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    for bx, bh in ((-44, 20), (-18, 24), (8, 16), (30, 22)):
        d.rectangle([cx + bx, cy + 12 - bh, cx + bx + 18, cy + 12],
                    fill=SLATE)
        d.rectangle([cx + bx + 4, cy + 12 - bh + 4, cx + bx + 8,
                     cy + 12 - bh + 8], fill=GOLD)
    d.ellipse([cx + 28, cy - 12, cx + 42, cy - 2], fill=(120, 126, 138))


def mini_warship(d, x0, y0, x1, y1, bg):
    """A grey warship with a turret and smoke."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.polygon([(cx - 50, cy + 2), (cx + 50, cy + 2), (cx + 42, cy + 11),
               (cx - 42, cy + 11)], fill=(70, 78, 92))
    d.rectangle([cx - 20, cy - 6, cx + 2, cy + 2], fill=INK)
    d.line([cx + 2, cy - 3, cx + 26, cy - 6], fill=INK, width=3)
    d.rectangle([cx + 28, cy - 9, cx + 34, cy + 2], fill=WHITE)
    d.ellipse([cx + 36, cy - 12, cx + 46, cy - 4], fill=(120, 126, 138))


def mini_oil(d, x0, y0, x1, y1, bg):
    """An oil pump jack."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.line([cx - 30, cy + 11, cx - 6, cy - 11], fill=INK, width=3)
    d.line([cx - 6, cy - 11, cx + 18, cy + 11], fill=INK, width=3)
    d.line([cx - 6, cy - 11, cx + 34, cy - 7], fill=GOLD, width=3)
    d.line([cx + 34, cy - 7, cx + 34, cy + 2], fill=GOLD, width=2)
    d.rectangle([cx - 36, cy + 9, cx + 40, cy + 12], fill=INK)


def mini_flame(d, x0, y0, x1, y1, bg):
    """Two flames and smoke, for blasts and fires."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    for fx in (-24, 4):
        d.polygon([(cx + fx - 12, cy + 11), (cx + fx, cy - 11),
                   (cx + fx + 12, cy + 11)], fill=GOLD)
        d.polygon([(cx + fx - 6, cy + 11), (cx + fx, cy - 2),
                   (cx + fx + 6, cy + 11)], fill=RED)
    d.ellipse([cx + 28, cy - 11, cx + 42, cy + 1], fill=(120, 126, 138))


def mini_flags(d, x0, y0, x1, y1, bg):
    """Two crossed flags on poles."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.line([cx - 20, cy - 11, cx - 20, cy + 12], fill=WHITE, width=2)
    d.line([cx + 20, cy - 11, cx + 20, cy + 12], fill=WHITE, width=2)
    d.polygon([(cx - 20, cy - 11), (cx - 2, cy - 8), (cx - 20, cy - 4)],
              fill=RED)
    d.polygon([(cx + 20, cy - 11), (cx + 2, cy - 8), (cx + 20, cy - 4)],
              fill=GOLD)
    d.rectangle([cx - 34, cy + 10, cx + 34, cy + 12], fill=WHITE)


def mini_heli(d, x0, y0, x1, y1, bg):
    """A helicopter: body, rotor, tail."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.ellipse([cx - 26, cy - 7, cx + 6, cy + 7], fill=INK)
    d.polygon([(cx + 6, cy - 2), (cx + 44, cy - 6), (cx + 44, cy + 1),
               (cx + 6, cy + 3)], fill=INK)
    d.line([cx - 30, cy - 11, cx + 10, cy - 11], fill=WHITE, width=2)
    d.line([cx - 10, cy - 7, cx - 10, cy - 11], fill=WHITE, width=2)
    d.rectangle([cx - 18, cy - 3, cx - 8, cy + 3], fill=GOLD)


def mini_building(d, x0, y0, x1, y1, bg):
    """A building with a red siren light on top."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.rectangle([cx - 26, cy - 8, cx + 26, cy + 12], fill=SLATE)
    for wx in (-18, 0, 18):
        d.rectangle([cx + wx - 4, cy - 4, cx + wx + 4, cy + 2],
                    fill=GOLD)
    d.rectangle([cx - 6, cy + 4, cx + 6, cy + 12], fill=WHITE)
    d.ellipse([cx - 4, cy - 13, cx + 4, cy - 8], fill=RED)


def mini_hospital(d, x0, y0, x1, y1, bg):
    """A hospital block with a red cross."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.rectangle([cx - 30, cy - 10, cx + 30, cy + 12], fill=WHITE)
    d.rectangle([cx - 4, cy - 7, cx + 4, cy + 7], fill=RED)
    d.rectangle([cx - 9, cy - 2, cx + 9, cy + 2], fill=RED)
    d.rectangle([cx - 30, cy + 8, cx + 30, cy + 12], fill=TEAL)


def mini_doc(d, x0, y0, x1, y1, bg):
    """A document with text lines and a red seal."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.rectangle([cx - 22, cy - 11, cx + 14, cy + 11], fill=WHITE)
    for i, ln in enumerate((-6, -1, 4)):
        d.line([cx - 17, cy + ln, cx + 9, cy + ln], fill=GREY, width=2)
    d.ellipse([cx + 16, cy + 1, cx + 28, cy + 11], fill=RED)
    d.ellipse([cx + 20, cy + 4, cx + 24, cy + 8], fill=WHITE)


def mini_trophy(d, x0, y0, x1, y1, bg):
    """A gold trophy cup."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.polygon([(cx - 12, cy - 11), (cx + 12, cy - 11), (cx + 8, cy + 1),
               (cx - 8, cy + 1)], fill=GOLD)
    d.arc([cx - 20, cy - 11, cx - 6, cy + 1], 90, 270, fill=GOLD, width=3)
    d.arc([cx + 6, cy - 11, cx + 20, cy + 1], 270, 90, fill=GOLD, width=3)
    d.rectangle([cx - 3, cy + 1, cx + 3, cy + 7], fill=GOLD)
    d.rectangle([cx - 10, cy + 7, cx + 10, cy + 11], fill=GOLD)


def mini_pill(d, x0, y0, x1, y1, bg):
    """A two-tone capsule."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.rounded_rectangle([cx - 34, cy - 8, cx + 34, cy + 8], radius=8,
                        fill=WHITE)
    d.rounded_rectangle([cx - 34, cy - 8, cx, cy + 8], radius=8,
                        fill=TEAL)
    d.rectangle([cx - 8, cy - 8, cx, cy + 8], fill=TEAL)
    d.ellipse([cx + 16, cy - 4, cx + 24, cy + 4], fill=GOLD)


def mini_bus(d, x0, y0, x1, y1, bg):
    """A bus with windows and wheels."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.rounded_rectangle([cx - 44, cy - 9, cx + 44, cy + 8], radius=5,
                        fill=INK)
    for wx in (-34, -16, 2, 20):
        d.rectangle([cx + wx, cy - 5, cx + wx + 12, cy + 1], fill=GOLD)
    d.ellipse([cx - 32, cy + 6, cx - 22, cy + 12], fill=INK)
    d.ellipse([cx + 22, cy + 6, cx + 32, cy + 12], fill=INK)
    d.ellipse([cx - 29, cy + 8, cx - 25, cy + 11], fill=GREY)
    d.ellipse([cx + 25, cy + 8, cx + 29, cy + 11], fill=GREY)


def mini_globe(d, x0, y0, x1, y1, bg):
    """A globe with meridians."""
    d.rectangle([x0, y0, x1, y1], fill=bg)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=TEAL)
    d.arc([cx - 12, cy - 12, cx + 12, cy + 12], 0, 360, fill=WHITE,
          width=2)
    d.arc([cx - 5, cy - 12, cx + 5, cy + 12], 0, 360, fill=WHITE, width=2)
    d.line([cx - 12, cy, cx + 12, cy], fill=WHITE, width=2)


# ---- the 29 grid stories --------------------------------------------
# (tag, accent, headline, mini scene, band colour). Headlines stay
# under ~42 characters so they wrap to two 12 px lines in a tile.
TILES = [
    ("POLAND", RED, "NATO sends AWACS to Poland", mini_plane, (32, 58, 92)),
    ("TECH", GOLD, "Huang back; Megaspeed barred", mini_chip,
     (243, 236, 220)),
    ("MEXICO", NAVY, "Mexico to try 'Chapo Isidro' at home", mini_court,
     (226, 230, 238)),
    ("INDONESIA", RED, "Serang fire: 24 dead, 30 missing", mini_factory,
     (250, 232, 200)),
    ("SPORT", TEAL, "Chess title match begins in Geneva", mini_chess, TEAL),
    ("CHINA", RED, "US jury convicts Huawei on 10 counts", mini_gavel,
     (243, 236, 220)),
    ("HORMUZ", NAVY, "Iran says 4th tanker hit by a mine", mini_tanker, SEA),
    ("HORMUZ", TEAL, "IRGC says it hit ship in Hormuz", mini_ship, SEA),
    ("YEMEN", GOLD, "Houthis 60 km from Aden; army digs in", mini_map,
     (243, 236, 220)),
    ("SAUDI", RED, "Houthi drone hits Riyadh PIF Tower", mini_tower,
     (32, 58, 92)),
    ("GAZA", NAVY, "Israel kills Hamas security chief", mini_city,
     (226, 230, 238)),
    ("UKRAINE", TEAL, "Zelenskyy confirms ship strikes", mini_warship, SEA),
    ("IRAQ", GOLD, "Baghdad takes over Kurdish oilfields", mini_oil,
     (243, 236, 220)),
    ("BANGLADESH", RED, "Hasina plans Dec 16 return from exile", mini_plane,
     (64, 84, 138)),
    ("MALAYSIA", TEAL, "Malaysia to send 6,800 home in Dec", mini_ship,
     SEA),
    ("VIETNAM", RED, "Hanoi hotpot blast kills six", mini_flame,
     (250, 232, 200)),
    ("LIBYA", NAVY, "Haftar visits Turkey for first time", mini_flags,
     (226, 230, 238)),
    ("TURKEY", GOLD, "Turkish helicopter crash kills five", mini_heli,
     (64, 84, 138)),
    ("COLOMBIA", RED, "25 held hostage in Cartagena store", mini_building,
     (226, 230, 238)),
    ("COLOMBIA", GOLD, "Car bomb injures 23 in Colombia", mini_flame,
     (250, 232, 200)),
    ("GAZA", TEAL, "Gaza declares meningitis alert", mini_hospital,
     (240, 235, 220)),
    ("UK", NAVY, "UK sanctions Houthis, 4 officials", mini_doc,
     (226, 230, 238)),
    ("SENEGAL", GREEN, "Senegal regain Africa Cup title", mini_trophy,
     (243, 236, 220)),
    ("PHARMA", TEAL, "Sanofi to buy Insmed for $41bn", mini_pill,
     (240, 235, 220)),
    ("YEMEN", RED, "Saudi strikes kill 25, reports say", mini_bus,
     (250, 232, 200)),
    ("PACIFIC", NAVY, "Solomon Islands to scrap China pact", mini_globe, SEA),
    ("UK", GOLD, "Nuclear-test veterans inquiry", mini_doc,
     (226, 230, 238)),
    ("BELARUS", RED, "Lukashenko: fly with Zelenskyy to Moscow", mini_flags,
     (243, 236, 220)),
    ("CHINA", NAVY, "China probes Chen Jining", mini_doc,
     (226, 230, 238)),
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead: date is the biggest text -------------------------
    d.rectangle([0, 0, W, 94], fill=NAVY)
    d.rectangle([0, 94, W, 100], fill=GOLD)
    d.text((32, 12), "THE WORLD IN ONE DAY  •  WORLD NEWS",
           font=font(SANS_B, 16), fill=GOLD)
    d.text((32, 32), "TUESDAY 24 NOVEMBER 2026",
           font=font(SERIF_B, 46), fill=WHITE)
    d.text((32, 80), "One image, one day — 30 stories, as reported on "
           "24 November 2026",
           font=font(SANS, 15), fill=(205, 212, 226))

    # ---- hero headline ----------------------------------------------
    tag(d, 32, 112, "AIR ALERT  •  ULLEUNG ISLAND, SOUTH KOREA", RED)
    d.text((32, 146), "Russian jets trigger island alert",
           font=font(SERIF_B, 46), fill=INK)
    subf = font(SANS, 18)
    sub_lines = wrap(d, "Seoul scrambles fighters as Russian planes "
                        "approach Ulleung — the island's alert is "
                        "lifted in minutes.",
                     subf, 960)
    draw_lines(d, 32, 192, sub_lines, subf, GREY, 23)

    # ---- hero scene ---------------------------------------------------
    hero_dawn(d, 0, 250, W, 560)
    d.rectangle([0, 560, W, 566], fill=GOLD)

    # ---- the day in 29 more stories ----------------------------------
    d.text((32, 576), "MORE TODAY — 29 STORIES",
           font=font(SANS_B, 18), fill=RED)
    d.line([300, 586, 992, 586], fill=LINE, width=2)

    col_w, row_h = 159, 77
    for idx, (tag_text, accent, head, scene, bg) in enumerate(TILES):
        r, c = divmod(idx, 6)
        x0 = 16 + c * 167
        x1 = x0 + col_w
        y0 = 596 + r * 83
        y1 = y0 + row_h
        d.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=CARD,
                            outline=LINE, width=1)
        d.rectangle([x0 + 2, y0, x1 - 2, y0 + 4], fill=accent)
        scene(d, x0 + 2, y0 + 6, x1 - 2, y0 + 32, bg)
        d.text((x0 + 8, y0 + 35), tag_text, font=font(SANS_B, 10),
               fill=accent)
        hf = font(SERIF_B, 12)
        hl = wrap(d, head, hf, x1 - x0 - 16)[:2]
        draw_lines(d, x0 + 8, y0 + 47, hl, hf, INK, 14)

    # ---- footer tile: the 30th slot of the 6x5 grid ------------------
    fx0 = 16 + 5 * 167
    fy0 = 596 + 4 * 83
    fx1, fy1 = fx0 + col_w, fy0 + row_h
    d.rounded_rectangle([fx0, fy0, fx1, fy1], radius=8, fill=NAVY)
    cx = (fx0 + fx1) // 2
    d.text((cx, fy0 + 14), "24 NOV 2026", font=font(SANS_B, 16),
           fill=WHITE, anchor="ma")
    d.text((cx, fy0 + 36), "30 STORIES", font=font(SANS_B, 13),
           fill=GOLD, anchor="ma")
    d.text((cx, fy0 + 56), "ONE DAY · ONE IMAGE", font=font(SANS_B, 9),
           fill=(205, 212, 226), anchor="ma")

    d.text((512, 1011), "24 NOVEMBER 2026  •  SOURCES: REUTERS, AP, AFP, BBC",
           font=font(SANS_B, 12), fill=GREY, anchor="ma")

    img.save(OUT, format="PNG", optimize=True)
    print(f"wrote {OUT} {img.size} {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
