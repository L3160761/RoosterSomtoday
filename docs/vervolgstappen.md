# Vervolgstappen — RFID Roosterscherm

Dit document is de actuele combinatie van **status + roadmap** voor het leerlingteam.

---

## Samenvatting status

- ✅ **Stap 1 t/m 3 zijn gerealiseerd als milestones in de huidige repository**.
- ⏳ **Stap 4 t/m 8 staan open** en vormen de vervolgfase naar een werkende hardware-opstelling op school.

---

## Stap 1 — Database-initialisatie repareren ✅ Gerealiseerd

**Doel**  
De backend laten werken met de juiste SQLite-structuur (`data/rooster.db`, tabellen `tags` en `students`).

**Opgeleverd**
- `backend/database_init.py` maakt nu `data/rooster.db` aan
- Tabellen `tags` en `students` worden aangemaakt
- Testdata met drie testtags is aanwezig

**Hoe testen**
```bash
python backend/database_init.py
# Verwacht: "Database aangemaakt: data/rooster.db"
```

---

## Stap 2 — Fake roosterdata aanpassen ✅ Gerealiseerd

**Doel**  
De roosterdata laten aansluiten op het formaat dat de backend verwacht.

**Opgeleverd**
- `data/fake_schedule.json` gebruikt nu per `user_key` een `lessons`-lijst
- Velden `start`, `end`, `subject`, `room`, `teacher`, `status` zijn beschikbaar

**Hoe testen**
```bash
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"tag_uid":"04A1B23C9F"}'
# Verwacht: JSON met student_display, today, ui.timeout_seconds
```

---

## Stap 3 — Frontend koppelen aan de backend ✅ Gerealiseerd

**Doel**  
Een testbare frontend-flow maken die echt de backend (`/api/scan`) aanroept.

**Opgeleverd**
- `frontend/index.html` bevat testinvoer voor tag-UID
- Frontend doet `fetch` naar scan-endpoint
- Foutmeldingen en timeout-terugval naar standby zijn aanwezig

**Hoe testen**
1. Start backend (`python backend/main.py`)
2. Open `frontend/index.html`
3. Gebruik testtag `04A1B23C9F`
4. Verwacht: roosterinformatie zichtbaar, daarna terug naar standby op timeout

---

## Stap 4 — Hardware-integratie bouwen ⏳ Open

**Doel**  
RC522-scans automatisch laten doorgeven aan de backend, zonder handmatige invoer.

**Vervolg**
1. Maak `backend/rfid_reader.py` met RC522-uitleesloop
2. Verstuur elke scan naar `POST /api/scan`
3. Log fouten zonder de scan-loop te stoppen
4. Test op Raspberry Pi 4B met SPI actief

---

## Stap 5 — Admin-sleutel naar configuratie verplaatsen ⏳ Open

**Doel**  
Hardcoded admin-sleutel vervangen door configuratie via omgevingvariabelen.

**Vervolg**
1. Voeg `ADMIN_API_KEY` toe aan `.env.example`
2. Lees sleutel in via `os.environ` in `backend/main.py`
3. Gebruik die sleutel in `/api/admin/map`
4. Test met juiste en onjuiste sleutel (verwacht 200 vs 401)

---

## Stap 6 — Rooster-integratie met Somtoday/Zermelo ⏳ Open

**Doel**  
Van fake data naar echte roosterbron voor productiegebruik.

**Vervolg**
1. Keuze maken: Somtoday of Zermelo als primaire bron
2. API-authenticatie en tokenbeheer uitwerken
3. Data-omzetter bouwen naar huidig intern roosterformaat
4. Caching en fallback ontwerpen bij API-storingen

---

## Stap 7 — Tests toevoegen ⏳ Open

**Doel**  
Regressies sneller vinden en vertrouwen vergroten bij wijzigingen.

**Vervolg**
1. Voeg backend-tests toe voor `/api/health` en `/api/scan`
2. Test bekende en onbekende tagscenario’s
3. Draai tests in CI zonder stilzwijgend overslaan

---

## Stap 8 — Testen op echte hardware ⏳ Open

**Doel**  
Valideren dat de volledige keten werkt op Raspberry Pi + RC522 + scherm.

**Vervolg**
- [ ] Backend start stabiel op Pi
- [ ] RC522 leest tags betrouwbaar uit
- [ ] Scan toont juiste leerlingrooster op scherm
- [ ] Onbekende tag geeft nette foutmelding
- [ ] Timeout keert terug naar standby
- [ ] Kioskstart en backend-start bij opstarten Pi werken automatisch

---

## Prioriteitstabel (actuele status)

| # | Stap | Prioriteit | Status | Volgende actie |
|---|---|---|---|---|
| 1 | Database repareren | 🔴 Kritiek | ✅ Gerealiseerd | Monitoren via regressietests |
| 2 | Fake data aanpassen | 🔴 Kritiek | ✅ Gerealiseerd | Valideren bij datamodel-wijzigingen |
| 3 | Frontend koppelen | 🟠 Hoog | ✅ Gerealiseerd | Verfijnen UX + hardware-trigger |
| 4 | Hardware-integratie | 🟠 Hoog | ⏳ Open | `rfid_reader.py` implementeren op Pi |
| 5 | Admin-sleutel naar .env | 🟡 Normaal | ⏳ Open | `ADMIN_API_KEY` doorvoeren |
| 6 | Somtoday/Zermelo-koppeling | 🟢 Uitbreiding | ⏳ Open | Bronkeuze + API-spike |
| 7 | Tests toevoegen | 🟡 Normaal | ⏳ Open | `pytest`-tests voor kernflow maken |
| 8 | Testen op hardware | 🟠 Hoog | ⏳ Open | Integratietest op Raspberry Pi plannen |
