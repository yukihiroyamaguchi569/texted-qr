import io
import os
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "NotoSans-Bold.ttf")


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size)


def _binary_search_font_size(text: str, target_px: int) -> int:
    lo, hi = 8, 400
    best = lo
    while lo <= hi:
        mid = (lo + hi) // 2
        font = _get_font(mid)
        bbox = font.getbbox(text)
        w = bbox[2] - bbox[0]
        if w <= target_px:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def _make_stroke_mask(
    width: int, height: int, text: str, position: str, module_size: int
) -> Image.Image:
    """
    Returns stroke_mask: white where font strokes are (slightly dilated).
    Dilation is kept small so the stroke shape stays natural.
    """
    target_px = int(width * 0.60)
    font_size = _binary_search_font_size(text, target_px)
    font = _get_font(font_size)

    bbox = font.getbbox(text)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x_offset = bbox[0]
    y_offset = bbox[1]

    x = (width - text_w) // 2 - x_offset

    if position == "top":
        y = int(height * 0.15) - y_offset
    elif position == "bottom":
        y = int(height * 0.70) - y_offset
    else:
        y = (height - text_h) // 2 - y_offset

    stroke_mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(stroke_mask).text((x, y), text, fill=255, font=font)
    dil = max(3, module_size // 4)
    stroke_mask = stroke_mask.filter(ImageFilter.MaxFilter(size=dil))

    return stroke_mask


def generate_qr_image(
    url: str,
    text: str,
    accent_color: tuple[int, int, int] = (220, 50, 50),
    position: str = "center",
) -> bytes:
    """
    Generate a QR code PNG where the given text floats inside the dot pattern.

    4-color scheme:
    - ON  + in stroke  → txt_dark  = accent_color   (scannable)
    - OFF + in stroke  → txt_light = 65% white + 35% accent  (scannable as OFF)
    - ON  + not stroke → bg_dark   = black
    - OFF + not stroke → bg_light  = white (skip, already background)
    """
    # --- QR matrix ---
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=1, border=4)
    qr.add_data(url)
    qr.make(fit=True)

    matrix = qr.get_matrix()
    total_modules = len(matrix)
    module_size = max(10, 800 // total_modules)
    img_size = total_modules * module_size
    radius = max(1, module_size // 4)

    stroke_mask = _make_stroke_mask(img_size, img_size, text, position, module_size)

    # txt_light: 65% white + 35% accent — bright enough for scanners to read as OFF
    light_accent = tuple(int(255 * 0.65 + c * 0.35) for c in accent_color)

    img = Image.new("RGB", (img_size, img_size), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    for row_idx, row in enumerate(matrix):
        for col_idx, module_on in enumerate(row):
            x0 = col_idx * module_size
            y0 = row_idx * module_size
            x1 = x0 + module_size - 1
            y1 = y0 + module_size - 1
            cx = x0 + module_size // 2
            cy = y0 + module_size // 2

            in_stroke = stroke_mask.getpixel((cx, cy)) > 128

            if module_on:
                color = accent_color if in_stroke else (0, 0, 0)
                draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=color)
            elif in_stroke:
                # txt_light: tinted just enough to show the font silhouette
                draw.rectangle([x0, y0, x1, y1], fill=light_accent)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()
