# Testhandleiding — RoosterSomtoday

Deze handleiding beschrijft hoe je lokaal de huidige scan-flow test.

## 1. Database initialiseren

Voer uit vanuit de repository-root:

```bash
python backend/database_init.py
```

Verwacht resultaat:
- melding `Database aangemaakt: data/rooster.db`
- bestand `data/rooster.db` bestaat

## 2. Backend starten

```bash
python backend/main.py
```

Backend draait op:
- `http://localhost:8000`

Snelle check:

```bash
curl http://localhost:8000/api/health
```

Verwacht JSON met minimaal:
- `status: "ok"`
- `timestamp`
- `version`

## 3. Scan-flow testen met curl

### Bekende tag

```bash
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"tag_uid":"04A1B23C9F"}'
```

Verwacht:
- HTTP 200
- JSON met `student_display`, `today`, `ui.timeout_seconds`

### Onbekende tag

```bash
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"tag_uid":"ONBEKEND"}'
```

Verwacht:
- HTTP 404
- detailmelding zoals `Tag onbekend`

## 4. Scan-flow testen via frontend

1. Laat backend draaien
2. Open `frontend/index.html`
3. Vul testtag in (bijv. `04A1B23C9F`)
4. Klik op **Test scan**

Verwacht:
- leerlingnaam en roosterinformatie worden getoond
- bij foute tag verschijnt foutmelding
- na timeout gaat scherm terug naar standby

## 5. Veelvoorkomende problemen

- **`Connection refused`**  
  Backend draait niet of op andere poort.

- **`Tag onbekend` bij bekende testtag**  
  Database mogelijk niet opnieuw geïnitialiseerd. Draai `python backend/database_init.py` opnieuw.

- **`Rooster niet beschikbaar`**  
  Controleer of `data/fake_schedule.json` geldig JSON is en juiste user keys bevat.

- **Frontend toont niets na klik**  
  Open browserconsole en controleer netwerkfouten naar `/api/scan` of `localhost:8000`.

