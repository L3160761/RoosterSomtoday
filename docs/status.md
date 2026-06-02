# Projectstatus — RFID Roosterscherm

Laatste update: juni 2026

## Overzicht

| Categorie | Status |
|---|---|
| Projectopzet en mappenstructuur | ✅ Af |
| Backend API (endpoints) | ✅ Grotendeels af |
| Scan-logica in backend | ✅ Aanwezig |
| Database-initialisatie | ❌ Inconsistent / kapot |
| Fake roosterdata (juist formaat) | ❌ Verkeerd formaat |
| Frontend koppeling aan backend | ❌ Nog niet gekoppeld |
| Hardware-integratiecode | ❌ Ontbreekt |
| Somtoday/Zermelo-koppeling | ❌ Niet aanwezig |
| Beveiliging admin endpoint | ⚠️ Prototype (hardcoded key) |
| Tests | ⚠️ Nauwelijks aanwezig |
| Documentatie | ✅ Toegevoegd (deze map) |

---

## Wat is af

### ✅ Projectopzet
De repository heeft een duidelijke en logische mappenstructuur:
- `backend/` — Python/FastAPI-code
- `frontend/` — HTML/JS kiosk-interface
- `data/` — testdata
- `.env.example` — template voor configuratie
- `.gitignore` — sluit gevoelige bestanden uit
- `.github/workflows/` — CI/CD-pipeline

### ✅ Backend API-structuur
`backend/main.py` bevat drie werkende endpoints:
- `GET /api/health` — geeft serverbeschikbaarheid terug
- `POST /api/scan` — kernfunctionaliteit: tag → rooster
- `POST /api/admin/map` — koppeling toevoegen via API

### ✅ Scan-logica
De logica in `/api/scan` is volledig uitgewerkt:
- Tag-UID ontvangen en valideren
- Opzoeken in de database (`tags`-tabel)
- Roosterdata laden uit JSON
- Huidige en volgende les bepalen op basis van tijd
- Weergavenaam ophalen uit de database (`students`-tabel)
- Screen-ready JSON samenstellen en terugsturen

### ✅ Privacybewuste aanpak
- Geen echte leerlingdata in de repository
- `.env` in `.gitignore`
- Logging zonder persoonsgegevens
- Fake testdata in plaats van echte namen/roosters

### ✅ CI/CD-pipeline
Er is een GitHub Actions-workflow die bij elke push automatisch:
- code-stijlcontrole uitvoert (`flake8`)
- pytest aanroept
- de backend kort opstart

---

## Wat gedeeltelijk af is

### ⚠️ Frontend (`frontend/index.html`)
Er is een basissjabloon voor de kiosk-interface:
- donker thema, centred layout
- standby-scherm aanwezig
- timeout na 30 seconden

**Wat ontbreekt:**
- De frontend roept de backend **nog niet** aan (`/api/scan` wordt nergens aangeroepen)
- Er is geen invoer voor een tag-UID (handmatig of via hardware)
- De roosterdata wordt niet echt weergegeven (hardcoded nep-tekst)
- Er is geen weergave van huidige les, volgende les of dagoverzicht
- Foutafhandeling (onbekende tag, backend offline) is niet uitgewerkt

### ⚠️ Admin-beveiliging
Het `/api/admin/map` endpoint vereist een API-sleutel, maar die is hardcoded in de broncode:

```python
if not api_key or api_key != "admin_key_pilot":
```

Dit is acceptabel voor een pilot, maar moet worden vervangen door een configureerbare sleutel via `.env` voordat het systeem in een echte schoolomgeving draait.

### ⚠️ Tests
De CI-pipeline roept `pytest` aan, maar er zijn geen testbestanden aanwezig in `backend/`. De tests slagen niet en de foutmelding wordt genegeerd (`2>/dev/null || echo "Tests setup"`).

---

## Wat ontbreekt

### ❌ Werkende database-initialisatie

Dit is de **grootste bekende bug** in het project.

**Wat de backend verwacht:**
- Databasebestand: `data/rooster.db`
- Tabel `tags` met kolommen: `tag_uid`, `user_key`, `active`
- Tabel `students` met kolommen: `user_key`, `display_name`

**Wat `backend/database_init.py` nu doet:**
- Maakt een bestand `example.db` aan (verkeerde naam, verkeerde locatie)
- Maakt een tabel `users` aan met kolommen `id`, `username`, `email`

Dit script is een generieke SQLite-template en heeft **niets** te maken met de werkelijke structuur die de backend nodig heeft. Als je nu `python database_init.py` uitvoert en daarna `python main.py` opstart, crasht de backend bij de eerste scan omdat de verwachte tabellen niet bestaan.

**Wat moet worden gedaan:**
`database_init.py` moet worden herschreven zodat het:
1. `data/rooster.db` aanmaakt
2. De tabel `tags` aanmaakt
3. De tabel `students` aanmaakt
4. Testdata invoegt (de drie testtags uit de README)

### ❌ Fake roosterdata in het juiste formaat

`data/fake_schedule.json` heeft een andere structuur dan de backend verwacht.

**Wat de backend verwacht:**
```json
{
  "wessel": {
    "lessons": [
      { "start": "08:30", "end": "10:00", "subject": "Nederlands", "room": "A101", "teacher": "Dhr. Jansen", "status": "normal" }
    ]
  }
}
```

**Wat het bestand nu bevat:**
```json
{
  "schedules": [
    {
      "user_id": "user1",
      "schedule": [
        { "date": "2026-03-31", "time": "08:00:00", "activity": "Meeting with team" }
      ]
    }
  ]
}
```

De sleutels, structuur en veldnamen kloppen niet. De scan-flow zal dus altijd falen met "Rooster niet beschikbaar", zelfs als de database wél correct is.

### ❌ Hardware-integratiecode

Er is geen Python-script aanwezig dat:
- de RC522 RFID-lezer uitleest via SPI
- de gelezen tag-UID doorstuurt naar `POST /api/scan`
- de koppeling maakt tussen fysieke hardware en de backend

Zonder dit script werkt het systeem alleen met handmatige API-aanroepen (bijv. via `curl`).

### ❌ Somtoday/Zermelo-koppeling

De repository heet `RoosterSomtoday` en `.env.example` bevat variabelen `ZERMELO_TOKEN` en `ZERMELO_SCHOOL`, maar er is **geen code** die een roosterplatform aanroept. Het systeem werkt uitsluitend met lokale fake data.

---

## Bekende inconsistenties

| # | Inconsistentie | Locatie | Impact |
|---|---|---|---|
| 1 | `database_init.py` maakt `example.db` + `users`-tabel, maar backend verwacht `data/rooster.db` + `tags` + `students` | `backend/database_init.py` vs `backend/main.py` | ❌ Backend crasht bij eerste scan |
| 2 | `fake_schedule.json` heeft verkeerde structuur (schedules-lijst vs user_key-dict) | `data/fake_schedule.json` vs `backend/main.py` | ❌ Scan geeft altijd "Rooster niet beschikbaar" |
| 3 | `tag_mapping.json` wordt niet gebruikt door de backend (backend gebruikt database) | `data/tag_mapping.json` | ⚠️ Verwarrend, maar geen directe fout |
| 4 | `main.py` start met relatieve paden (`data/rooster.db`) maar CI start het vanuit `backend/`-map | `.github/workflows/main.yml` | ⚠️ Database gevonden mits gestart vanuit root |
| 5 | Admin key hardcoded in broncode | `backend/main.py` regel 139 | ⚠️ Niet veilig voor productie |
| 6 | Frontend roept backend niet aan | `frontend/index.html` | ❌ Systeem werkt niet end-to-end |
