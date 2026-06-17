# Architectuur — RFID Roosterscherm

## Overzicht

Het systeem bestaat uit vier lagen die samenwerken:

```
[Hardware]          [Backend]           [Data]              [Frontend]
Raspberry Pi   →    FastAPI API     →   SQLite DB       →   Kiosk Browser
RC522 RFID         /api/scan            data/rooster.db     frontend/index.html
HDMI scherm        /api/health          fake_schedule.json
                   /api/admin/map       tag_mapping.json
```

## Componenten in detail

### 1. Hardware (Raspberry Pi + RC522)

- **Raspberry Pi** draait de backend-server en stuurt de kiosk-browser aan
- **RC522 RFID-lezer** leest de tag-UID van een leerlingtag (kluis-tag)
- **HDMI-scherm** toont de kiosk-webpagina via `chromium-browser --kiosk`

De Pi leest de tag-UID via de RC522 en stuurt die via een HTTP POST naar de lokale backend.

> **Let op:** De hardware-integratiecode (Python-script dat de RC522 uitleest en de backend aanroept) is in de huidige repository nog niet aanwezig. Dat is een ontbrekend onderdeel.

---

### 2. Backend (FastAPI — `backend/main.py`)

De backend is een Python-webserver die draait op `http://localhost:8000`.

#### Endpoints

| Methode | URL | Beschrijving |
|---|---|---|
| `GET` | `/api/health` | Controleert of de server bereikbaar is |
| `POST` | `/api/scan` | Ontvangt tag-UID, geeft rooster terug |
| `POST` | `/api/admin/map` | Voegt een tag–leerling-koppeling toe (vereist API-sleutel) |

#### Scan-flow stap voor stap

```
1. Frontend / hardware stuurt:
   POST /api/scan
   {"tag_uid": "04A1B23C9F"}

2. Backend zoekt tag_uid op in de database:
   SELECT user_key FROM tags WHERE tag_uid = ? AND active = 1

3. Als tag gevonden: haal user_key op (bijv. "wessel")

4. Laad fake_schedule.json en zoek lessons op voor die user_key:
   schedule_data["wessel"]["lessons"]

5. Bepaal huidige les en volgende les op basis van huidig tijdstip

6. Haal weergavenaam op uit de database:
   SELECT display_name FROM students WHERE user_key = ?

7. Stuur screen-ready JSON terug:
   {
     "student_display": "Wessel",
     "date": "2026-06-02",
     "now": { "start": "09:00", "end": "10:30", "subject": "Wiskunde", ... },
     "next": { ... },
     "today": [ ... alle lessen ... ],
     "ui": { "timeout_seconds": 45 }
   }
```

#### Configuratie

De backend leest de volgende paden:

```python
DATABASE_PATH = "data/rooster.db"
FAKE_SCHEDULE_PATH = "data/fake_schedule.json"
```

De server moet worden gestart vanuit de **root van de repository**, niet vanuit de `backend/`-map, omdat de paden relatief zijn aan de werkdirectory.

---

### 3. Database (SQLite — `data/rooster.db`)

De backend verwacht een SQLite-database op `data/rooster.db` met twee tabellen:

#### Tabel `tags`

| Kolom | Type | Beschrijving |
|---|---|---|
| `tag_uid` | TEXT | De unieke ID van de RFID-tag |
| `user_key` | TEXT | Sleutelwoord dat verwijst naar de leerling |
| `active` | INTEGER | 1 = actief, 0 = uitgeschakeld |

#### Tabel `students`

| Kolom | Type | Beschrijving |
|---|---|---|
| `user_key` | TEXT | Sleutelwoord (bijv. `"wessel"`) |
| `display_name` | TEXT | Naam voor weergave op het scherm (bijv. `"Wessel"`) |

> **Bekende inconsistentie:** `backend/database_init.py` maakt momenteel **niet** deze database en tabellen aan. Zie [`status.md`](status.md) voor details.

---

### 4. Data (`data/`)

#### `data/fake_schedule.json`

Bevat het nep-rooster voor testdoeleinden. De backend verwacht deze structuur:

```json
{
  "wessel": {
    "lessons": [
      {
        "start": "08:30",
        "end": "10:00",
        "subject": "Nederlands",
        "room": "A101",
        "teacher": "Dhr. Jansen",
        "status": "normal"
      }
    ]
  }
}
```

Mogelijke waarden voor `status`: `normal`, `moved`, `cancelled`

> **Bekende inconsistentie:** het huidige `data/fake_schedule.json` heeft een andere structuur dan de backend verwacht. Zie [`status.md`](status.md).

#### `data/tag_mapping.json`

Bevat een eenvoudige mapping van NFC/RFID tag-UID naar leerling-key:

```json
{
  "04A1B23C9F": "zine",
  "12B4C56D8E": "tom",
  "99Z8Y7X6W5": "rekawt"
}
```

Dit bestand wordt gebruikt door `backend/database_init.py` om de `tags`-tabel te vullen. Vervang de voorbeeld-UIDs door de echte UID-nummers die de NFC-lezer teruggeeft.

---

### 5. Frontend (`frontend/index.html`)

De frontend is een enkele HTML-pagina die draait in een kiosk-browser (Chromium in fullscreen).

**Huidig gedrag:**
- Toont een standby-scherm bij laden
- Heeft een hardcoded timeout van 30 seconden
- Toont een gesimuleerde melding ("Next Event: Meeting at 10:00 AM")
- Roept de backend **nog niet** aan via `/api/scan`

De frontend is dus nog een basissjabloon en moet nog volledig worden gekoppeld aan de backend-API.

---

### 6. CI/CD (`.github/workflows/main.yml`)

Bij elke push en pull request wordt automatisch uitgevoerd:
1. `flake8 backend/` — code-stijlcontrole (fouten worden genegeerd met `--exit-zero`)
2. `pytest backend/` — unit tests (er zijn nog geen tests, commando mislukt stilletjes)
3. `python database_init.py` + `python main.py` (korte opstart-test)

---

## Hoe de onderdelen samenwerken (ideale situatie)

```
Leerling scan
     │
     ▼
RC522 RFID-lezer (hardware)
     │  tag_uid: "04A1B23C9F"
     ▼
Python hardware-script (ontbreekt nog)
     │  POST /api/scan
     ▼
FastAPI backend (main.py)
     │  zoek tag in data/rooster.db
     │  laad data/fake_schedule.json
     │  bepaal huidige/volgende les
     ▼
Screen-ready JSON response
     │
     ▼
Frontend (index.html in kiosk-browser)
     │  toon naam, huidige les, volgende les, dagrooster
     ▼
Scherm zichtbaar voor leerling
     │  na 45 seconden
     ▼
Standby-scherm
```
