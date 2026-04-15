"""Generate cwtray.ico with multiple sizes for Windows."""
from PIL import Image, ImageDraw, ImageFont
import datetime
import os


def make_image(size, cw_number):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    font_top_size = int(size * 0.34)
    font_bot_size = int(size * 0.44)

    font_paths = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    font_top = font_bot = None
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font_top = ImageFont.truetype(fp, font_top_size)
                font_bot = ImageFont.truetype(fp, font_bot_size)
                break
            except Exception:
                pass
    if font_top is None:
        font_top = ImageFont.load_default()
        font_bot = font_top

    text_top = "CW"
    text_bot = str(cw_number)

    bbox_top = draw.textbbox((0, 0), text_top, font=font_top)
    w_top = bbox_top[2] - bbox_top[0]
    draw.text(((size - w_top) / 2, size * 0.06), text_top, font=font_top, fill=(255, 255, 255, 255))

    bbox_bot = draw.textbbox((0, 0), text_bot, font=font_bot)
    w_bot = bbox_bot[2] - bbox_bot[0]
    draw.text(((size - w_bot) / 2, size * 0.46), text_bot, font=font_bot, fill=(255, 255, 0, 255))

    return img


if __name__ == "__main__":
    cw = datetime.date.today().isocalendar()[1]
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = [make_image(s, cw) for s in sizes]
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cwtray.ico")
    images[0].save(out, format="ICO", sizes=[(s, s) for s in sizes], append_images=images[1:])
    print(f"Wrote {out}")
