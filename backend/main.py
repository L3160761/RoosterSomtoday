from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
from datetime import datetime, timedelta
import logging
import asyncio
from rfid_reader import get_reader
from uid_utils import normalize_tag_uid

app = FastAPI(title="RFID Roosterscherm API", version="0.1.0")

# CORS configuratie - alle origins in development
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "file://",  # Voor lokale HTML-bestanden
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Sta alle origins toe in development
    allow_credentials=True,
    allow_methods=["*"],  # Sta alle methods toe
    allow_headers=["*"],  # Sta alle headers toe
)

# Logging configuratie (geen persoonsgegevens)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_PATH = "data/rooster.db"
FAKE_SCHEDULE_PATH = "data/fake_schedule.json"
ADMIN_API_KEY = "admin_key_pilot"

def get_db():
    """Database verbinding"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def load_fake_schedule():
    """Laad fake roosterdata"""
    try:
        with open(FAKE_SCHEDULE_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Fout bij laden roosterdata: {str(e)}")
        return {}

def verify_admin_key(api_key: str = Header(None)):
    """Verifieer admin API key"""
    if not api_key or api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Ongeautoriseerd - Ongeldige API key")
    return api_key

def get_current_and_next_lesson(lessons, current_time_str):
    """Bepaal huidige en volgende les"""
    current = None
    next_lesson = None
    
    for lesson in lessons:
        start = lesson.get('start', '')
        end = lesson.get('end', '')
        
        if start <= current_time_str < end:
            current = lesson
        elif start >= current_time_str and next_lesson is None:
            next_lesson = lesson
    
    return current, next_lesson

def get_schedule_response(user_key):
    """Bouw een schedule-response voor een user_key"""
    # Laad roosterdata
    schedule_data = load_fake_schedule()
    lessons = schedule_data.get(user_key, {}).get('lessons', [])
    
    if not lessons:
        logger.warning(f"Geen rooster gevonden voor user_key: {user_key}")
        return None
    
    # Bepaal huidige en volgende les
    now = datetime.now()
    current_time_str = now.strftime("%H:%M")
    today_date = now.strftime("%Y-%m-%d")
    
    current_lesson, next_lesson = get_current_and_next_lesson(lessons, current_time_str)
    
    # Haal student display naam
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT display_name FROM students WHERE user_key = ?", (user_key,))
    student_result = cursor.fetchone()
    conn.close()
    
    display_name = student_result['display_name'] if student_result else user_key
    
    # Bouw response (screen-ready JSON)
    response = {
        "student_display": display_name,
        "date": today_date,
        "now": current_lesson if current_lesson else None,
        "next": next_lesson if next_lesson else None,
        "today": lessons,
        "ui": {
            "timeout_seconds": 15
        }
    }
    
    return response

@app.get("/api/health")
async def health_check():
    """Health check endpoint - publiek beschikbaar"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0"
    }

@app.post("/api/scan")
async def scan_tag(tag_data: dict):
    """
    Scan endpoint: ontvangt tag UID, returnt rooster
    
    Request: {"tag_uid": "04A1B23C9F"}
    Response: screen-ready JSON met rooster
    """
    try:
        tag_uid = normalize_tag_uid(tag_data.get("tag_uid", ""))
    except ValueError as exc:
        logger.warning("Ongeldige tag_uid ontvangen")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    
    # Zoek tag in database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_key FROM tags WHERE tag_uid = ? AND active = 1", (tag_uid,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        logger.info(f"Onbekende tag gescand: {tag_uid[:4]}...{tag_uid[-4:]}")
        raise HTTPException(status_code=404, detail="Tag onbekend")
    
    user_key = result['user_key']
    response = get_schedule_response(user_key)
    
    if not response:
        raise HTTPException(status_code=404, detail="Rooster niet beschikbaar")
    
    logger.info(f"Scan succesvol verwerkt voor: {user_key}")
    return response

@app.get("/api/scan-hardware")
async def scan_hardware(timeout: int = 10):
    """
    Hardware-scan endpoint: lees RC522 RFID-tag van Raspberry Pi
    
    Query params:
    - timeout: Maximale wachttijd in seconden (default: 10)
    
    Response: Zoals /api/scan (screen-ready JSON) of foutmelding
    """
    if timeout < 1 or timeout > 60:
        raise HTTPException(status_code=400, detail="Timeout moet tussen 1 en 60 seconden zijn")
    
    reader = get_reader()
    
    # Controleer of hardware beschikbaar is
    if not reader.hardware_available:
        logger.warning("RC522 hardware niet beschikbaar")
        raise HTTPException(
            status_code=503,
            detail="RC522 hardware niet beschikbaar (niet op Raspberry Pi of SPI niet ingeschakeld?)"
        )
    
    logger.info(f"Hardware-scan gestart (timeout: {timeout}s)")
    
    # Lees tag (async-safe met timeout)
    try:
        tag_uid = await asyncio.wait_for(
            asyncio.to_thread(reader.read_tag, timeout),
            timeout=timeout + 1
        )
    except asyncio.TimeoutError:
        logger.warning("Hardware-scan timeout bereikt")
        raise HTTPException(status_code=408, detail="Geen tag gescand (timeout)")
    except Exception as e:
        logger.error(f"Fout bij hardware-scan: {e}")
        raise HTTPException(status_code=500, detail=f"Fout bij hardware-scan: {str(e)}")
    
    if not tag_uid:
        logger.warning("Geen tag gescand")
        raise HTTPException(status_code=408, detail="Geen tag gescand")
    
    # Zoek tag in database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_key FROM tags WHERE tag_uid = ? AND active = 1", (tag_uid,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        logger.info(f"Onbekende tag gescand: {tag_uid[:4]}...{tag_uid[-4:]}")
        raise HTTPException(status_code=404, detail="Tag onbekend")
    
    user_key = result['user_key']
    response = get_schedule_response(user_key)
    
    if not response:
        raise HTTPException(status_code=404, detail="Rooster niet beschikbaar")
    
    logger.info(f"Hardware-scan succesvol verwerkt voor: {user_key}")
    return response

@app.post("/api/admin/map")
async def add_mapping(mapping_data: dict, api_key: str = Depends(verify_admin_key)):
    """
    Admin endpoint: voeg mapping toe
    Requires: X-API-Key header met admin_key_pilot
    """
    user_key = mapping_data.get("user_key")
    display_name = mapping_data.get("display_name", user_key)

    if not user_key:
        raise HTTPException(status_code=400, detail="user_key is verplicht")

    try:
        tag_uid = normalize_tag_uid(mapping_data.get("tag_uid", ""))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    
    # Validatie: alleen bepaalde user_keys allowed
    allowed_users = ["zine", "tom", "rekawt"]
    if user_key not in allowed_users:
        logger.warning(f"Poging om niet-toegestane user_key toe te voegen: {user_key}")
        raise HTTPException(status_code=403, detail=f"User key '{user_key}' is niet toegestaan. Alleen: {', '.join(allowed_users)}")
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Voeg tag toe
        cursor.execute(
            "INSERT OR REPLACE INTO tags (tag_uid, user_key, active) VALUES (?, ?, 1)",
            (tag_uid, user_key)
        )
        
        # Voeg/update student toe
        cursor.execute(
            "INSERT OR REPLACE INTO students (user_key, display_name) VALUES (?, ?)",
            (user_key, display_name)
        )
        
        conn.commit()
        conn.close()
        
        logger.info(f"Mapping toegevoegd: {tag_uid[:4]}... -> {user_key}")
        return {"status": "ok", "message": f"Mapping toegevoegd voor {user_key}"}
    
    except Exception as e:
        logger.error(f"Fout bij toevoegen mapping: {str(e)}")
        raise HTTPException(status_code=500, detail="Fout bij opslaan mapping")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
