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

- **Iconița** afișează `CW` și numărul săptămânii (ex: `CW 16`)
- **Hover** pe iconiță → afișează săptămâna, anul și intervalul de date
- **Click dreapta** → meniu cu opțiuni:
  - Info săptămână
  - Activare/dezactivare pornire automată cu Windows
  - Exit

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
