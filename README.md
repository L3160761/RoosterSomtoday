# 🎓 RoosterSomtoday (RFID Roosterscherm)

RoosterSomtoday is een schoolproject waarmee leerlingen via een RFID-tag hun dagrooster op een gedeeld scherm kunnen bekijken (telefoonvrij alternatief).

## Wat doet dit project?

1. Leerling scant RFID-tag
2. Backend koppelt tag aan leerling
3. Backend levert roosterdata terug
4. Frontend toont huidige/volgende les en dagoverzicht

## Globale architectuur

- **Frontend**: `frontend/index.html` (kiosk-weergave + testscan)
- **Backend**: `backend/main.py` (FastAPI met `/api/health`, `/api/scan`, `/api/admin/map`)
- **Data nu**: SQLite + fake roosterdata (`data/fake_schedule.json`)
- **Richting vervolg**: integratie met echte roosterbron (Somtoday/Zermelo) volgens roadmap

## Snel starten

### 1) Dependencies installeren
```bash
pip install -r requirements.txt
```

### 2) Database initialiseren
```bash
python backend/database_init.py
```

### 3) Backend starten
```bash
python backend/main.py
```
Backend draait dan op `http://localhost:8000`.

### 4) Frontend openen
Open `frontend/index.html` in je browser en voer een test tag-UID in.

Testtags (vervang deze voorbeeld-UIDs in `data/tag_mapping.json` door de echte NFC UID-nummers):
- `04A1B23C9F` → zine
- `12B4C56D8E` → tom
- `99Z8Y7X6W5` → rekawt

## Belangrijke documentatie (`docs/`)

### Lees dit als nieuw teamlid als eerste
1. [`docs/overdracht.md`](docs/overdracht.md) — huidige status, wat werkt, wat nog niet, aanbevolen werkvolgorde
2. [`docs/vervolgstappen.md`](docs/vervolgstappen.md) — roadmap met gerealiseerde milestones en openstaande stappen
3. [`docs/testen.md`](docs/testen.md) — lokale testhandleiding (backend, curl, frontend-flow)
4. [`docs/hardware-rc522.md`](docs/hardware-rc522.md) — RC522 aansluiten op Raspberry Pi 4B

### Aanvullende achtergrond
- [`docs/overzicht.md`](docs/overzicht.md)
- [`docs/architectuur.md`](docs/architectuur.md)
- [`docs/status.md`](docs/status.md)

## Licentie
Schoolproject — vrij te gebruiken binnen onderwijscontext.
