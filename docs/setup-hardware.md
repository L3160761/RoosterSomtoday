# Setup Hardware RC522 RFID Reader

## Wat betekent de fout?
```
WARNING:__main__:RC522 hardware niet beschikbaar
```

Dit betekent dat de RC522 RFID-lezer niet wordt herkend. Dit kan aan deze dingen liggen:

## 1. SPI Inschakelen (BELANGRIJK!)

Op de Raspberry Pi moet SPI worden ingeschakeld via raspi-config:

```bash
sudo raspi-config
```

Navigeer naar:
- **Interface Options** → **SPI** → **Yes** → Bevestigen
- **Interface Options** → **I2C** → **Yes** → Bevestigen (ook nodig)

Daarna **reboot**:
```bash
sudo reboot
```

## 2. Controleer Physical Pin Aansluiting

De RC522 RFID-lezer moet op deze Raspberry Pi GPIO pins worden aangesloten:

| RC522 Pin | RPi GPIO Pin | BCM # |
|-----------|--------------|-------|
| VCC       | Pin 2        | 5V    |
| GND       | Pin 6        | GND   |
| MISO      | Pin 21       | GPIO9 |
| MOSI      | Pin 19       | GPIO10|
| SCK       | Pin 23       | GPIO11|
| SDA/CS    | Pin 24       | GPIO8 |
| RST       | Pin 22       | GPIO25|

**Visueel schema:**
```
RC522    →  Raspberry Pi 4B
VCC      →  5V (Pin 2)
GND      →  GND (Pin 6)
MOSI     →  GPIO10 (Pin 19)
MISO     →  GPIO9 (Pin 21)
SCK      →  GPIO11 (Pin 23)
SDA/CS   →  GPIO8 (Pin 24) - Chip Select
RST      →  GPIO25 (Pin 22)
```

## 3. Test of SPI werkt

```bash
# Check of SPI device bestaat
ls -l /dev/spidev*

# Output moet zijn:
# crw-rw---- 1 root spi ... /dev/spidev0.0
# crw-rw---- 1 root spi ... /dev/spidev0.1
```

## 4. Zorg dat je user in spi group zit

```bash
# Voeg pi user toe aan spi group
sudo usermod -aG spi pi

# Logout en login opnieuw (of restart)
sudo reboot
```

## 5. Test de Dependencies

```bash
# Test of alles geïnstalleerd is
python3 -c "import RPi.GPIO; print('GPIO OK')"
python3 -c "import spidev; print('SPIDEV OK')"
python3 -c "from pirc522 import PIRC522; print('PIRC522 OK')"
```

## 6. Test de Reader Direct

```bash
cd /path/to/RoosterSomtoday
python3 backend/rfid_reader.py
```

Je zou moeten zien:
```
Raspberry Pi GPIO gedetecteerd - RC522 hardware-mode actief
RC522 succesvol geïnitialiseerd (RST=25, CS=8)
RC522 Test - Scan een tag...
```

Scan een tag en je ziet:
```
✓ Tag gescand: 04A1B23C9F
```

## 7. Als het nog steeds niet werkt

### Check de logs:
```bash
sudo journalctl -u backend.service -f  # Als je systemd service hebt

# Of direct in backend logs
tail -f /var/log/rooster-backend.log
```

### Controleer pin configuratie in code

In `backend/rfid_reader.py` zijn de pin nummers:
- `rst_pin=25` (RST pin, GPIO25)
- `cs_pin=8` (CS/SDA pin, GPIO8)

Als je andere pins gebruikt hebt, wijzig deze numbers.

### Test met verbeterde logging

```bash
# Zet verbeterde debug aan
LOGLEVEL=DEBUG python3 backend/main.py
```

## Veelgestelde problemen

### "No module named RPi.GPIO"
```bash
# Herinstalleer dependencies
sudo pip3 install -r requirements.txt
```

### "SPI device not found"
- SPI is niet ingeschakeld in raspi-config
- Je bent niet in de spi group
- De hardware pins zijn niet correct aangesloten

### "Permission denied /dev/spidev0.0"
```bash
# Geef jezelf permissions
sudo usermod -aG spi $(whoami)
sudo usermod -aG gpio $(whoami)
sudo reboot
```

### Pin mismatch
- RC522 is op verkeerde pins aangesloten
- Wijzig `rst_pin` en `cs_pin` in `backend/rfid_reader.py` als nodig

## Sneltest na setup

Als alles werkt, test je de volledige flow:

```bash
# Terminal 1: Backend starten
python3 backend/main.py

# Terminal 2: Frontend openen en tag scannen
# Open frontend/index.html in browser
# Scan een tag met de RC522 lezer
```

In je browser debug panel zou je moeten zien:
```
✓ Rooster geladen voor [Student naam]
```
