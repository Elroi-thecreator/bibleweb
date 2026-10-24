"""
Devotional Verse of the Day & Scripture Image Card Generator.
Renders high-resolution 1080x1080 spiritual status cards with dual-language typography,
ornamental golden borders, and citation banners using Pillow.
"""

import io
import logging
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("whatsapp_gateway.card_generator")


def _get_font(font_family: str, size: int) -> ImageFont.ImageFont:
    """Safely loads a system TrueType font with graceful fallback to default."""
    font_paths = {
        "tamil": [
            "C:/Windows/Fonts/Nirmala.ttf",
            "C:/Windows/Fonts/NirmalaB.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansTamil-Regular.ttf",
        ],
        "serif": [
            "C:/Windows/Fonts/georgia.ttf",
            "C:/Windows/Fonts/georgiab.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        ],
        "sans": [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ],
    }

    candidates = font_paths.get(font_family, font_paths["sans"])
    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue

    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.ImageDraw) -> list:
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
    # 1. Create base canvas with smooth vertical gradient (Deep Midnight Navy)
    img = Image.new("RGB", (width, height), color=(12, 18, 32))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        # Subtle dark gradient from top to bottom
        r = int(10 + (y / height) * 12)
        g = int(16 + (y / height) * 16)
        b = int(32 + (y / height) * 28)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 2. Draw Golden Ornamental Borders
    gold = (218, 165, 32)
    dark_gold = (140, 100, 20)
    white = (248, 248, 250)
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
    font_header = _get_font("serif", 24)
    header_text = "✦ HOLY BIBLE • பரிசுத்த வேதாகமம் ✦"
    h_bbox = draw.textbbox((0, 0), header_text, font=font_header)
    h_w = h_bbox[2] - h_bbox[0]
    draw.text(((width - h_w) // 2, margin + 35), header_text, fill=muted_gold, font=font_header)

    # Dividing flourish line
    flourish_y = margin + 80
    draw.line([(width // 2 - 120, flourish_y), (width // 2 + 120, flourish_y)], fill=gold, width=2)

    # 4. Scripture Body Text
    content_width = width - (margin * 2 + 80)
    y_cursor = margin + 140

    has_ta = bool(scripture_ta and scripture_ta.strip())
    has_en = bool(scripture_en and scripture_en.strip())

    if has_ta and has_en:
        # Dual-language layout
        # Tamil font
        font_ta = _get_font("tamil", 38)
        lines_ta = _wrap_text(scripture_ta.strip(), font_ta, content_width, draw)
        if len(lines_ta) > 7:
            lines_ta = lines_ta[:7]
            lines_ta[-1] += "..."

        for line in lines_ta:
            bbox = draw.textbbox((0, 0), line, font=font_ta)
            lw = bbox[2] - bbox[0]
            draw.text(((width - lw) // 2, y_cursor), line, fill=white, font=font_ta)
            y_cursor += 54

        # Small separator
        y_cursor += 20
        draw.line([(width // 2 - 60, y_cursor), (width // 2 + 60, y_cursor)], fill=dark_gold, width=1)
        y_cursor += 30

        # English font
        font_en = _get_font("serif", 32)
        lines_en = _wrap_text(f'"{scripture_en.strip()}"', font_en, content_width, draw)
        if len(lines_en) > 6:
            lines_en = lines_en[:6]
            lines_en[-1] += "..."

        for line in lines_en:
            bbox = draw.textbbox((0, 0), line, font=font_en)
            lw = bbox[2] - bbox[0]
            draw.text(((width - lw) // 2, y_cursor), line, fill=(215, 225, 240), font=font_en)
            y_cursor += 46

    else:
        # Single-language layout (Large prominent font)
        primary = scripture_ta.strip() if has_ta else scripture_en.strip()
        is_tamil = has_ta
        font_primary = _get_font("tamil" if is_tamil else "serif", 46)

        lines = _wrap_text(f'"{primary}"', font_primary, content_width, draw)
        if len(lines) > 9:
            lines = lines[:9]
            lines[-1] += "..."

        # Calculate vertical centering
        total_text_height = len(lines) * 64
        y_cursor = max(margin + 180, (height - 200 - total_text_height) // 2)

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font_primary)
            lw = bbox[2] - bbox[0]
            draw.text(((width - lw) // 2, y_cursor), line, fill=white, font=font_primary)
            y_cursor += 64

    # 5. Footer: Citation & Branding
    font_ref = _get_font("serif", 40)
    ref_display = f"— {ref_text.strip()} —"
    r_bbox = draw.textbbox((0, 0), ref_display, font=font_ref)
    rw = r_bbox[2] - r_bbox[0]
    draw.text(((width - rw) // 2, height - margin - 110), ref_display, fill=gold, font=font_ref)

    font_sub = _get_font("sans", 20)
    footer_text = "Daily Bread • Scripture Status Card • webbible.app"
    f_bbox = draw.textbbox((0, 0), footer_text, font=font_sub)
    fw = f_bbox[2] - f_bbox[0]
    draw.text(((width - fw) // 2, height - margin - 50), footer_text, fill=(160, 175, 195), font=font_sub)

    # 6. Save to high-quality JPEG
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=95, optimize=True)
    return buffer.getvalue()
