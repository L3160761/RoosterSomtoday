# Overdracht — RoosterSomtoday

Dit document helpt een nieuw leerlingteam om snel en veilig verder te werken.

## 1. Huidige projectstatus

Het project zit in een werkende prototypefase:
- backend werkt en reageert op scans
- fake data en database sluiten op elkaar aan
- frontend kan backend aanroepen met test tag-UID

Tegelijk zijn belangrijke vervolgstappen nog open (hardware-integratie, beveiliging admin key, echte roosterkoppeling, tests).

## 2. Wat werkt al

- `backend/database_init.py` maakt de verwachte SQLite-database aan
- `POST /api/scan` geeft roosterdata terug voor bekende tags
- `GET /api/health` werkt voor snelle controle
- frontend bevat testscan-flow en toont rooster/fouten
- timeout-gedrag naar standby is aanwezig in frontend

## 3. Wat nog niet af is

- RC522 is nog niet direct gekoppeld via een hardware-reader script
- admin endpoint gebruikt nog een hardcoded sleutel
- er is nog geen Somtoday/Zermelo API-koppeling
- er zijn nog geen backend-tests toegevoegd
- end-to-end testen op echte Raspberry Pi-opstelling ontbreken

## 4. Aanbevolen werkvolgorde voor het leerlingteam

1. **Stap 4: Hardware-integratie**  
   Bouw eerst een betrouwbare RC522 → backend scan-loop op Raspberry Pi.
2. **Stap 5: Beveiliging admin key**  
   Verplaats hardcoded sleutel naar `.env` configuratie.
3. **Stap 7: Tests toevoegen**  
   Leg basisgedrag vast met `pytest` voordat grote integraties starten.
4. **Stap 6: Echte roosterkoppeling**  
   Koppel daarna pas Somtoday/Zermelo aan het bestaande interne formaat.
5. **Stap 8: Hardware-eindtest**  
   Sluit af met complete praktijktest op Pi + RC522 + scherm.

## 5. Bekende risico’s en aandachtspunten

- **Pad-afhankelijkheid**: start backend vanuit repository-root, anders kloppen relatieve paden mogelijk niet.
- **Hardware-afhankelijkheid**: RC522-testen kan niet volledig op normale laptop/pc.
- **Beveiliging**: hardcoded admin key eerst oplossen vóór bredere uitrol.
- **Externe API-risico’s**: Somtoday/Zermelo kan rate limits of auth-complexiteit geven.
- **Stabiliteit zonder tests**: zonder geautomatiseerde tests is regressierisico hoger.

## 6. Eerste documenten om te lezen

1. [`docs/vervolgstappen.md`](vervolgstappen.md)
2. [`docs/testen.md`](testen.md)
3. [`docs/hardware-rc522.md`](hardware-rc522.md)
4. [`docs/architectuur.md`](architectuur.md)

