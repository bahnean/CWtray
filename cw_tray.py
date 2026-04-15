import pystray
from PIL import Image, ImageDraw, ImageFont
import datetime
import threading
import time
import sys
import os
import winreg

APP_NAME = "CW Tray"
AUTOSTART_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def get_cw():
    """Return current ISO calendar week number."""
    return datetime.date.today().isocalendar()[1]


def make_icon(cw_number):
    """Generate a 64x64 tray icon with 'CW XX' text on black background."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    text_top = f"CW"
    text_bot = str(cw_number)

    # Try to use a system font, fall back to default
    font_top = None
    font_bot = None
    font_paths = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/verdana.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font_top = ImageFont.truetype(fp, 22)
                font_bot = ImageFont.truetype(fp, 28)
                break
            except Exception:
                pass

    if font_top is None:
        font_top = ImageFont.load_default()
        font_bot = font_top

    # Draw "CW" on top half
    bbox_top = draw.textbbox((0, 0), text_top, font=font_top)
    w_top = bbox_top[2] - bbox_top[0]
    draw.text(((size - w_top) / 2, 4), text_top, font=font_top, fill=(255, 255, 255, 255))

    # Draw number on bottom half
    bbox_bot = draw.textbbox((0, 0), text_bot, font=font_bot)
    w_bot = bbox_bot[2] - bbox_bot[0]
    draw.text(((size - w_bot) / 2, 30), text_bot, font=font_bot, fill=(255, 255, 0, 255))

    return img


def get_tooltip():
    today = datetime.date.today()
    cw = today.isocalendar()[1]
    year = today.isocalendar()[0]
    # Monday of current week
    monday = today - datetime.timedelta(days=today.weekday())
    sunday = monday + datetime.timedelta(days=6)
    return (
        f"CW {cw} – {year}\n"
        f"{monday.strftime('%d.%m.%Y')} → {sunday.strftime('%d.%m.%Y')}"
    )


def is_autostart_enabled():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_KEY, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False


def enable_autostart():
    exe = sys.executable
    script = os.path.abspath(__file__)
    value = f'"{exe}" "{script}"'
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_KEY, 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, value)
    winreg.CloseKey(key)


def disable_autostart():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_KEY, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass


class CWTrayApp:
    def __init__(self):
        self.cw = get_cw()
        self.icon = None
        self._stop_event = threading.Event()

    def build_menu(self):
        autostart_label = (
            "✓ Pornire automată cu Windows"
            if is_autostart_enabled()
            else "  Pornire automată cu Windows"
        )
        return pystray.Menu(
            pystray.MenuItem(get_tooltip(), None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(autostart_label, self.toggle_autostart),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.quit),
        )

    def toggle_autostart(self):
        if is_autostart_enabled():
            disable_autostart()
        else:
            enable_autostart()
        # Rebuild menu to reflect new state
        self.icon.menu = self.build_menu()

    def quit(self):
        self._stop_event.set()
        self.icon.stop()

    def update_loop(self):
        """Check every minute if week changed and update icon."""
        while not self._stop_event.is_set():
            new_cw = get_cw()
            if new_cw != self.cw:
                self.cw = new_cw
                self.icon.icon = make_icon(self.cw)
                self.icon.menu = self.build_menu()
            time.sleep(60)

    def run(self):
        # Enable autostart on first run
        if not is_autostart_enabled():
            enable_autostart()

        img = make_icon(self.cw)
        self.icon = pystray.Icon(
            APP_NAME,
            img,
            title=get_tooltip(),
            menu=self.build_menu(),
        )

        # Start background update thread
        t = threading.Thread(target=self.update_loop, daemon=True)
        t.start()

        self.icon.run()


if __name__ == "__main__":
    app = CWTrayApp()
    app.run()
