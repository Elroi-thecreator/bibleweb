"""
Devotional Verse of the Day & Scripture Image Card Generator.
Renders high-resolution 1080x1080 spiritual status cards with dual-language typography,
ornamental golden borders, HarfBuzz OpenType complex script shaping (for Tamil ligatures),
and citation banners using Pillow, uharfbuzz, and freetype-py.
"""

import io
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("whatsapp_gateway.card_generator")

try:
    import uharfbuzz as hb
    import freetype
    HAS_HARFBUZZ = True
except ImportError:
    HAS_HARFBUZZ = False
    logger.warning("uharfbuzz or freetype-py not available; falling back to basic layout")


def _is_tamil(text: str) -> bool:
    """Detects if string contains Tamil Unicode code points."""
    return any(0x0B80 <= ord(c) <= 0x0BFF for c in text)


def _resolve_font_paths() -> Tuple[Path, Path]:
    """Resolves font paths for Tamil and English Serif fonts."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    bundled_fonts_dir = base_dir / "static" / "fonts"

    if hasattr(sys, "_MEIPASS"):
        meipass_fonts = Path(sys._MEIPASS) / "static" / "fonts"
        if meipass_fonts.is_dir():
            bundled_fonts_dir = meipass_fonts

    # 1. Tamil / Mixed font (supports both Tamil and Latin)
    font_tamil = bundled_fonts_dir / "NotoSansTamil-Variable.ttf"
    if not font_tamil.exists():
        font_tamil = bundled_fonts_dir / "NotoSansTamil-Bold.ttf"
    if not font_tamil.exists():
        candidates = [
            "C:/Windows/Fonts/Nirmala.ttf",
            "C:/Windows/Fonts/NirmalaB.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansTamil-Regular.ttf",
        ]
        for c in candidates:
            if Path(c).exists():
                font_tamil = Path(c)
                break

    # 2. English Serif font
    font_serif = bundled_fonts_dir / "NotoSerif-Regular.ttf"
    if not font_serif.exists():
        candidates = [
            "C:/Windows/Fonts/georgia.ttf",
            "C:/Windows/Fonts/georgiab.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        ]
        for c in candidates:
            if Path(c).exists():
                font_serif = Path(c)
                break

    return font_tamil, font_serif


def _measure_line_width(text: str, font_path: str, font_size: int) -> int:
    """Measures horizontal advance width of shaped text line."""
    if not text.strip():
        return 0
    if HAS_HARFBUZZ and os.path.exists(font_path):
        try:
            with open(font_path, "rb") as f:
                font_data = f.read()
            blob = hb.Blob(font_data)
            hb_face = hb.Face(blob)
            hb_font = hb.Font(hb_face)
            hb_font.scale = (font_size * 64, font_size * 64)

            buf = hb.Buffer()
            buf.add_str(text)
            if _is_tamil(text):
                buf.script = "Taml"
                buf.language = "ta"
            else:
                buf.script = "Latn"
                buf.language = "en"
            buf.direction = "ltr"
            hb.shape(hb_font, buf)
            return sum(pos.x_advance >> 6 for pos in buf.glyph_positions)
        except Exception:
            pass

    return len(text) * int(font_size * 0.58)


def _wrap_text(text: str, font_path: str, font_size: int, max_width: int) -> List[str]:
    """Wraps text into multiple lines that fit within max_width pixels."""
    words = text.split()
    if not words:
        return []
    lines = []
    current_line = words[0]

    for word in words[1:]:
        test_line = f"{current_line} {word}"
        w = _measure_line_width(test_line, font_path, font_size)
        if w <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines


def _render_line(
    canvas: Image.Image,
    text: str,
    font_path: str,
    font_size: int,
    color: Tuple[int, int, int],
    y: int,
    center: bool = True,
) -> int:
    """Renders a text line onto the canvas with HarfBuzz OpenType shaping and FreeType rasterization."""
    width, height = canvas.size
    if HAS_HARFBUZZ and os.path.exists(font_path):
        try:
            face = freetype.Face(font_path)
            face.set_char_size(font_size * 64)

            with open(font_path, "rb") as f:
                font_data = f.read()
            blob = hb.Blob(font_data)
            hb_face = hb.Face(blob)
            hb_font = hb.Font(hb_face)
            hb_font.scale = (font_size * 64, font_size * 64)

            buf = hb.Buffer()
            buf.add_str(text)
            if _is_tamil(text):
                buf.script = "Taml"
                buf.language = "ta"
            else:
                buf.script = "Latn"
                buf.language = "en"
            buf.direction = "ltr"
            hb.shape(hb_font, buf)

            infos = buf.glyph_infos
            positions = buf.glyph_positions

            total_width = sum(pos.x_advance >> 6 for pos in positions)
            start_x = (width - total_width) // 2 if center else 50
            baseline = y + int(font_size * 0.9)

            cur_x = start_x
            for info, pos in zip(infos, positions):
                gid = info.codepoint
                face.load_glyph(gid, freetype.FT_LOAD_RENDER)
                slot = face.glyph
                bitmap = slot.bitmap

                gx = cur_x + (pos.x_offset >> 6) + slot.bitmap_left
                gy = baseline - (pos.y_offset >> 6) - slot.bitmap_top

                if bitmap.width > 0 and bitmap.rows > 0:
                    glyph_img = Image.frombytes("L", (bitmap.width, bitmap.rows), bytes(bitmap.buffer))
                    solid = Image.new("RGBA", (bitmap.width, bitmap.rows), color + (255,))
                    canvas.paste(solid, (gx, gy), glyph_img)

                cur_x += (pos.x_advance >> 6)
            return total_width
        except Exception as exc:
            logger.warning("HarfBuzz text rendering exception (%s); using basic fallback", exc)

    # Fallback to standard Pillow drawing
    draw = ImageDraw.Draw(canvas)
    try:
        fnt = ImageFont.truetype(font_path, font_size)
    except Exception:
        fnt = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=fnt)
    w = bbox[2] - bbox[0]
    start_x = (width - w) // 2 if center else 50
    draw.text((start_x, y), text, fill=color, font=fnt)
    return w


def generate_verse_card(
    ref_text: str,
    scripture_en: str,
    scripture_ta: str = "",
    width: int = 1080,
    height: int = 1080,
) -> bytes:
    """
    Renders an elegant 1080x1080 JPEG scripture card with HarfBuzz Tamil shaping,
    golden ornamental borders, and adaptive vertical centering.
    """
    p_tamil, p_serif = _resolve_font_paths()
    font_tamil = str(p_tamil)
    font_serif = str(p_serif)

    # 1. Base canvas with smooth vertical midnight gradient
    img = Image.new("RGB", (width, height), color=(10, 16, 30))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        ratio = y / height
        r = int(10 + 8 * (1 - abs(ratio - 0.5) * 2))
        g = int(16 + 14 * (1 - abs(ratio - 0.5) * 2))
        b = int(32 + 24 * (1 - abs(ratio - 0.5) * 2))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 2. Golden Ornamental Borders
    gold = (218, 165, 32)
    dark_gold = (140, 100, 20)
    white = (255, 255, 255)
    cream = (225, 235, 248)
    muted_gold = (240, 210, 120)

    margin = 44
    draw.rectangle([margin, margin, width - margin, height - margin], outline=gold, width=4)
    draw.rectangle([margin + 12, margin + 12, width - (margin + 12), height - (margin + 12)], outline=dark_gold, width=2)

    # Decorative corner squares
    corner_size = 18
    for cx, cy in [
        (margin + 6, margin + 6),
        (width - margin - 24, margin + 6),
        (margin + 6, height - margin - 24),
        (width - margin - 24, height - margin - 24),
    ]:
        draw.rectangle([cx, cy, cx + corner_size, cy + corner_size], outline=gold, width=2)

    # 3. Header: App & Faith Banner
    _render_line(img, "• HOLY BIBLE • பரிசுத்த வேதாகமம் •", font_tamil, 22, muted_gold, margin + 35)

    flourish_y = margin + 75
    draw.line([(width // 2 - 140, flourish_y), (width // 2 - 20, flourish_y)], fill=gold, width=2)
    draw.line([(width // 2 + 20, flourish_y), (width // 2 + 140, flourish_y)], fill=gold, width=2)
    draw.polygon([(width // 2, flourish_y - 6), (width // 2 + 6, flourish_y), (width // 2, flourish_y + 6), (width // 2 - 6, flourish_y)], fill=gold)

    # 4. Scripture Body Text & Centering
    content_width = width - (margin * 2 + 100)
    has_ta = bool(scripture_ta and scripture_ta.strip())
    has_en = bool(scripture_en and scripture_en.strip())

    avail_h = 830  # Vertical space between header flourish (y=150) and footer (y=980)

    if has_ta and has_en:
        # Dual-language layout
        ta_char_len = len(scripture_ta.strip())
        en_char_len = len(scripture_en.strip())
        is_long = ta_char_len > 120 or en_char_len > 140

        size_ta = 38 if is_long else 42
        size_en = 30 if is_long else 34
        lh_ta = 56 if is_long else 62
        lh_en = 44 if is_long else 50

        lines_ta = _wrap_text(scripture_ta.strip(), font_tamil, size_ta, content_width)
        if len(lines_ta) > 7:
            lines_ta = lines_ta[:7]
            lines_ta[-1] += "..."

        lines_en = _wrap_text(f'“{scripture_en.strip()}”', font_serif, size_en, content_width)
        if len(lines_en) > 6:
            lines_en = lines_en[:6]
            lines_en[-1] += "..."

        h_ta = len(lines_ta) * lh_ta
        h_sep = 40
        h_en = len(lines_en) * lh_en
        gap_ref = 36
        h_ref = 36

        total_h = h_ta + h_sep + h_en + gap_ref + h_ref
        start_y = 150 + max(20, (avail_h - total_h) // 2)

        y_cursor = start_y

        # Render Tamil Scripture lines
        for line in lines_ta:
            _render_line(img, line, font_tamil, size_ta, white, y_cursor)
            y_cursor += lh_ta

        # Ornate Gold Flourish Divider
        y_cursor += 10
        draw.line([(width // 2 - 80, y_cursor), (width // 2 - 15, y_cursor)], fill=dark_gold, width=1)
        draw.line([(width // 2 + 15, y_cursor), (width // 2 + 80, y_cursor)], fill=dark_gold, width=1)
        draw.polygon([(width // 2, y_cursor - 4), (width // 2 + 4, y_cursor), (width // 2, y_cursor + 4), (width // 2 - 4, y_cursor)], fill=gold)
        y_cursor += (h_sep - 10)

        # Render English Scripture lines
        for line in lines_en:
            _render_line(img, line, font_serif, size_en, cream, y_cursor)
            y_cursor += lh_en

        # Render Citation
        y_cursor += gap_ref
        ref_display = f"— {ref_text.strip()} —"
        _render_line(img, ref_display, font_tamil, 32, gold, y_cursor)

    else:
        # Single-language layout
        primary = scripture_ta.strip() if has_ta else scripture_en.strip()
        is_tamil_single = has_ta

        font_chosen = font_tamil if is_tamil_single else font_serif
        size_prim = 44 if len(primary) > 100 else 48
        lh_prim = 62 if len(primary) > 100 else 68

        lines = _wrap_text(f'“{primary}”', font_chosen, size_prim, content_width)
        if len(lines) > 8:
            lines = lines[:8]
            lines[-1] += "..."

        h_prim = len(lines) * lh_prim
        gap_ref = 46
        h_ref = 38
        total_h = h_prim + gap_ref + h_ref

        start_y = 150 + max(20, (avail_h - total_h) // 2)
        y_cursor = start_y

        for line in lines:
            _render_line(img, line, font_chosen, size_prim, white, y_cursor)
            y_cursor += lh_prim

        y_cursor += gap_ref
        ref_display = f"— {ref_text.strip()} —"
        _render_line(img, ref_display, font_tamil, 34, gold, y_cursor)

    # 5. Footer: Citation & Web Portal Branding
    footer_text = "Daily Bread • Scripture Status Card • elroi-bible.vercel.app"
    _render_line(img, footer_text, font_tamil, 18, (150, 165, 185), height - margin - 45)

    # 6. Save to high-quality JPEG
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=95, optimize=True)
    return buffer.getvalue()
