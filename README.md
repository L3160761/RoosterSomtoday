# 🎓 RFID Roosterscherm - Pilot V5

Project van Tom, Floris, Zine-Eddine, Rekawt

Een scherm in de aula, waar leerlingen door middel van hun RFID-tag te scannen hun dagrooster kunnen zien. Dit is een telefoonvrije oplossing voor het schoolplein.

## 📋 Projectdoelen
- Leerling scant kluis-tag (RFID/NFC)
- Scherm toont dagrooster van die leerling
- Volledig geautomatiseerd display zonder handmatige invoer
- Veilig en privacygericht (geen echte data in repo)
- Eenvoudig in te stellen en uit te breiden

## 🏗️ Architectuur
Raspberry Pi met RFID lezer (RC522) en HDMI scherm -> Backend API (FastAPI) -> SQLite database en fake data -> Frontend (Kiosk browser)

## 📂 Mappenstructuur
- backend/main.py - FastAPI applicatie
- backend/database_init.py - Database setup
- frontend/index.html - Kiosk webinterface
- data/fake_schedule.json - Nep-roosterdata
- data/tag_mapping.json - Tag-mappings
- requirements.txt - Python dependencies
- .gitignore - Git exclusies
- .env.example - Template configuratie

## 🚀 Installatiehandleiding

### Voorvereisten
- Python 3.8+
- Pip (Python package manager)
- Browser (Chrome/Firefox)
- Git

### Backend opstarten
pip install -r requirements.txt
cd backend
python database_init.py
python main.py

De server draait nu op http://localhost:8000

### Frontend openen
Optie A: Direct openen: frontend/index.html
Optie B: Via Python server: python -m http.server 8001 en open http://localhost:8001/index.html
Optie C: Op Raspberry Pi: chromium-browser --kiosk file:///home/pi/RoosterSomtoday/frontend/index.html

## 🧪 Testen

### Test Tags
04A1B23C9F - wessel
12B4C56D8E - anna
99Z8Y7X6W5 - thomas

### Test-scenario's
1. Standby scherm laadt
2. Scan met bekende tag - rooster verschijnt
3. Scan met onbekende tag - foutmelding
4. Timeout test - na 45 sec terug naar standby
5. Health check: curl http://localhost:8000/api/health

## 📊 API Endpoints

POST /api/scan - Scand RFID tag en geeft rooster terug
GET /api/health - Health check endpoint
POST /api/admin/map - Voeg mapping toe

## 📦 Data Structuur
Lessons hebben: start, end, subject, room, teacher, status
Status waarden: normal, moved, cancelled
Screen-ready JSON bevat: student_display, date, now, next, today, ui

## 🔐 Beveiliging & Privacy
- Geen echte leerlingdata in repository
- Geen API-tokens in code
- .env file in .gitignore
- Logging zonder persoonsgegevens
- Fake data voor testen

## 🐛 Troubleshooting
- ModuleNotFoundError: pip install -r requirements.txt
- Connection refused: check of backend draait
- CORS error: backend CORS is enabled, check console
- Database errors: python database_init.py
- Timeout werkt niet: check JavaScript console
- Port 8000 in gebruik: wijzig poort in main.py

## 👥 Team
Ontwikkelaars: Tom, Floris, Zine-Eddine, Rekawt

## 📝 Licentie
School project - Vrij gebruik