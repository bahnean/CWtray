# CW Tray 🗓️

Afișează numărul săptămânii curente (Calendar Week) în system tray-ul Windows.

---

## Instalare

### Pas 1 – Instalează Python
Descarcă Python 3.10+ de pe https://python.org și bifează "Add to PATH" la instalare.

### Pas 2 – Instalează dependențele
Deschide Command Prompt în folderul aplicației și rulează:

```
pip install -r requirements.txt
```

### Pas 3 – Pornește aplicația
```
python cw_tray.py
```

Aplicația va apărea în system tray (lângă ceas) și se va adăuga automat la pornirea Windows.

---

## Utilizare

- **Iconița** afișează numărul săptămânii (ex: `16`)
- **Hover** pe iconiță → afișează săptămâna, anul și intervalul de date
- **Click dreapta** → meniu cu opțiuni:
  - Info săptămână (neclicabil)
  - **Standard săptămână** (submeniu, alege cum se calculează CW-ul)
  - Activare/dezactivare pornire automată cu Windows
  - Exit

### Standarde de săptămână

| Standard | Ziua de început | Săptămâna 1 | Uz |
|---|---|---|---|
| **ISO 8601** (default) | Luni | Săptămâna care conține prima zi de joi a anului (echiv. cu cea care are 4+ zile în anul nou) | Europa, ISO, majoritatea industriilor. |
| **US** | Duminică | Săptămâna care conține 1 ianuarie | Statele Unite, Canada. |
| **Simplu** | Luni | Săptămâna care conține 1 ianuarie | Variantă pragmatică — start de luni, fără regula ISO de "prima joi". |

Alegerea se salvează în `%APPDATA%\CWTray\config.json` și persistă între restartări.

---

## Oprire autostart
Din meniul click-dreapta pe iconiță, debifează "Pornire automată cu Windows".

---

## Rulare ca .exe (opțional)
Dacă vrei un executabil fără Python instalat:

```
pip install pyinstaller
pyinstaller --onefile --windowed --name CWTray cw_tray.py
```

Executabilul va fi în folderul `dist/`.
