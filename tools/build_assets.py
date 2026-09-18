"""Builds every hand-made SVG used by the profile README.

Run it after touching a colour, a copy line or a pixel grid:

    python tools/build_assets.py

Nothing here talks to the network: the whole visual identity is generated
locally so the profile never depends on a third party staying online.
"""

from __future__ import annotations

import json
import random

import pixelfont as pf
from theme import ROOT, DARK, LIGHT, NEUTRAL, card, embed, mono, svg, write

# --------------------------------------------------------------------------
# pixel art
# --------------------------------------------------------------------------

# 16x16 oni mask - the profile's sigil.
ONI = [
    "..mm........mm..",
    ".mmmm......mmmm.",
    ".mmmmmmeemmmmmm.",
    "mmmmmmmmmmmmmmmm",
    "mmdddmmmmmmdddmm",
    "mmeeemmmmmmeeemm",
    "mmmeeemmmmeeemmm",
    "mmmmmmmddmmmmmmm",
    "mmmmmmmmmmmmmmmm",
    ".mmmoooooooommm.",
    ".mmmooddddoommm.",
    "..mmmoooooommm..",
    "..mmmmmmmmmmmm..",
    "...mmmmmmmmmm...",
    "....mmmmmmmm....",
    "......mmmm......",
]

# 12x12 glyphs for the off-screen section.
GLYPHS_12 = {
    "chainsaw": [
        "............",
        "............",
        "......d.d.d.",
        ".bbbbbbbbbbb",
        ".bbbbcccccc.",
        ".bbbbbbbbbbb",
        ".bbbb.d.d.d.",
        ".bbbb.......",
        ".bb.........",
        ".bb.........",
        ".bbb........",
        "............",
    ],
    "notebook": [
        "............",
        ".ccbbbbbbbb.",
        ".ccbbbbbbbb.",
        ".ccbbdbbdbb.",
        ".ccbbbddbbb.",
        ".ccbbbddbbb.",
        ".ccbbdbbdbb.",
        ".ccbbbbbbbb.",
        ".ccbbbbbbbb.",
        ".ccbbbbbbbb.",
        ".cc.aaaaaaa.",
        "............",
    ],
    "axe": [
        "..c.....bb..",
        ".cc.....bb..",
        ".ccc....bb..",
        ".cccc...bb..",
        ".ccccccccb..",
        ".ccccccccb..",
        ".cccc...bb..",
        ".ccc....bb..",
        ".cc.....bb..",
        "..c.....bb..",
        "........bb..",
        "............",
    ],
    "hourglass": [
        ".cccccccccc.",
        ".c........c.",
        "..d......d..",
        "...d....d...",
        "....d..d....",
        ".....dd.....",
        "....b..b....",
        "...bb..bb...",
        "..bbbbbbbb..",
        ".b........b.",
        ".cccccccccc.",
        "............",
    ],
    "tarot": [
        "..aaaaaaaa..",
        "..abbbbbba..",
        "..ab....ba..",
        "..ab.dd.ba..",
        "..a.dddd.a..",
        "..a.dccd.a..",
        "..a.dddd.a..",
        "..ab.dd.ba..",
        "..ab....ba..",
        "..abbbbbba..",
        "..aaaaaaaa..",
        "............",
    ],
    "vinyl": [
        "....dddd....",
        "..dd....dd..",
        ".d........d.",
        ".d..cccc..d.",
        "d..c....c..d",
        "d..c.bb.c..d",
        "d..c.bb.c..d",
        "d..c....c..d",
        ".d..cccc..d.",
        ".d........d.",
        "..dd....dd..",
        "....dddd....",
    ],
    "staff": [
        "...ddd......",
        "..dcccd..d..",
        "..dcccd.....",
        "...ddd...d..",
        "....bb......",
        "....bb..d...",
        "....bb......",
        "....bb......",
        "....bb......",
        "...abba.....",
        "..aabbaa....",
        "............",
    ],
}

for _key, _rows in GLYPHS_12.items():
    assert len(_rows) == 12, _key
    for _row in _rows:
        assert len(_row) == 12, (_key, _row)

for _row in ONI:
    assert len(_row) == 16, _row


def oni_palette(pal: dict) -> dict[str, str]:
    return {
        "m": pal["accent"],
        "d": "#3B1E6E" if pal["name"] == "dark" else "#4C1D95",
        "e": pal["pink"],
        "o": pal["hi"] if pal["name"] == "dark" else "#FFFFFF",
    }


CARD_GLYPH_PALETTE = {
    "a": "#5B2E9E",
    "b": "#7C3AED",
    "c": "#C4B5FD",
    "d": "#F0ABFC",
}


# --------------------------------------------------------------------------
# hero
# --------------------------------------------------------------------------

NEOFETCH = [
    ("alias", "roylizzz"),
    ("role", "software developer"),
    ("stack", "c# · .net · react · typescript"),
    ("tools", "visual studio · vs code · git"),
    ("shell", "powershell · windows 11"),
    ("since", "2025 on github"),
]


def hero(pal: dict) -> str:
    W, H = 1000, 440
    dark = pal["name"] == "dark"
    out: list[str] = []

    out.append(
        "<defs>"
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{pal["bg"]}"/>'
        f'<stop offset="1" stop-color="{pal["panel2"]}"/></linearGradient>'
        f'<radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="{pal["accent2"]}" stop-opacity="{0.55 if dark else 0.30}"/>'
        f'<stop offset="1" stop-color="{pal["accent2"]}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="word" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{pal["glow"]}"/>'
        f'<stop offset="0.5" stop-color="{pal["accent2"]}"/>'
        f'<stop offset="1" stop-color="{pal["pink"]}"/></linearGradient>'
        '<filter id="soft" x="-60%" y="-60%" width="220%" height="220%">'
        '<feGaussianBlur stdDeviation="7"/></filter>'
        '<filter id="tiny" x="-60%" y="-60%" width="220%" height="220%">'
        '<feGaussianBlur stdDeviation="2.4"/></filter>'
        '<pattern id="grid" width="26" height="26" patternUnits="userSpaceOnUse">'
        f'<path d="M26 0H0V26" fill="none" stroke="{pal["grid"]}" stroke-width="1"/></pattern>'
        '<clipPath id="frame"><rect width="1000" height="440" rx="22"/></clipPath>'
        "</defs>"
    )

    out.append(
        "<style>"
        # no base opacity:0 -> if a renderer ignores CSS the text still shows
        ".fi{animation:fi .55s ease-out both}"
        "@keyframes fi{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:translateX(0)}}"
        ".bk{animation:bk 1.05s steps(1) infinite}@keyframes bk{50%{opacity:0}}"
        ".pl{animation:pl 3.2s ease-in-out infinite}@keyframes pl{0%,100%{opacity:.45}50%{opacity:1}}"
        ".tw{animation:tw 4.4s ease-in-out infinite}@keyframes tw{0%,100%{opacity:.12}50%{opacity:.85}}"
        ".pt{animation:pt 11s linear infinite;transform-origin:center}"
        "@keyframes pt{0%{transform:translate(0,-30px) rotate(0)}"
        "100%{transform:translate(26px,470px) rotate(220deg)}}"
        ".sw{animation:sw 5s ease-in-out infinite}@keyframes sw{0%,100%{opacity:.5}50%{opacity:1}}"
        "</style>"
    )

    out.append('<g clip-path="url(#frame)">')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#grid)" opacity="{0.9 if dark else 1}"/>')
    out.append('<ellipse cx="880" cy="40" rx="330" ry="200" fill="url(#halo)" class="pl"/>')
    out.append(
        '<ellipse cx="90" cy="430" rx="280" ry="170" fill="url(#halo)" class="pl" '
        'style="animation-delay:1.6s"/>'
    )

    random.seed(11)
    stars = []
    for i in range(46):
        sx = random.randint(8, W - 8)
        sy = random.randint(8, H - 8)
        size = random.choice([1, 1, 2, 2, 3])
        delay = round(random.uniform(0, 4.4), 2)
        stars.append(
            f'<rect x="{sx}" y="{sy}" width="{size}" height="{size}" class="tw" '
            f'style="animation-delay:{delay}s"/>'
        )
    out.append(f'<g fill="{pal["glow"]}">' + "".join(stars) + "</g>")

    # falling pixel petals
    petals = []
    for i, (px, delay, scale) in enumerate(
        [(150, 0, 5), (430, 2.6, 4), (690, 5.2, 6), (905, 7.4, 4), (300, 9.1, 5)]
    ):
        petals.append(
            f'<g class="pt" style="animation-delay:{delay}s">'
            f'<rect x="{px}" y="0" width="{scale}" height="{scale}" rx="1" '
            f'fill="{pal["pink"]}" opacity="{0.75 if dark else 0.55}"/>'
            f'<rect x="{px + scale}" y="{scale}" width="{scale}" height="{scale}" rx="1" '
            f'fill="{pal["accent2"]}" opacity="{0.55 if dark else 0.4}"/></g>'
        )
    out.append("".join(petals))
    out.append("</g>")

    # terminal frame
    out.append(
        f'<rect x="28" y="26" width="944" height="388" rx="16" fill="{pal["panel"]}" '
        f'fill-opacity="{0.86 if dark else 0.94}" stroke="{pal["border"]}" stroke-width="1.5"/>'
    )
    out.append(
        f'<path d="M28 42a16 16 0 0 1 16-16h912a16 16 0 0 1 16 16v22H28z" fill="{pal["panel2"]}"/>'
    )
    out.append(f'<path d="M28 64h944" stroke="{pal["border"]}" stroke-width="1.5"/>')
    for i, colour in enumerate([pal["pink"], pal["accent2"], pal["accent"]]):
        out.append(f'<circle cx="{54 + i * 20}" cy="45" r="5.5" fill="{colour}"/>')
    out.append(
        mono("roylizzz@github: ~/profile — neofetch", 128, 50, 12.5, pal["dim"], spacing=0.4)
    )

    # left column: the mask
    out.append(f'<path d="M322 86v300" stroke="{pal["border"]}" stroke-width="1.5"/>')
    mask_scale = 11
    mask_x = 175 - (16 * mask_scale) // 2
    mask_y = 132
    out.append(
        f'<rect x="{mask_x - 26}" y="{mask_y - 26}" width="{16 * mask_scale + 52}" '
        f'height="{16 * mask_scale + 52}" rx="18" fill="{pal["accent"]}" fill-opacity="0.06" '
        f'stroke="{pal["border"]}" stroke-width="1"/>'
    )
    out.append(
        f'<g filter="url(#soft)" opacity="{0.5 if dark else 0.28}">'
        + pf.grid(ONI, mask_x, mask_y, mask_scale, {"m": pal["accent2"], "e": pal["pink"]})
        + "</g>"
    )
    out.append(
        pf.grid(
            ONI,
            mask_x,
            mask_y,
            mask_scale,
            oni_palette(pal),
            extra={"e": 'class="pl"'},
        )
    )

    # right column
    x0 = 356
    word_scale = 8
    out.append(
        f'<g filter="url(#soft)" opacity="{0.55 if dark else 0.3}">'
        + pf.draw("ROYLIZZZ", x0, 92, word_scale, 1, pal["accent2"])
        + "</g>"
    )
    out.append(pf.draw("ROYLIZZZ", x0, 92, word_scale, 1, "url(#word)"))
    out.append(
        mono("DUVAN SALDARRIAGA", x0 + 2, 178, 13, pal["hi"], weight=600, spacing=6.2)
    )
    out.append(f'<rect x="{x0 + 2}" y="192" width="56" height="3" rx="1.5" fill="{pal["accent"]}"/>')
    out.append(
        mono(
            "builds desktop + web software, mostly in the .net world",
            x0 + 70,
            197,
            11.5,
            pal["dim"],
            spacing=0.2,
        )
    )
    out.append(
        f'<path d="M{x0} 214h584" stroke="{pal["border"]}" stroke-width="1.5" '
        'stroke-dasharray="3 5"/>'
    )

    y = 238
    for i, (key, value) in enumerate(NEOFETCH):
        delay = round(0.12 + i * 0.09, 2)
        out.append(
            f'<g class="fi" style="animation-delay:{delay}s">'
            + mono(key, x0 + 4, y, 13, pal["accent"], weight=600, spacing=1.4)
            + mono("│", x0 + 84, y, 13, pal["border"])
            + mono(value, x0 + 104, y, 13, pal["text"], spacing=0.3)
            + "</g>"
        )
        y += 24

    prompt_y = y + 8
    out.append(
        '<g class="fi" style="animation-delay:.72s">'
        + mono("roylizzz@github", x0 + 4, prompt_y, 13, pal["accent2"], weight=600)
        + mono(":~$", x0 + 4 + 15 * 7.82, prompt_y, 13, pal["dim"])
        + f'<rect x="{x0 + 175}" y="{prompt_y - 13}" width="9" height="14" '
        f'fill="{pal["glow"]}" class="bk"/>'
        + "</g>"
    )

    swatches = [
        "#2E1065",
        "#4C1D95",
        "#5B21B6",
        pal["accent"],
        pal["accent2"],
        pal["glow"],
        pal["pink"],
        pal["hi"],
    ]
    for i, colour in enumerate(swatches):
        out.append(
            f'<rect x="{608 + i * 24}" y="{prompt_y - 12}" width="18" height="10" rx="2" '
            f'fill="{colour}" stroke="{pal["border"]}" stroke-width="0.6" class="sw" '
            f'style="animation-delay:{round(i * 0.18, 2)}s"/>'
        )

    # corner brackets
    for path in [
        "M40 16h-24v24",
        "M960 16h24v24",
        "M40 424h-24v-24",
        "M960 424h24v-24",
    ]:
        out.append(
            f'<path d="{path}" stroke="{pal["accent"]}" stroke-width="2" opacity="0.55" '
            'stroke-linecap="round"/>'
        )

    return svg(W, H, "".join(out))


# --------------------------------------------------------------------------
# section headings
# --------------------------------------------------------------------------


def heading(title: str, subtitle: str) -> str:
    W, H = 760, 62
    scale = 5
    out = [
        "<defs>"
        '<linearGradient id="t" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{NEUTRAL["accent"]}"/>'
        f'<stop offset="1" stop-color="{NEUTRAL["glow"]}"/></linearGradient>'
        "</defs>"
    ]
    # pixel bracket
    out.append(
        f'<g fill="{NEUTRAL["accent2"]}">'
        '<rect x="0" y="6" width="6" height="6"/>'
        '<rect x="0" y="16" width="6" height="26" opacity="0.85"/>'
        '<rect x="0" y="46" width="6" height="6"/>'
        '<rect x="10" y="16" width="6" height="26" opacity="0.5"/>'
        "</g>"
    )
    text_x = 28
    out.append(pf.draw(title, text_x, 8, scale, 1, "url(#t)"))
    width = pf.measure(title, scale)
    out.append(
        mono(subtitle, text_x + 2, 56, 11, NEUTRAL["accent"], spacing=1.1, opacity=0.72)
    )
    line_x = text_x + width + 24
    out.append(
        f'<path d="M{line_x} 22h{W - line_x - 26}" stroke="{NEUTRAL["accent"]}" '
        'stroke-width="1.5" stroke-dasharray="2 6" opacity="0.5"/>'
    )
    out.append(
        f'<g fill="{NEUTRAL["glow"]}" opacity="0.8">'
        f'<rect x="{W - 18}" y="15" width="7" height="7" transform="rotate(45 {W - 14.5} 18.5)"/>'
        "</g>"
    )
    return svg(W, H, "".join(out))


# --------------------------------------------------------------------------
# pills
# --------------------------------------------------------------------------


def pill(text: str, tone: str = "accent") -> str:
    scale = 3
    tw = pf.measure(text, scale)
    W = tw + 30
    H = 36
    colour = NEUTRAL[tone]
    out = [
        f'<rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="8" '
        f'fill="{colour}" fill-opacity="0.13" stroke="{colour}" stroke-width="1.5" '
        'stroke-opacity="0.55"/>',
        f'<rect x="8" y="{H // 2 - 4}" width="4" height="8" rx="1" fill="{colour}"/>',
        pf.draw(text, 19, (H - pf.height(scale)) // 2 + 1, scale, 1, colour),
    ]
    return svg(W, H, "".join(out))


# --------------------------------------------------------------------------
# note strips
# --------------------------------------------------------------------------


def note_strip(text: str) -> str:
    """A dashed, theme-neutral strip for one-line asides."""
    W, H = 760, 46
    colour = NEUTRAL["accent"]
    out = [
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" fill="{colour}" '
        f'fill-opacity="0.07" stroke="{colour}" stroke-width="1.5" stroke-opacity="0.45" '
        'stroke-dasharray="4 6"/>',
        f'<g fill="{colour}"><rect x="18" y="{H // 2 - 6}" width="4" height="4"/>'
        f'<rect x="18" y="{H // 2}" width="4" height="4" opacity="0.6"/>'
        f'<rect x="{W - 22}" y="{H // 2 - 6}" width="4" height="4" opacity="0.6"/>'
        f'<rect x="{W - 22}" y="{H // 2}" width="4" height="4"/></g>',
        mono(text, W // 2, H // 2 + 4, 12, colour, anchor="middle", spacing=0.6, opacity=0.95),
    ]
    return svg(W, H, "".join(out))


# --------------------------------------------------------------------------
# divider
# --------------------------------------------------------------------------


def divider() -> str:
    W, H = 1000, 26
    out = [
        "<style>.mv{animation:mv 7s ease-in-out infinite}"
        "@keyframes mv{0%{transform:translateX(-300px)}50%{transform:translateX(300px)}"
        "100%{transform:translateX(-300px)}}</style>",
        "<defs>"
        '<linearGradient id="d" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{NEUTRAL["accent"]}" stop-opacity="0"/>'
        f'<stop offset="0.5" stop-color="{NEUTRAL["accent"]}" stop-opacity="1"/>'
        f'<stop offset="1" stop-color="{NEUTRAL["accent"]}" stop-opacity="0"/>'
        "</linearGradient></defs>",
        '<path d="M40 13h920" stroke="url(#d)" stroke-width="2"/>',
    ]
    cx = W // 2
    out.append(
        f'<g fill="{NEUTRAL["glow"]}">'
        f'<rect x="{cx - 4}" y="9" width="8" height="8" transform="rotate(45 {cx} 13)"/>'
        f'<rect x="{cx - 26}" y="10.5" width="5" height="5" transform="rotate(45 {cx - 23.5} 13)" opacity="0.6"/>'
        f'<rect x="{cx + 21}" y="10.5" width="5" height="5" transform="rotate(45 {cx + 23.5} 13)" opacity="0.6"/>'
        "</g>"
    )
    out.append(
        f'<g class="mv"><rect x="{cx - 1}" y="11" width="16" height="4" rx="2" '
        f'fill="{NEUTRAL["glow"]}" opacity="0.55"/></g>'
    )
    return svg(W, H, "".join(out))


# --------------------------------------------------------------------------
# off-screen cards
# --------------------------------------------------------------------------

COVERS = ROOT / "assets" / "covers"

# slug -> the line that is actually mine. Title, format, year and score come
# from assets/covers/meta.json, written by tools/fetch_covers.py.
WATCHLIST = [
    ("chainsaw-man", "CHAINSAW MAN", "Denji just wants a normal life. He never gets one."),
    ("death-note", "DEATH NOTE", "Still the sharpest chess match ever animated."),
    ("vinland-saga", "VINLAND SAGA", "Thorfinn's arc wrecked me. Farmland included."),
    ("rezero", "RE:ZERO", "Trial and error, except the errors really hurt."),
    ("lord-of-the-mysteries", "LORD OF THE MYSTERIES", "Klein's paranoia is basically my debug process."),
    ("mushoku-tensei", "MUSHOKU TENSEI", "A second run at life, with the consequences kept."),
]

FORMATS = {"TV": "ANIME", "MOVIE": "FILM", "OVA": "OVA", "MANGA": "MANGA", "NOVEL": "NOVEL"}


def load_meta() -> dict:
    path = COVERS / "meta.json"
    if not path.exists():
        raise SystemExit(
            "assets/covers/meta.json is missing - run: python tools/fetch_covers.py"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def wrap_title(title: str, room: int) -> tuple[list[str], int]:
    """One line when it fits, otherwise break on the space closest to the middle."""
    if pf.measure(title, 4) <= room:
        return [title], 4
    scale = 3
    words = title.split(" ")
    best, gap = 1, 10**9
    for cut in range(1, len(words)):
        widest = max(
            pf.measure(" ".join(words[:cut]), scale),
            pf.measure(" ".join(words[cut:]), scale),
        )
        if widest < gap:
            best, gap = cut, widest
    return [" ".join(words[:best]), " ".join(words[best:])], scale


def watch_card(slug: str, title: str, note: str, meta: dict) -> str:
    """A poster in a purple frame, its real metadata, and one line of mine."""
    W, H = 480, 200
    px, py, pw, ph = 18, 14, 116, 172
    out = [
        "<defs>"
        '<linearGradient id="c" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#150C28"/><stop offset="1" stop-color="#0A0513"/>'
        "</linearGradient>"
        '<linearGradient id="t" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#DDD1FF"/><stop offset="1" stop-color="#A855F7"/>'
        "</linearGradient>"
        '<linearGradient id="v" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0.45" stop-color="#0A0513" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#0A0513" stop-opacity="0.75"/>'
        "</linearGradient>"
        '<filter id="g" x="-40%" y="-40%" width="180%" height="180%">'
        '<feGaussianBlur stdDeviation="9"/></filter>'
        f'<clipPath id="poster"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10"/>'
        "</clipPath>"
        "</defs>",
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="url(#c)" '
        'stroke="#33205C" stroke-width="1.5"/>',
        f'<rect x="1" y="1" width="4" height="{H - 2}" rx="2" fill="#8B5CF6" opacity="0.85"/>',
        # the cover bleeds a soft purple glow behind itself
        f'<g filter="url(#g)" opacity="0.5"><rect x="{px + 8}" y="{py + 10}" '
        f'width="{pw - 16}" height="{ph - 20}" rx="12" fill="#7C3AED"/></g>',
        embed(COVERS / f"{slug}.jpg", px, py, pw, ph, 'clip-path="url(#poster)"'),
        f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10" fill="url(#v)"/>',
        f'<rect x="{px + 0.75}" y="{py + 0.75}" width="{pw - 1.5}" height="{ph - 1.5}" rx="10" '
        'fill="none" stroke="#A855F7" stroke-width="1.5" stroke-opacity="0.8"/>',
    ]

    tx = px + pw + 30
    room = W - tx - 24
    lines, title_scale = wrap_title(title, room)
    if len(lines) == 1:
        out.append(pf.draw(lines[0], tx, 34, title_scale, 1, "url(#t)"))
    else:
        out.append(pf.draw(lines[0], tx, 26, title_scale, 1, "url(#t)"))
        out.append(pf.draw(lines[1], tx, 50, title_scale, 1, "url(#t)"))

    kind = FORMATS.get(meta.get("format", ""), meta.get("format", ""))
    tag = " \u00b7 ".join(str(bit) for bit in (kind, meta.get("year")) if bit)
    out.append(mono(tag, tx + 2, 90, 10, "#8B5CF6", spacing=2.2, opacity=0.9))
    out.append(f'<path d="M{tx} 102h{W - tx - 26}" stroke="#2A1A4A" stroke-width="1"/>')
    out.append(mono(note, tx, 124, 10.5, "#9C8AC7", spacing=0.1))

    score = meta.get("score")
    if score:
        bar_w = W - tx - 26
        out.append(mono("anilist score", tx, 158, 9.5, "#6C5A99", spacing=1.4))
        out.append(mono(str(score), tx + bar_w, 158, 11, "#C4B5FD", weight=700, anchor="end"))
        out.append(
            f'<rect x="{tx}" y="166" width="{bar_w}" height="6" rx="3" '
            'fill="#8B5CF6" opacity="0.16"/>'
        )
        out.append(
            f'<rect x="{tx}" y="166" width="{bar_w * score / 100:.1f}" height="6" rx="3" '
            'fill="#A855F7"/>'
        )
    return svg(W, H, "".join(out))


# --------------------------------------------------------------------------
# character strip
# --------------------------------------------------------------------------


def characters(meta: dict) -> str:
    """Six circular portraits - the most-favourited character of each title."""
    W, H = 760, 172
    size, gap = 96, 28
    total = len(WATCHLIST) * size + (len(WATCHLIST) - 1) * gap
    x0 = (W - total) // 2
    out = [
        "<defs>"
        '<linearGradient id="r" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{NEUTRAL["glow"]}"/>'
        f'<stop offset="1" stop-color="{NEUTRAL["accent"]}"/></linearGradient>'
        '<filter id="g" x="-50%" y="-50%" width="200%" height="200%">'
        '<feGaussianBlur stdDeviation="7"/></filter>'
    ]
    for index in range(len(WATCHLIST)):
        cx = x0 + index * (size + gap) + size // 2
        out.append(
            f'<clipPath id="c{index}"><circle cx="{cx}" cy="{14 + size // 2}" '
            f'r="{size // 2}"/></clipPath>'
        )
    out.append("</defs>")

    for index, (slug, _, _) in enumerate(WATCHLIST):
        x = x0 + index * (size + gap)
        cx, cy = x + size // 2, 14 + size // 2
        face = COVERS / f"{slug}-face.jpg"
        out.append(
            f'<g filter="url(#g)" opacity="0.45"><circle cx="{cx}" cy="{cy}" '
            f'r="{size // 2 - 2}" fill="{NEUTRAL["accent"]}"/></g>'
        )
        if face.exists():
            out.append(embed(face, x, 14, size, size, f'clip-path="url(#c{index})"'))
        out.append(
            f'<circle cx="{cx}" cy="{cy}" r="{size // 2 - 1}" fill="none" '
            'stroke="url(#r)" stroke-width="2.5"/>'
        )
        name = meta.get(slug, {}).get("character", "").split(" ")[0].upper() or "?"
        scale = 2 if pf.measure(name, 2) <= size + gap - 6 else 1
        out.append(
            pf.draw(name, cx - pf.measure(name, scale) // 2, 128, scale, 1, NEUTRAL["accent"])
        )
    out.append(
        mono(
            "most-favourited character of each, straight from anilist",
            W // 2,
            160,
            10.5,
            NEUTRAL["accent"],
            anchor="middle",
            spacing=1.2,
            opacity=0.75,
        )
    )
    return svg(W, H, "".join(out))


# --------------------------------------------------------------------------
# now playing fallback
# --------------------------------------------------------------------------


def nowplaying(pal: dict) -> str:
    """Shown until a Spotify uid is wired in - see SETUP.md step 2."""
    W, H = 480, 150
    out = [
        "<style>"
        ".spin{animation:spin 6s linear infinite;transform-origin:96px 75px}"
        "@keyframes spin{to{transform:rotate(360deg)}}"
        ".eq rect{animation:eq 1.4s ease-in-out infinite;transform-box:fill-box;transform-origin:center bottom}"
        "@keyframes eq{0%,100%{transform:scaleY(.3)}50%{transform:scaleY(1)}}"
        "</style>",
        card(pal, W, H),
    ]
    scale = 6
    gx, gy = 96 - 6 * scale, 75 - 6 * scale
    out.append(
        f'<rect x="{gx - 14}" y="{gy - 14}" width="{12 * scale + 28}" '
        f'height="{12 * scale + 28}" rx="12" fill="{pal["accent"]}" fill-opacity="0.08" '
        f'stroke="{pal["border"]}" stroke-width="1"/>'
    )
    out.append(
        '<g class="spin">'
        + pf.grid(
            GLYPHS_12["vinyl"],
            gx,
            gy,
            scale,
            {"b": pal["pink"], "c": pal["accent"], "d": pal["accent2"]},
        )
        + "</g>"
    )

    tx = 176
    out.append(pf.draw("NOT PLAYING", tx, 34, 3, 1, pal["accent2"]))
    out.append(mono("spotify · nothing on the wire", tx, 72, 11, pal["dim"]))
    for i, bar in enumerate([10, 20, 14, 26, 18, 24, 12, 22]):
        out.append(
            f'<g class="eq"><rect x="{tx + i * 12}" y="{104 - bar}" width="7" height="{bar}" '
            f'rx="2" fill="{pal["accent"]}" opacity="{0.35 + (i % 3) * 0.2:.2f}" '
            f'style="animation-delay:{round(i * 0.11, 2)}s"/></g>'
        )
    out.append(f'<path d="M{tx} 116h{W - tx - 26}" stroke="{pal["border"]}" stroke-width="1"/>')
    out.append(mono("connect it — SETUP.md step 2", tx, 134, 10.5, pal["accent"]))
    return svg(W, H, "".join(out))


# --------------------------------------------------------------------------
# footer
# --------------------------------------------------------------------------


def footer(pal: dict) -> str:
    W, H = 1000, 190
    dark = pal["name"] == "dark"
    out = [
        "<defs>"
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{pal["bg"]}" stop-opacity="0"/>'
        f'<stop offset="0.45" stop-color="{pal["panel2"]}" stop-opacity="{0.9 if dark else 1}"/>'
        f'<stop offset="1" stop-color="{pal["bg"]}"/></linearGradient>'
        '<clipPath id="fr"><rect width="1000" height="190" rx="22"/></clipPath>'
        '<filter id="soft" x="-60%" y="-60%" width="220%" height="220%">'
        '<feGaussianBlur stdDeviation="6"/></filter>'
        "</defs>",
        "<style>"
        ".w1{animation:w1 14s linear infinite}@keyframes w1{to{transform:translateX(-200px)}}"
        ".w2{animation:w2 19s linear infinite}@keyframes w2{to{transform:translateX(200px)}}"
        ".tw{animation:tw 4s ease-in-out infinite}@keyframes tw{0%,100%{opacity:.15}50%{opacity:.9}}"
        ".pl{animation:pl 3s ease-in-out infinite}@keyframes pl{0%,100%{opacity:.5}50%{opacity:1}}"
        "</style>",
    ]
    out.append('<g clip-path="url(#fr)">')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')

    random.seed(29)
    stars = "".join(
        f'<rect x="{random.randint(10, W - 10)}" y="{random.randint(6, 120)}" '
        f'width="{random.choice([1, 2, 2, 3])}" height="{random.choice([1, 2, 2, 3])}" '
        f'class="tw" style="animation-delay:{round(random.uniform(0, 4), 2)}s"/>'
        for _ in range(38)
    )
    out.append(f'<g fill="{pal["glow"]}">{stars}</g>')

    out.append(
        f'<g class="w1"><path d="M-200 140c110-26 210 22 320 4s210-46 320-24 210 40 320 20 '
        f'210-42 320-22v92H-200z" fill="{pal["accent"]}" opacity="{0.18 if dark else 0.12}"/></g>'
    )
    out.append(
        f'<g class="w2"><path d="M-200 158c120-20 200 26 320 12s200-38 320-18 210 34 320 14 '
        f'200-36 320-16v90H-200z" fill="{pal["accent2"]}" opacity="{0.26 if dark else 0.16}"/></g>'
    )
    out.append("</g>")

    mask_scale = 4
    mx = W // 2 - (16 * mask_scale) // 2
    out.append(
        f'<g filter="url(#soft)" opacity="0.6">'
        + pf.grid(ONI, mx, 26, mask_scale, {"m": pal["accent2"], "e": pal["pink"]})
        + "</g>"
    )
    out.append(
        pf.grid(ONI, mx, 26, mask_scale, oni_palette(pal), extra={"e": 'class="pl"'})
    )

    title = "THANKS FOR SCROLLING"
    scale = 4
    out.append(
        pf.draw(title, W // 2 - pf.measure(title, scale) // 2, 106, scale, 1, pal["accent2"])
    )
    out.append(
        mono(
            "roylizzz · built by hand, pixel by pixel",
            W // 2,
            156,
            11.5,
            pal["dim"],
            anchor="middle",
            spacing=2.4,
        )
    )
    out.append(
        f'<path d="M300 172h400" stroke="{pal["accent"]}" stroke-width="1" '
        'stroke-dasharray="2 6" opacity="0.45"/>'
    )
    return svg(W, H, "".join(out))


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------

HEADINGS = {
    "about": ("ABOUT", ""),
    "stack": ("STACK", ""),
    "signals": ("SIGNALS", ""),
    "offscreen": ("OFF SCREEN", ""),
    "connect": ("CONNECT", ""),
}

NOTES = {}

PILLS = [
    ("now", "NOW"),
    ("building", "BUILDING"),
    ("offscreen", "OFF SCREEN"),
    ("core", "CORE"),
    ("toolbelt", "TOOLBELT"),
    ("visitors", "VISITORS"),
    ("nowplaying", "NOW PLAYING"),
    ("contributions", "CONTRIBUTIONS"),
    ("cast", "CAST"),
    ("github", "GITHUB"),
    ("linkedin", "LINKEDIN"),
    ("email", "EMAIL"),
]


def main() -> None:
    print("building assets...")
    for pal in (DARK, LIGHT):
        write(f"hero-{pal['name']}.svg", hero(pal))
    for key, (title, subtitle) in HEADINGS.items():
        write(f"heading-{key}.svg", heading(title, subtitle))
    for slug, label in PILLS:
        write(f"pill-{slug}.svg", pill(label))
    write("divider.svg", divider())
    for slug, text in NOTES.items():
        write(f"note-{slug}.svg", note_strip(text))
    meta = load_meta()
    for slug, title, note in WATCHLIST:
        write(f"watch-{slug}.svg", watch_card(slug, title, note, meta[slug]))
    write("characters.svg", characters(meta))
    for pal in (DARK, LIGHT):
        write(f"nowplaying-{pal['name']}.svg", nowplaying(pal))
    print("done.")


if __name__ == "__main__":
    main()
