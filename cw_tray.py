import pystray
from PIL import Image, ImageDraw, ImageFont
import datetime
import threading
import time
import sys
import os
import json
import winreg

APP_NAME = "CW Tray"
AUTOSTART_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

# Supported week-numbering standards.
# Each entry: (key, label, week_start_weekday[Mon=0..Sun=6])
STANDARDS = [
    ("iso",     "ISO 8601 (Europa, luni)",       0),
    ("us",      "US (duminică, 1 ian = sapt. 1)", 6),
    ("simple",  "Simplu (luni, 1 ian = sapt. 1)", 0),
]
DEFAULT_STANDARD = "iso"

CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "CWTray")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_config(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f)


def compute_cw(today, standard):
    """Return (week_number, year, week_start_date, week_end_date) for given standard."""
    if standard == "iso":
        iso = today.isocalendar()
        week = iso[1]
        year = iso[0]
        start = today - datetime.timedelta(days=today.weekday())  # Monday
        end = start + datetime.timedelta(days=6)
        return week, year, start, end
    if standard == "us":
        # Week starts Sunday; week 1 is the week containing Jan 1.
        week = int(today.strftime("%U"))
        if week == 0:
            week = 1
        # Sunday of current week: weekday() gives Mon=0..Sun=6, so offset to Sunday
        offset = (today.weekday() + 1) % 7  # Sun=0..Sat=6
        start = today - datetime.timedelta(days=offset)
        end = start + datetime.timedelta(days=6)
        return week, today.year, start, end
    if standard == "simple":
        # Week starts Monday; week 1 contains Jan 1.
        week = int(today.strftime("%W"))
        if week == 0:
            week = 1
        start = today - datetime.timedelta(days=today.weekday())
        end = start + datetime.timedelta(days=6)
        return week, today.year, start, end
    return compute_cw(today, "iso")


def make_icon(cw_number):
    """Generate a tray icon with the week number, as large as possible."""
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    text = str(cw_number)

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

    if chosen_path:
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
    draw.text((x, y), text, font=font, fill=(0, 0, 0, 255))

    return img


def get_tooltip(standard):
    today = datetime.date.today()
    week, year, start, end = compute_cw(today, standard)
    return (
        f"CW {week} – {year}\n"
        f"{start.strftime('%d.%m.%Y')} → {end.strftime('%d.%m.%Y')}"
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
        cfg = load_config()
        self.standard = cfg.get("standard", DEFAULT_STANDARD)
        if self.standard not in {k for k, _, _ in STANDARDS}:
            self.standard = DEFAULT_STANDARD
        self.cw = self._current_week()
        self.icon = None
        self._stop_event = threading.Event()

    def _current_week(self):
        return compute_cw(datetime.date.today(), self.standard)[0]

    def _make_standard_handler(self, key):
        def handler(_icon=None, _item=None):
            if self.standard == key:
                return
            self.standard = key
            save_config({"standard": key})
            self.cw = self._current_week()
            self.icon.icon = make_icon(self.cw)
            self.icon.title = get_tooltip(self.standard)
            self.icon.menu = self.build_menu()
        return handler

    def _is_standard_checked_factory(self, key):
        return lambda _item: self.standard == key

    def build_menu(self):
        autostart_label = (
            "✓ Pornire automată cu Windows"
            if is_autostart_enabled()
            else "  Pornire automată cu Windows"
        )
        standard_items = [
            pystray.MenuItem(
                label,
                self._make_standard_handler(key),
                checked=self._is_standard_checked_factory(key),
                radio=True,
            )
            for key, label, _ in STANDARDS
        ]
        return pystray.Menu(
            pystray.MenuItem(get_tooltip(self.standard), None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Standard săptămână", pystray.Menu(*standard_items)),
            pystray.MenuItem(autostart_label, self.toggle_autostart),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.quit),
        )

    def toggle_autostart(self):
        if is_autostart_enabled():
            disable_autostart()
        else:
            enable_autostart()
        self.icon.menu = self.build_menu()

    def quit(self):
        self._stop_event.set()
        self.icon.stop()

    def update_loop(self):
        """Check every minute if week changed and update icon."""
        while not self._stop_event.is_set():
            new_cw = self._current_week()
            if new_cw != self.cw:
                self.cw = new_cw
                self.icon.icon = make_icon(self.cw)
                self.icon.title = get_tooltip(self.standard)
                self.icon.menu = self.build_menu()
            time.sleep(60)

    def run(self):
        if not is_autostart_enabled():
            enable_autostart()

        img = make_icon(self.cw)
        self.icon = pystray.Icon(
            APP_NAME,
            img,
            title=get_tooltip(self.standard),
            menu=self.build_menu(),
        )

        t = threading.Thread(target=self.update_loop, daemon=True)
        t.start()

        self.icon.run()


if __name__ == "__main__":
    app = CWTrayApp()
    app.run()
