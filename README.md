# CW Tray 🗓️

Afișează numărul săptămânii curente (Calendar Week) în system tray-ul Windows.

---

## Instalare

1. Descarcă `CWTray.exe` din [Releases](https://github.com/bahnean/CWtray/releases/latest).
2. Mută-l într-un folder permanent (ex: `C:\Users\<tu>\Apps\CWTray\`).
3. Dublu-click pe `CWTray.exe`.

Aplicația apare în system tray (lângă ceas) și se adaugă automat la pornirea Windows.

> Notă: nu trebuie să ai Python instalat.

---

## Utilizare

- **Iconița** afișează numărul săptămânii curente (ex: `16`). Culoarea textului se adaptează automat la tema taskbar-ului (negru pe light, alb pe dark).
- **Hover** pe iconiță → săptămâna, anul și intervalul de date al săptămânii curente.
- **Click dreapta** → meniu cu:
  - Info săptămână (neclicabil, doar afișaj)
  - **Standard săptămână** — submeniu pentru a alege cum se numerotează săptămânile
  - Activare/dezactivare pornire automată cu Windows
  - Exit

### Standarde de săptămână

| Standard | Ziua de început | Săptămâna 1 | Uz |
|---|---|---|---|
| **ISO 8601** (default) | Luni | Săptămâna care conține prima zi de joi (echiv. cu cea cu 4+ zile în anul nou) | Europa, ISO, majoritatea industriilor. |
| **US** | Duminică | Săptămâna care conține 1 ianuarie | Statele Unite, Canada. |
| **Simplu** | Luni | Săptămâna care conține 1 ianuarie | Variantă pragmatică — start de luni, fără regula ISO de "prima joi". |

Alegerea se salvează în `%APPDATA%\CWTray\config.json` și persistă între restartări.

---

## Oprire autostart

Click dreapta pe iconiță → debifează **Pornire automată cu Windows**.

## Dezinstalare

1. Click dreapta pe iconiță → debifează **Pornire automată cu Windows**.
2. Click dreapta → **Exit**.
3. Șterge `CWTray.exe` și folderul `%APPDATA%\CWTray\`.
