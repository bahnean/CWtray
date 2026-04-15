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
    """Generate a tray icon with 'CWxx' as a single line, as large as possible."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    text = f"CW{cw_number}"

    font_paths = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/verdana.ttf",
    ]

    def load_font(fp, sz):
        return ImageFont.truetype(fp, sz)

    chosen_path = None
    for fp in font_paths:
        if os.path.exists(fp):
            chosen_path = fp
            break

    font = None
    if chosen_path:
        # Binary-search the largest font size that fits within the icon.
        lo, hi = 8, size
        best = 8
        while lo <= hi:
            mid = (lo + hi) // 2
            try:
                f = load_font(chosen_path, mid)
            except Exception:
                break
            bbox = draw.textbbox((0, 0), text, font=f)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            if w <= size and h <= size:
                best = mid
                lo = mid + 1
            else:
                hi = mid - 1
        font = load_font(chosen_path, best)
    else:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (size - w) / 2 - bbox[0]
    y = (size - h) / 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))

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
    if getattr(sys, "frozen", False):
        # Running as a PyInstaller-built .exe
        value = f'"{sys.executable}"'
    else:
        value = f'"{sys.executable}" "{os.path.abspath(__file__)}"'
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
