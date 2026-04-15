"""Generate calendar.ico — a clean, flat calendar icon for the .exe.

Design priorities: readable at 16-32 px, no fine detail that disappears
when downscaled. Flat rounded square, solid top band, bold day number.
"""
from PIL import Image, ImageDraw, ImageFont
import os


RED = (225, 75, 70, 255)
WHITE = (255, 255, 255, 255)
DARK = (35, 35, 40, 255)


def make_calendar(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Geometry scales with size. Keep numbers "round" so small renders stay crisp.
    radius = max(2, size // 7)
    band_h = max(3, int(size * 0.30))

    body = (0, 0, size - 1, size - 1)
    band = (0, 0, size - 1, band_h)

    # White body with rounded corners.
    draw.rounded_rectangle(body, radius=radius, fill=WHITE, outline=DARK, width=max(1, size // 32))

    # Red top band. Rounded only at the top; flat bottom by overdrawing.
    draw.rounded_rectangle(band, radius=radius, fill=RED)
    draw.rectangle((0, band_h - radius, size - 1, band_h), fill=RED)

    # Day number in the body.
    text = "31"
    font_path = None
    for fp in ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"):
        if os.path.exists(fp):
            font_path = fp
            break

    body_top = band_h
    body_bot = size - 1
    avail_h = int((body_bot - body_top) * 0.85)
    avail_w = int(size * 0.80)

    if font_path:
        lo, hi = 4, size
        best = 4
        while lo <= hi:
            mid = (lo + hi) // 2
            try:
                f = ImageFont.truetype(font_path, mid)
            except Exception:
                break
            bbox = draw.textbbox((0, 0), text, font=f)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            if w <= avail_w and h <= avail_h:
                best = mid
                lo = mid + 1
            else:
                hi = mid - 1
        font = ImageFont.truetype(font_path, best)
    else:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (size - w) / 2 - bbox[0]
    y = body_top + ((body_bot - body_top) - h) / 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=DARK)

    return img


if __name__ == "__main__":
    sizes = [16, 20, 24, 32, 40, 48, 64, 128, 256]
    images = [make_calendar(s) for s in sizes]
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calendar.ico")
    images[0].save(out, format="ICO", sizes=[(s, s) for s in sizes], append_images=images[1:])
    print(f"Wrote {out}")
