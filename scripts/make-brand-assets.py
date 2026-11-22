#!/usr/bin/env python3
"""Regenerate the TechyLili brand raster assets for the Android app.

Mirrors the iOS fork's scripts/make-brand-assets.py: the same mark (brush hiragana
て, "te" of Techy, in Yuji Syuku calligraphy) and the same TECHYLILI wordmark
(Archivo Black), applied to the surfaces this app ships:

- tv_launcher_icon.png   320x320  TV flavor's full-bleed tile: white て on black.
- tv_banner_art.png       320x180  Leanback row banner: the て accent mark alone,
                                    centered on near-black (no wordmark — the app's
                                    name already sits beside the banner in the row).
- anilili_launcher.png   1254x1254  Adaptive-icon foreground: て in #8872EF on black,
                                    sized like the upstream あ it replaces.
- mipmap-*/ic_launcher*.png          Legacy launcher tiles at each density: the original
                                    file's own alpha mask is reused as the tile shape,
                                    redrawn black with the て accent inside it.
- anilili_header_wordmark.png        The TECHYLILI wordmark, white alpha mask (546x130
                                    upstream, this file is 987x130 at the same 130 height).

The monochrome adaptive-icon glyph (a play triangle in miruro_accent) is brand
neutral and is intentionally left alone.

Fonts are SIL OFL, fetched on first run into scripts/brand-fonts/ (override with
TECHYLILI_FONT_DIR):

- Yuji Syuku   https://raw.githubusercontent.com/google/fonts/main/ofl/yujisyuku/YujiSyuku-Regular.ttf
- Archivo Black https://raw.githubusercontent.com/google/fonts/main/ofl/archivoblack/ArchivoBlack-Regular.ttf

Run:  python3 scripts/make-brand-assets.py
"""

import os
import shutil
import urllib.request
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = Path(os.environ.get("TECHYLILI_FONT_DIR") or Path(__file__).resolve().parent / "brand-fonts")

FONT_URLS = {
    "YujiSyuku-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/yujisyuku/YujiSyuku-Regular.ttf",
    "ArchivoBlack-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/archivoblack/ArchivoBlack-Regular.ttf",
}

ACCENT = (136, 114, 239)   # #8872EF upstream launcher mark color
BANNER_BG = (7, 5, 15)     # #07050f upstream banner ground
WHITE = (255, 255, 255)
RESAMPLE = Image.LANCZOS  # type: ignore[attr-defined]  # PIL 8.x constant


def ensure_fonts() -> dict:
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    fonts = {}
    for name, url in FONT_URLS.items():
        path = FONT_DIR / name
        if not path.exists():
            print(f"downloading {name} ...")
            urllib.request.urlretrieve(url, path)
        fonts[name] = path
    return fonts


def glyph_ink(font_path: Path, glyph: str = "て", size: int = 1000) -> Image.Image:
    """Render one character to a tight-bbox grayscale mask."""
    font = ImageFont.truetype(str(font_path), size)
    canvas = Image.new("L", (3600, 3600), 0)
    draw = ImageDraw.Draw(canvas)
    draw.text((1800, 1800), glyph, font=font, fill=255, anchor="mm")
    return canvas.crop(canvas.getbbox())


def wordmark_ink(font_path: Path, text: str = "TECHYLILI", size: int = 300) -> Image.Image:
    font = ImageFont.truetype(str(font_path), size)
    canvas = Image.new("L", (len(text) * 700, 1000), 0)
    draw = ImageDraw.Draw(canvas)
    draw.text((canvas.width // 2, canvas.height // 2), text, font=font, fill=255, anchor="mm")
    return canvas.crop(canvas.getbbox())


def mask_through(alpha: Image.Image, ink: Image.Image, box: tuple, color: tuple) -> Image.Image:
    """Paste a glyph mask, clipped to an existing alpha mask, onto an RGBA canvas."""
    bx0, by0, bx1, by1 = box
    bw, bh = bx1 - bx0, by1 - by0
    scale = min(bw / ink.width, bh / ink.height)
    ink = ink.resize((max(1, round(ink.width * scale)), max(1, round(ink.height * scale))), RESAMPLE)
    glyph = Image.new("L", alpha.size, 0)
    glyph.paste(ink, (round(bx0 + (bw - ink.width) / 2), round(by0 + (bh - ink.height) / 2)))
    out = Image.new("RGBA", alpha.size, (0, 0, 0, 0))
    tile = Image.new("RGBA", alpha.size, (0, 0, 0, 255))
    out.alpha_composite(tile)  # black tile under the original mask
    solid = Image.new("RGBA", alpha.size, color + (255,))
    clipped = ImageChops.darker(glyph, alpha)  # glyph confined to the tile mask
    out.paste(solid, (0, 0), clipped)
    out.putalpha(alpha)
    return out


def main() -> None:
    fonts = ensure_fonts()
    mark = glyph_ink(fonts["YujiSyuku-Regular.ttf"])
    wm = wordmark_ink(fonts["ArchivoBlack-Regular.ttf"])

    # ---- TV flavor tile: white て on an opaque black square
    tile = Image.new("RGBA", (320, 320), (0, 0, 0, 255))
    ink = mark.resize((round(mark.width * 180 / mark.height), 180), RESAMPLE)
    layer = Image.new("RGBA", tile.size, WHITE + (255,))
    m = Image.new("L", tile.size, 0)
    m.paste(ink, ((320 - ink.width) // 2, (320 - ink.height) // 2))
    tile.paste(layer, (0, 0), m)
    out = ROOT / "app/src/tv/res/drawable-nodpi/tv_launcher_icon.png"
    tile.save(out)
    print(f"tv_launcher_icon -> {out.relative_to(ROOT)} {tile.size}")

    # ---- leanback banner: the て mark alone, centered. The wordmark reads as clutter
    # at TV-row size, and the launcher already prints the app name beside the banner.
    banner = Image.new("RGB", (320, 180), BANNER_BG)
    g = mark.resize((round(mark.width * 140 / mark.height), 140), RESAMPLE)
    gm = Image.new("L", banner.size, 0)
    gm.paste(g, ((320 - g.width) // 2, (180 - g.height) // 2))
    banner.paste(Image.new("RGB", banner.size, ACCENT), (0, 0), gm)
    out = ROOT / "app/src/main/res/drawable-nodpi/tv_banner_art.png"
    banner.save(out)
    print(f"tv_banner_art    -> {out.relative_to(ROOT)} {banner.size}")

    # ---- adaptive-icon foreground: て in the accent on black, like the upstream あ
    fg = Image.new("RGB", (1254, 1254), (0, 0, 0))
    ink = mark.resize((round(mark.width * 575 / mark.height), 575), RESAMPLE)
    m = Image.new("L", fg.size, 0)
    m.paste(ink, ((1254 - ink.width) // 2, (1254 - ink.height) // 2))
    fg.paste(Image.new("RGB", fg.size, ACCENT), (0, 0), m)
    out = ROOT / "app/src/main/res/drawable/anilili_launcher.png"
    fg.save(out)
    print(f"launcher fg      -> {out.relative_to(ROOT)} {fg.size}")

    # ---- legacy mipmap tiles: original alpha reused as the tile shape, て inside
    for res_dir in sorted((ROOT / "app/src/main/res").glob("mipmap-*")):
        for name in ("ic_launcher.png", "ic_launcher_round.png"):
            path = res_dir / name
            if not path.exists():
                continue
            original = Image.open(path).convert("RGBA")
            alpha = original.split()[3]
            size = original.size
            box = (round(size[0] * 0.18), round(size[1] * 0.18),
                   round(size[0] * 0.82), round(size[1] * 0.82))
            redone = mask_through(alpha, mark, box, ACCENT)
            redone.save(path)
            print(f"legacy tile      -> {path.relative_to(ROOT)} {redone.size}")

    # ---- header wordmark: the TECHYLILI lockup, white alpha mask
    src = ROOT.parent / "iosrepo1" / "Sources" / "Anilili" / "Resources" / "Wordmark.png"
    dest = ROOT / "app/src/main/res/drawable-nodpi/anilili_header_wordmark.png"
    if src.exists():
        shutil.copyfile(src, dest)
        print(f"header wordmark  -> {dest.relative_to(ROOT)} (copied from the iOS fork's)")
    else:
        cap = 130
        ink = wm.resize((round(wm.width * cap / wm.height), cap), RESAMPLE)
        canvas = Image.new("L", (ink.width + 12, cap + 11), 0)
        canvas.paste(ink, (6, 6))
        out_img = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
        out_img.putalpha(canvas)
        out_img.save(dest)
        print(f"header wordmark  -> {dest.relative_to(ROOT)} {out_img.size}")


if __name__ == "__main__":
    main()
