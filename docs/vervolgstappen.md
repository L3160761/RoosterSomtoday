# Vervolgstappen — RFID Roosterscherm

Dit document beschrijft de concrete vervolgstappen voor het project, gesorteerd op prioriteit. Begin bij stap 1 en werk naar beneden.

---

## Stap 1 — Database-initialisatie repareren ⚡ HOOGSTE PRIORITEIT

**Waarom:** Zonder dit werkt de backend helemaal niet. Dit is de grootste blokkade.

**Wat moet er gebeuren:**

Herschrijf `backend/database_init.py` zodat het de juiste database aanmaakt:

```python
import sqlite3
import os

os.makedirs("data", exist_ok=True)

conn = sqlite3.connect("data/rooster.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tags (
        tag_uid TEXT PRIMARY KEY,
        user_key TEXT NOT NULL,
        active INTEGER DEFAULT 1
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        user_key TEXT PRIMARY KEY,
        display_name TEXT NOT NULL
    )
''')

# Testdata
cursor.executemany(
    "INSERT OR IGNORE INTO tags (tag_uid, user_key, active) VALUES (?, ?, 1)",
    [
        ("04A1B23C9F", "wessel"),
        ("12B4C56D8E", "anna"),
        ("99Z8Y7X6W5", "thomas"),
    ]
)

cursor.executemany(
    "INSERT OR IGNORE INTO students (user_key, display_name) VALUES (?, ?)",
    [
        ("wessel", "Wessel"),
        ("anna", "Anna"),
        ("thomas", "Thomas"),
    ]
)

conn.commit()
conn.close()
print("Database aangemaakt: data/rooster.db")
```

**Hoe testen:**
```bash
python backend/database_init.py
# Verwacht: "Database aangemaakt: data/rooster.db"
```

---

## Stap 2 — Fake roosterdata aanpassen

**Waarom:** Zelfs met een werkende database zal de scan-flow falen als `fake_schedule.json` de verkeerde structuur heeft.

**Wat moet er gebeuren:**

Vervang `data/fake_schedule.json` door roosterdata in het formaat dat de backend verwacht:

```json
{
  "wessel": {
    "lessons": [
      { "start": "08:30", "end": "10:00", "subject": "Nederlands", "room": "A101", "teacher": "Dhr. Jansen", "status": "normal" },
      { "start": "10:15", "end": "11:45", "subject": "Wiskunde", "room": "B203", "teacher": "Mw. De Vries", "status": "normal" },
      { "start": "12:30", "end": "14:00", "subject": "Engels", "room": "C105", "teacher": "Dhr. Smith", "status": "normal" }
    ]
  },
  "anna": {
    "lessons": [
      { "start": "09:00", "end": "10:30", "subject": "Biologie", "room": "D301", "teacher": "Mw. Bakker", "status": "normal" },
      { "start": "11:00", "end": "12:30", "subject": "Geschiedenis", "room": "A203", "teacher": "Dhr. Hendriks", "status": "normal" }
    ]
  },
  "thomas": {
    "lessons": [
      { "start": "08:30", "end": "10:00", "subject": "Scheikunde", "room": "E102", "teacher": "Dhr. Peters", "status": "normal" },
      { "start": "13:00", "end": "14:30", "subject": "Sport", "room": "Gymzaal", "teacher": "Mw. Van Dam", "status": "normal" }
    ]
  }
}
```

**Hoe testen:**
```bash
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"tag_uid": "04A1B23C9F"}'
# Verwacht: JSON met rooster van Wessel
```

---

## Stap 3 — Frontend koppelen aan de backend

**Waarom:** De frontend toont nu hardcoded tekst. Er is geen werkende koppeling met de backend.

**Wat moet er gebeuren:**

Pas `frontend/index.html` aan zodat het:
1. Een invoerveld of knop heeft voor een tag-UID (voor testen)
2. Een `fetch()` aanroep doet naar `POST /api/scan`
3. De ontvangen JSON verwerkt en weergeeft:
   - Naam van de leerling
   - Huidige les (vak, lokaal, leraar, tijdstip)
   - Volgende les
   - Optioneel: volledig dagoverzicht
4. Een foutmelding toont bij onbekende tag of server-error
5. Na `timeout_seconds` (uit de API-response) terugkeert naar het standby-scherm

**Minimale implementatie voor testen:**

```javascript
async function scanTag(tagUid) {
    try {
        const response = await fetch('http://localhost:8000/api/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tag_uid: tagUid })
        });
        if (!response.ok) {
            showError('Tag onbekend of rooster niet beschikbaar');
            return;
        }
        const data = await response.json();
        showSchedule(data);
        setTimeout(showStandby, data.ui.timeout_seconds * 1000);
    } catch (e) {
        showError('Backend niet bereikbaar');
    }
}
```

---

## Stap 4 — Hardware-integratie bouwen

**Waarom:** Zonder dit moeten scans handmatig worden ingevoerd. Het systeem is pas écht bruikbaar als de RFID-lezer automatisch werkt.

**Wat moet er gebeuren:**

Maak een nieuw bestand `backend/rfid_reader.py` (of vergelijkbaar) dat:
1. De RC522 RFID-lezer uitleest via de `mfrc522` Python-bibliotheek
2. Bij elke succesvolle scan de tag-UID doorstuurt naar de backend via `requests.post()`
3. Continu luistert (loop) en fouten netjes afhandelt

**Benodigde bibliotheek:**
```
pip install mfrc522
```
Voeg toe aan `requirements.txt`.

**Let op:** Dit werkt alleen op een Raspberry Pi met de juiste SPI-configuratie. Testen op een gewone PC is niet mogelijk zonder emulatie.

---

## Stap 5 — Admin-sleutel naar configuratie verplaatsen

**Waarom:** De hardcoded `"admin_key_pilot"` in `backend/main.py` is een beveiligingsrisico als de code ooit openbaar wordt of in productie gaat.

**Wat moet er gebeuren:**

1. Voeg `ADMIN_API_KEY` toe aan `.env.example`
2. Laad de sleutel via `os.environ` in `main.py`:
   ```python
   import os
   ADMIN_KEY = os.environ.get("ADMIN_API_KEY", "admin_key_pilot")
   ```
3. Gebruik `ADMIN_KEY` in de vergelijking in `/api/admin/map`

---

## Stap 6 — Rooster-integratie met Somtoday of Zermelo

**Waarom:** Het systeem heet "RoosterSomtoday" maar gebruikt alleen fake data. Voor echte schoolgebruik is een koppeling met een roosterdienst nodig.

**Wat moet er gebeuren:**

1. Bepaal welke API gebruikt wordt (Somtoday of Zermelo — `.env.example` noemt Zermelo)
2. Onderzoek de beschikbare API-documentatie en authenticatiemethode
3. Schrijf een module die roosterdata ophaalt en omzet naar het interne formaat
4. Voeg caching toe zodat het scherm werkt als de API tijdelijk niet beschikbaar is
5. Bewaar tokens veilig in `.env`, nooit in de broncode

Dit is de grootste functionele uitbreiding en vraagt waarschijnlijk de meeste tijd.

---

## Stap 7 — Tests toevoegen

**Waarom:** De CI-pipeline roept al `pytest` aan maar er zijn geen tests. Dat maakt het moeilijk om te weten of wijzigingen iets breken.

**Wat moet er gebeuren:**

Maak `backend/test_main.py` aan met minimale tests:
- Test of `/api/health` een 200-respons geeft
- Test of `/api/scan` met een onbekende tag een 404 geeft
- Test of `/api/scan` met een bekende tag een geldig rooster geeft (na het oplossen van stap 1 en 2)

---

## Stap 8 — Testen op echte hardware

**Wanneer:** Nadat stap 1 t/m 4 zijn afgerond.

**Checklist voor praktijktesten:**
- [ ] Backend start op zonder fouten vanuit de juiste map
- [ ] Database wordt correct aangemaakt
- [ ] Scan met een testtag geeft het juiste rooster terug
- [ ] Frontend toont het rooster op het scherm
- [ ] Timeout werkt: standby-scherm na 45 seconden
- [ ] Onbekende tag geeft een duidelijke foutmelding
- [ ] Scherm is goed leesbaar op afstand (lettergrootte, contrast)
- [ ] Systeem start automatisch op bij aanzetten van de Pi (autostart instellen)

---

## Prioriteitstabel

| # | Stap | Prioriteit | Geschatte moeite |
|---|---|---|---|
| 1 | Database repareren | 🔴 Kritiek | Klein (< 1 uur) |
| 2 | Fake data aanpassen | 🔴 Kritiek | Klein (< 1 uur) |
| 3 | Frontend koppelen | 🟠 Hoog | Middel (2–4 uur) |
| 4 | Hardware-integratie | 🟠 Hoog | Middel (2–4 uur) |
| 5 | Admin-sleutel naar .env | 🟡 Normaal | Klein (< 30 min) |
| 6 | Somtoday/Zermelo-koppeling | 🟢 Uitbreiding | Groot (meerdere dagen) |
| 7 | Tests toevoegen | 🟡 Normaal | Middel (1–2 uur) |
| 8 | Testen op hardware | 🟠 Hoog | Afhankelijk van bovenstaande |
