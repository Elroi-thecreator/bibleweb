"""
Devotional Verse of the Day & Scripture Image Card Generator.
Renders high-resolution 1080x1080 spiritual status cards with dual-language typography,
ornamental golden borders, and citation banners using Pillow.
"""

import io
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("whatsapp_gateway.card_generator")


def _get_font(font_family: str, size: int) -> ImageFont.ImageFont:
    """
    Safely loads TrueType fonts with priority for bundled repository fonts in static/fonts/,
    falling back to system fonts and default font if needed.
    """
    # 1. Resolve project root and static/fonts directory
    base_dir = Path(__file__).resolve().parent.parent.parent
    bundled_fonts_dir = base_dir / "static" / "fonts"

    # Also support PyInstaller frozen path
    if hasattr(sys, "_MEIPASS"):
        meipass_fonts = Path(sys._MEIPASS) / "static" / "fonts"
        if meipass_fonts.is_dir():
            bundled_fonts_dir = meipass_fonts

    font_candidates = {
        "tamil": [
            bundled_fonts_dir / "NotoSansTamil-Variable.ttf",
            bundled_fonts_dir / "NotoSansTamil-Bold.ttf",
            bundled_fonts_dir / "NotoSansTamil-Regular.ttf",
            "C:/Windows/Fonts/Nirmala.ttf",
            "C:/Windows/Fonts/NirmalaB.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansTamil-Regular.ttf",
        ],
        "mixed": [
            bundled_fonts_dir / "NotoSansTamil-Variable.ttf",
            bundled_fonts_dir / "NotoSansTamil-Bold.ttf",
            bundled_fonts_dir / "NotoSansTamil-Regular.ttf",
            "C:/Windows/Fonts/Nirmala.ttf",
            "C:/Windows/Fonts/NirmalaB.ttf",
        ],
        "serif": [
            bundled_fonts_dir / "NotoSerif-Regular.ttf",
            bundled_fonts_dir / "NotoSerif-Bold.ttf",
            bundled_fonts_dir / "NotoSansTamil-Variable.ttf",
            "C:/Windows/Fonts/georgia.ttf",
            "C:/Windows/Fonts/georgiab.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        ],
        "sans": [
            bundled_fonts_dir / "NotoSansTamil-Variable.ttf",
            bundled_fonts_dir / "NotoSansTamil-Regular.ttf",
            bundled_fonts_dir / "NotoSerif-Regular.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ],
    }

    candidates = font_candidates.get(font_family, font_candidates["mixed"])
    for p in candidates:
        path_obj = Path(p)
        if path_obj.exists():
            try:
                return ImageFont.truetype(str(path_obj), size)
            except Exception:
                continue

    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.ImageDraw) -> List[str]:
    """Wraps text into multiple lines that fit within max_width pixels."""
    words = text.split()
    if not words:
        return []
    lines = []
    current_line = words[0]

    for word in words[1:]:
        test_line = f"{current_line} {word}"
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines


def generate_verse_card(
    ref_text: str,
    scripture_en: str,
    scripture_ta: str = "",
    width: int = 1080,
    height: int = 1080,
) -> bytes:
    """
    Renders an elegant 1080x1080 JPEG scripture card.
    Perfect for sharing on WhatsApp status, Instagram, or community groups.
    """
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

    # 3. Header: App & Faith Banner (Mixed font supporting both Latin and Tamil)
    font_header = _get_font("mixed", 22)
    header_text = "• HOLY BIBLE • பரிசுத்த வேதாகமம் •"
    h_bbox = draw.textbbox((0, 0), header_text, font=font_header)
    h_w = h_bbox[2] - h_bbox[0]
    draw.text(((width - h_w) // 2, margin + 35), header_text, fill=muted_gold, font=font_header)

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
        # Adaptive font sizing: if verse text is long, use slightly smaller font to fit comfortably
        ta_char_len = len(scripture_ta.strip())
        en_char_len = len(scripture_en.strip())
        is_long = ta_char_len > 120 or en_char_len > 140

        size_ta = 38 if is_long else 42
        size_en = 30 if is_long else 34
        lh_ta = 56 if is_long else 62
        lh_en = 44 if is_long else 50

        font_ta = _get_font("tamil", size_ta)
        font_en = _get_font("serif", size_en)
        font_ref = _get_font("mixed", 32)

        lines_ta = _wrap_text(scripture_ta.strip(), font_ta, content_width, draw)
        if len(lines_ta) > 7:
            lines_ta = lines_ta[:7]
            lines_ta[-1] += "..."

        lines_en = _wrap_text(f'“{scripture_en.strip()}”', font_en, content_width, draw)
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
            bbox = draw.textbbox((0, 0), line, font=font_ta)
            lw = bbox[2] - bbox[0]
            draw.text(((width - lw) // 2, y_cursor), line, fill=white, font=font_ta)
            y_cursor += lh_ta

        # Ornate Gold Flourish Divider
        y_cursor += 10
        draw.line([(width // 2 - 80, y_cursor), (width // 2 - 15, y_cursor)], fill=dark_gold, width=1)
        draw.line([(width // 2 + 15, y_cursor), (width // 2 + 80, y_cursor)], fill=dark_gold, width=1)
        draw.polygon([(width // 2, y_cursor - 4), (width // 2 + 4, y_cursor), (width // 2, y_cursor + 4), (width // 2 - 4, y_cursor)], fill=gold)
        y_cursor += (h_sep - 10)

        # Render English Scripture lines
        for line in lines_en:
            bbox = draw.textbbox((0, 0), line, font=font_en)
            lw = bbox[2] - bbox[0]
            draw.text(((width - lw) // 2, y_cursor), line, fill=cream, font=font_en)
            y_cursor += lh_en

        # Render Citation
        y_cursor += gap_ref
        ref_display = f"— {ref_text.strip()} —"
        r_bbox = draw.textbbox((0, 0), ref_display, font=font_ref)
        rw = r_bbox[2] - r_bbox[0]
        draw.text(((width - rw) // 2, y_cursor), ref_display, fill=gold, font=font_ref)

    else:
        # Single-language layout (Large prominent font)
        primary = scripture_ta.strip() if has_ta else scripture_en.strip()
        is_tamil = has_ta

        font_primary = _get_font("tamil" if is_tamil else "serif", 46)
        font_ref = _get_font("mixed", 34)

        lines = _wrap_text(f'“{primary}”', font_primary, content_width, draw)
        if len(lines) > 8:
            lines = lines[:8]
            lines[-1] += "..."

        lh_prim = 66
        h_prim = len(lines) * lh_prim
        gap_ref = 46
        h_ref = 38
        total_h = h_prim + gap_ref + h_ref

        start_y = 150 + max(20, (avail_h - total_h) // 2)
        y_cursor = start_y

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font_primary)
            lw = bbox[2] - bbox[0]
            draw.text(((width - lw) // 2, y_cursor), line, fill=white, font=font_primary)
            y_cursor += lh_prim

        y_cursor += gap_ref
        ref_display = f"— {ref_text.strip()} —"
        r_bbox = draw.textbbox((0, 0), ref_display, font=font_ref)
        rw = r_bbox[2] - r_bbox[0]
        draw.text(((width - rw) // 2, y_cursor), ref_display, fill=gold, font=font_ref)

    # 5. Footer: Citation & Web Portal Branding
    font_sub = _get_font("mixed", 18)
    footer_text = "Daily Bread • Scripture Status Card • elroi-bible.vercel.app"
    f_bbox = draw.textbbox((0, 0), footer_text, font=font_sub)
    fw = f_bbox[2] - f_bbox[0]
    draw.text(((width - fw) // 2, height - margin - 45), footer_text, fill=(150, 165, 185), font=font_sub)

    # 6. Save to high-quality JPEG
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=95, optimize=True)
    return buffer.getvalue()
