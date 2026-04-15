"""Generate calendar.ico — a generic calendar icon for the .exe."""
from PIL import Image, ImageDraw, ImageFont
import os


def make_calendar(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pad = max(1, int(size * 0.06))
    r = max(2, int(size * 0.14))  # corner radius
    header_h = int(size * 0.22)

    body_rect = (pad, pad, size - pad, size - pad)
    header_rect = (pad, pad, size - pad, pad + header_h)

    # Body (white)
    draw.rounded_rectangle(body_rect, radius=r, fill=(255, 255, 255, 255))
    # Header (red)
    # Draw a rounded rect and mask the bottom by overdrawing a flat strip.
    draw.rounded_rectangle(header_rect, radius=r, fill=(220, 50, 50, 255))
    draw.rectangle(
        (pad, pad + header_h - r, size - pad, pad + header_h),
        fill=(220, 50, 50, 255),
    )

    # Two rings on the header
    ring_r = max(1, int(size * 0.035))
    ring_y = pad + int(header_h * 0.15)
    ring_y2 = pad - int(size * 0.04)
    for cx in (pad + int(size * 0.28), size - pad - int(size * 0.28)):
        draw.ellipse(
            (cx - ring_r, ring_y2, cx + ring_r, ring_y2 + ring_r * 2 + int(size * 0.06)),
            fill=(200, 200, 200, 255),
            outline=(120, 120, 120, 255),
            width=max(1, int(size * 0.012)),
        )

    # Day number "31"
    text = "31"
    font_path = None
    for fp in ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"):
        if os.path.exists(fp):
            font_path = fp
            break

    # Fit text in the body area below the header
    body_top = pad + header_h
    body_bot = size - pad
    avail_h = body_bot - body_top - int(size * 0.06)
    avail_w = (size - 2 * pad) - int(size * 0.1)

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
    cx = (size - w) / 2 - bbox[0]
    cy = body_top + (avail_h - h) / 2 - bbox[1] + int(size * 0.03)
    draw.text((cx, cy), text, font=font, fill=(40, 40, 40, 255))

    return img


if __name__ == "__main__":
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = [make_calendar(s) for s in sizes]
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calendar.ico")
    images[0].save(out, format="ICO", sizes=[(s, s) for s in sizes], append_images=images[1:])
    print(f"Wrote {out}")
