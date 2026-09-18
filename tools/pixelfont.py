"""Tiny 5x7 bitmap font used to draw the pixel-art headings of the profile.

Every glyph is seven rows of five characters. '#' paints a pixel, '.' skips it.
Horizontal runs are merged so the generated SVG stays small.
"""

from __future__ import annotations

GLYPH_W = 5
GLYPH_H = 7

_RAW: dict[str, str] = {
    "A": ".###.|#...#|#...#|#####|#...#|#...#|#...#",
    "B": "####.|#...#|#...#|####.|#...#|#...#|####.",
    "C": ".####|#....|#....|#....|#....|#....|.####",
    "D": "####.|#...#|#...#|#...#|#...#|#...#|####.",
    "E": "#####|#....|#....|####.|#....|#....|#####",
    "F": "#####|#....|#....|####.|#....|#....|#....",
    "G": ".###.|#...#|#....|#..##|#...#|#...#|.###.",
    "H": "#...#|#...#|#...#|#####|#...#|#...#|#...#",
    "I": "#####|..#..|..#..|..#..|..#..|..#..|#####",
    "J": "....#|....#|....#|....#|#...#|#...#|.###.",
    "K": "#...#|#..#.|#.#..|##...|#.#..|#..#.|#...#",
    "L": "#....|#....|#....|#....|#....|#....|#####",
    "M": "#...#|##.##|#.#.#|#...#|#...#|#...#|#...#",
    "N": "#...#|##..#|#.#.#|#..##|#...#|#...#|#...#",
    "O": ".###.|#...#|#...#|#...#|#...#|#...#|.###.",
    "P": "####.|#...#|#...#|####.|#....|#....|#....",
    "Q": ".###.|#...#|#...#|#...#|#.#.#|#..#.|.##.#",
    "R": "####.|#...#|#...#|####.|#.#..|#..#.|#...#",
    "S": ".####|#....|#....|.###.|....#|....#|####.",
    "T": "#####|..#..|..#..|..#..|..#..|..#..|..#..",
    "U": "#...#|#...#|#...#|#...#|#...#|#...#|.###.",
    "V": "#...#|#...#|#...#|#...#|#...#|.#.#.|..#..",
    "W": "#...#|#...#|#...#|#...#|#.#.#|##.##|#...#",
    "X": "#...#|#...#|.#.#.|..#..|.#.#.|#...#|#...#",
    "Y": "#...#|#...#|.#.#.|..#..|..#..|..#..|..#..",
    "Z": "#####|....#|...#.|..#..|.#...|#....|#####",
    "0": ".###.|#...#|#..##|#.#.#|##..#|#...#|.###.",
    "1": "..#..|.##..|..#..|..#..|..#..|..#..|.###.",
    "2": ".###.|#...#|....#|...#.|..#..|.#...|#####",
    "3": "####.|....#|....#|.###.|....#|....#|####.",
    "4": "#..#.|#..#.|#..#.|#####|...#.|...#.|...#.",
    "5": "#####|#....|####.|....#|....#|#...#|.###.",
    "6": ".###.|#....|#....|####.|#...#|#...#|.###.",
    "7": "#####|....#|...#.|..#..|.#...|.#...|.#...",
    "8": ".###.|#...#|#...#|.###.|#...#|#...#|.###.",
    "9": ".###.|#...#|#...#|.####|....#|....#|.###.",
    " ": ".....|.....|.....|.....|.....|.....|.....",
    ".": ".....|.....|.....|.....|.....|.##..|.##..",
    "·": ".....|.....|.##..|.##..|.....|.....|.....",
    "-": ".....|.....|.....|#####|.....|.....|.....",
    "_": ".....|.....|.....|.....|.....|.....|#####",
    ":": ".....|.##..|.##..|.....|.##..|.##..|.....",
    "/": "....#|....#|...#.|..#..|.#...|#....|#....",
    "!": "..#..|..#..|..#..|..#..|..#..|.....|..#..",
    "?": ".###.|#...#|....#|..##.|..#..|.....|..#..",
    "<": "...#.|..#..|.#...|#....|.#...|..#..|...#.",
    ">": ".#...|..#..|...#.|....#|...#.|..#..|.#...",
    "+": ".....|..#..|..#..|#####|..#..|..#..|.....",
    "'": "..#..|..#..|.....|.....|.....|.....|.....",
    "(": "...#.|..#..|.#...|.#...|.#...|..#..|...#.",
    ")": ".#...|..#..|...#.|...#.|...#.|..#..|.#...",
    "#": ".#.#.|#####|.#.#.|.#.#.|#####|.#.#.|.....",
    "@": ".###.|#...#|#.###|#.#.#|#.###|#....|.###.",
}

GLYPHS: dict[str, list[str]] = {}
for _char, _bits in _RAW.items():
    _rows = _bits.split("|")
    assert len(_rows) == GLYPH_H, f"glyph {_char!r} has {len(_rows)} rows"
    for _row in _rows:
        assert len(_row) == GLYPH_W, f"glyph {_char!r} row {_row!r} is not {GLYPH_W} wide"
    GLYPHS[_char] = _rows


def measure(text: str, scale: int = 4, tracking: int = 1) -> int:
    """Width in user units of `text` rendered at `scale`."""
    text = text.upper()
    if not text:
        return 0
    return (len(text) * (GLYPH_W + tracking) - tracking) * scale


def height(scale: int = 4) -> int:
    return GLYPH_H * scale


def pixels(text: str, x: int, y: int, scale: int = 4, tracking: int = 1):
    """Yield (x, y, w, h) rectangles for `text`, merging horizontal runs."""
    text = text.upper()
    cursor = x
    for char in text:
        rows = GLYPHS.get(char)
        if rows is None:
            rows = GLYPHS["?"]
        for row_index, row in enumerate(rows):
            col = 0
            while col < GLYPH_W:
                if row[col] == "#":
                    run = 1
                    while col + run < GLYPH_W and row[col + run] == "#":
                        run += 1
                    yield (
                        cursor + col * scale,
                        y + row_index * scale,
                        run * scale,
                        scale,
                    )
                    col += run
                else:
                    col += 1
        cursor += (GLYPH_W + tracking) * scale


def draw(
    text: str,
    x: int,
    y: int,
    scale: int = 4,
    tracking: int = 1,
    fill: str = "#8B5CF6",
    extra: str = "",
) -> str:
    """Render `text` as a single <g> of merged rectangles."""
    rects = "".join(
        f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}"/>'
        for rx, ry, rw, rh in pixels(text, x, y, scale, tracking)
    )
    return f'<g fill="{fill}"{(" " + extra) if extra else ""}>{rects}</g>'


def grid(
    rows: list[str],
    x: int,
    y: int,
    scale: int,
    palette: dict[str, str],
    extra: dict[str, str] | None = None,
) -> str:
    """Render a pixel-art grid. `rows` maps characters to colours via `palette`."""
    extra = extra or {}
    buckets: dict[str, list[str]] = {}
    for row_index, row in enumerate(rows):
        for col_index, key in enumerate(row):
            colour = palette.get(key)
            if colour is None:
                continue
            buckets.setdefault(key, []).append(
                f'<rect x="{x + col_index * scale}" y="{y + row_index * scale}"'
                f' width="{scale}" height="{scale}"/>'
            )
    out = []
    for key, rects in buckets.items():
        attrs = extra.get(key, "")
        out.append(
            f'<g fill="{palette[key]}"{(" " + attrs) if attrs else ""}>' + "".join(rects) + "</g>"
        )
    return "".join(out)
