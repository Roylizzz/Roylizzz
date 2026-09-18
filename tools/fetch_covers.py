"""Downloads cover art and character portraits from AniList.

Run once (or when the watchlist changes):

    python tools/fetch_covers.py

Images land in assets/covers/ already cropped and resized, plus a meta.json
with the real format/year/score. build_assets.py embeds them into the cards,
so the README never hotlinks anyone's CDN.
"""

from __future__ import annotations

import io
import json
import time
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
COVERS = ROOT / "assets" / "covers"

API = "https://graphql.anilist.co"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
)
QUERY = """
query($search: String, $type: MediaType) {
  Media(search: $search, type: $type) {
    title { romaji english }
    format
    startDate { year }
    status
    averageScore
    coverImage { extraLarge large }
    characters(sort: FAVOURITES_DESC, perPage: 1) {
      nodes { name { full } image { large } }
    }
  }
}
"""

# slug -> (search term, AniList media type)
WATCHLIST = [
    ("chainsaw-man", "Chainsaw Man", "MANGA"),
    ("death-note", "Death Note", "ANIME"),
    ("vinland-saga", "Vinland Saga", "MANGA"),
    ("rezero", "Re:Zero kara Hajimeru Isekai Seikatsu", "ANIME"),
    ("lord-of-the-mysteries", "Lord of the Mysteries", "MANGA"),
    ("mushoku-tensei", "Mushoku Tensei: Isekai Ittara Honki Dasu", "ANIME"),
]

COVER_SIZE = (232, 344)  # 2x of the slot in the card
FACE_SIZE = (168, 168)


def query(search: str, media_type: str) -> dict:
    payload = json.dumps({"query": QUERY, "variables": {"search": search, "type": media_type}})
    request = urllib.request.Request(
        API,
        data=payload.encode(),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": UA,
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = json.load(response)
    if body.get("errors"):
        raise RuntimeError(body["errors"])
    return body["data"]["Media"]


def grab(url: str) -> Image.Image:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=30) as response:
        return Image.open(io.BytesIO(response.read())).convert("RGB")


def cover_crop(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Centre-crop to the target aspect ratio, then resize."""
    target = size[0] / size[1]
    width, height = image.size
    if width / height > target:
        new_width = int(height * target)
        left = (width - new_width) // 2
        image = image.crop((left, 0, left + new_width, height))
    else:
        new_height = int(width / target)
        top = int((height - new_height) * 0.12)  # faces sit high on posters
        top = max(0, min(top, height - new_height))
        image = image.crop((0, top, width, top + new_height))
    return image.resize(size, Image.LANCZOS)


def main() -> None:
    COVERS.mkdir(parents=True, exist_ok=True)
    meta = {}
    for slug, search, media_type in WATCHLIST:
        print(f"  {slug:<24} ", end="", flush=True)
        media = query(search, media_type)

        cover = cover_crop(grab(media["coverImage"]["extraLarge"]), COVER_SIZE)
        cover.save(COVERS / f"{slug}.jpg", quality=84, optimize=True)

        entry = {
            "title": media["title"]["english"] or media["title"]["romaji"],
            "format": media["format"],
            "year": (media["startDate"] or {}).get("year"),
            "status": media["status"],
            "score": media["averageScore"],
        }

        nodes = media["characters"]["nodes"]
        if nodes:
            face = cover_crop(grab(nodes[0]["image"]["large"]), FACE_SIZE)
            face.save(COVERS / f"{slug}-face.jpg", quality=84, optimize=True)
            entry["character"] = nodes[0]["name"]["full"]

        meta[slug] = entry
        print(f"{entry['title']} ({entry['format']}, {entry['year']})")
        time.sleep(1.2)  # AniList asks for <= 90 req/min

    (COVERS / "meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"\nwrote {len(meta)} entries to {(COVERS / 'meta.json').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
