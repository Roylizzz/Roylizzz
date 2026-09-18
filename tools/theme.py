"""Shared palette and SVG helpers for every generated asset."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

DARK = {
    "name": "dark",
    "bg": "#07040D",
    "panel": "#0D0718",
    "panel2": "#150C26",
    "border": "#2E1A52",
    "grid": "#180E2B",
    "text": "#BDACE4",
    "dim": "#6C5A99",
    "accent": "#8B5CF6",
    "accent2": "#A855F7",
    "glow": "#C084FC",
    "hi": "#EDE9FE",
    "pink": "#F0ABFC",
}

LIGHT = {
    "name": "light",
    "bg": "#FBF9FF",
    "panel": "#FFFFFF",
    "panel2": "#F4EFFF",
    "border": "#DCCEFA",
    "grid": "#EDE6FD",
    "text": "#4B3781",
    "dim": "#8878B3",
    "accent": "#7C3AED",
    "accent2": "#9333EA",
    "glow": "#A855F7",
    "hi": "#2E1065",
    "pink": "#C026D3",
}

PALETTES = (DARK, LIGHT)

MONO = (
    "ui-monospace,'JetBrains Mono','Fira Code','Cascadia Mono',"
    "'Segoe UI Mono',Consolas,monospace"
)

# Colours that read well on both GitHub themes, used by theme-neutral assets.
NEUTRAL = {
    "accent": "#8B5CF6",
    "accent2": "#A855F7",
    "glow": "#C084FC",
    "dim": "#8B5CF6",
}

# Heat ramp for contribution squares, darkest -> brightest.
HEAT_DARK = ["#1A0F2E", "#4C1D95", "#6D28D9", "#8B5CF6", "#C084FC"]
HEAT_LIGHT = ["#EDE6FD", "#C4B5FD", "#A78BFA", "#7C3AED", "#5B21B6"]


def heat(pal: dict) -> list[str]:
    return HEAT_DARK if pal["name"] == "dark" else HEAT_LIGHT


def write(name: str, markup: str) -> None:
    ASSETS.mkdir(exist_ok=True)
    path = ASSETS / name
    path.write_text(markup, encoding="utf-8")
    print(f"  {path.relative_to(ROOT).as_posix():<44} {len(markup):>7,} bytes")


def svg(width: int, height: int, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" fill="none" role="img">{body}</svg>'
    )


def embed(path, x: float, y: float, width: float, height: float, extra: str = "") -> str:
    """Inline a local raster as a data URI so the SVG stays self-contained."""
    import base64
    import mimetypes

    data = base64.b64encode(Path(path).read_bytes()).decode()
    mime = mimetypes.guess_type(str(path))[0] or "image/jpeg"
    uri = f"data:{mime};base64,{data}"
    return (
        f'<image x="{x}" y="{y}" width="{width}" height="{height}" '
        f'preserveAspectRatio="xMidYMid slice" href="{uri}" xlink:href="{uri}"'
        f'{(" " + extra) if extra else ""}/>'
    )


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def mono(
    text: str,
    x: float,
    y: float,
    size: float,
    fill: str,
    weight: int = 400,
    anchor: str = "start",
    spacing: float | None = None,
    opacity: float | None = None,
    extra: str = "",
) -> str:
    bits = [
        f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}"',
        f'fill="{fill}" font-weight="{weight}" text-anchor="{anchor}"',
    ]
    if spacing is not None:
        bits.append(f'letter-spacing="{spacing}"')
    if opacity is not None:
        bits.append(f'opacity="{opacity}"')
    if extra:
        bits.append(extra)
    return " ".join(bits) + f">{esc(text)}</text>"


def card(pal: dict, width: int, height: int, radius: int = 14) -> str:
    """The shared card chrome: panel, border and the purple spine on the left."""
    return (
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="{radius}" '
        f'fill="{pal["panel"]}" stroke="{pal["border"]}" stroke-width="1.5"/>'
        f'<rect x="1" y="1" width="4" height="{height - 2}" rx="2" '
        f'fill="{pal["accent"]}" opacity="0.85"/>'
    )
