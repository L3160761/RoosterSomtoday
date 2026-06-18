"""
RC522 RFID-lezer integratie voor Raspberry Pi 4B
Leest NFC-tags via SPI en retourneert de tag UID

FIXES:
- Juiste pirc522 library configuratie
- Better exception handling
- Debounce for repeated scans
- Debug logging voor troubleshooting
"""

import time
import logging
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Flag om aan te geven of we op een Raspberry Pi zijn
IS_RASPBERRY_PI = False
READER_INSTANCE = None

try:
    import RPi.GPIO as GPIO
    from pirc522 import PIRC522
    IS_RASPBERRY_PI = True
    logger.info("✓ Raspberry Pi GPIO gedetecteerd - RC522 hardware-mode actief")
except ImportError as e:
    logger.warning(f"✗ Raspberry Pi GPIO niet beschikbaar: {e}")
    logger.warning("  → RC522 draait in test-mode")
except RuntimeError as e:
    logger.warning(f"✗ GPIO fout: {e}")
    logger.warning("  → Waarschijnlijk niet op Raspberry Pi")


class RC522Reader:
    """
    RC522 RFID-lezer wrapper voor Raspberry Pi
    Werkt in hardware-mode op Pi, graceful fallback op dev machines
    """
    
    def __init__(self, rst_pin=25, cs_pin=8):
        """
        Initialiseer RC522-lezer
        
        Args:
            rst_pin: GPIO BCM pin voor RST (default: 25 / fysieke pin 22)
            cs_pin: GPIO BCM pin voor CS/SDA (default: 8 / fysieke pin 24)
            
        Pin layout voor Raspberry Pi 4B:
        ┌─────────────────────────────────┐
        │ RC522    → RPi GPIO (BCM)        │
        │ VCC      → 3.3V (Pin 1 of 17)   │
        │ GND      → GND (Pin 6, 9, ...)  │
        │ MISO     → GPIO9 (Pin 21)       │
        │ MOSI     → GPIO10 (Pin 19)      │
        │ SCK      → GPIO11 (Pin 23)      │
        │ SDA/CS   → GPIO8 (Pin 24)       │
        │ RST      → GPIO25 (Pin 22)      │
        └─────────────────────────────────┘
        """
        self.rst_pin = rst_pin
        self.cs_pin = cs_pin
        self.rdr = None
        self.hardware_available = False
        self.last_uid = None
        self.last_scan_time = 0
        self.debounce_seconds = 1.0  # Voorkom dubbele scans binnen 1 seconde
        
        if IS_RASPBERRY_PI:
            self._init_hardware()
        else:
            logger.warning("✗ Hardware niet beschikbaar - test-mode ingeschakeld")
    
    def _init_hardware(self):
        """Initialiseer hardware met error handling"""
        try:
            # Controleer SPI
            if not os.path.exists("/dev/spidev0.0"):
                logger.error("✗ SPI device niet beschikbaar - zet SPI in via raspi-config")
                logger.error("  Commando: sudo raspi-config → Interface Options → SPI → Enable")
                return
            
            # Setup GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Initialiseer PIRC522
            logger.debug(f"→ Initialiseren PIRC522 (RST={self.rst_pin}, CS={self.cs_pin})")
            self.rdr = PIRC522(GPIO_RST=self.rst_pin, GPIO_IRQ=None)
            
            # Test initialisatie
            self.rdr.MFRC522_Init()
            
            self.hardware_available = True
            logger.info(f"✓ RC522 succesvol geïnitialiseerd")
            logger.info(f"  RST pin: GPIO{self.rst_pin} (fysiek pin 22)")
            logger.info(f"  CS pin: GPIO{self.cs_pin} (fysiek pin 24)")
            
        except FileNotFoundError as e:
            logger.error(f"✗ SPI device niet gevonden: {e}")
            logger.error("  Commando: ls -la /dev/spidev*")
            self.hardware_available = False
            
        except PermissionError as e:
            logger.error(f"✗ Permissie geweigerd op SPI device: {e}")
            logger.error("  Fix: sudo usermod -aG spi,gpio $(whoami) && sudo reboot")
            self.hardware_available = False
            
        except Exception as e:
            logger.error(f"✗ RC522 initialisatie fout: {type(e).__name__}: {e}")
            logger.error(f"  Stack: {e.__class__.__module__}.{e.__class__.__name__}")
            self.hardware_available = False
    
    def read_tag(self, timeout=10):
        """
        Lees een RFID-tag
        
        Args:
            timeout: Maximale wachttijd in seconden
            
        Returns:
            Tag UID als string (bijv. "04A1B23C9F") of None als timeout/fout
            
        Flow:
        1. Wacht op tag binnenbereik
        2. Stuurt SELECT-commando naar tag
        3. Haalt unieke identifier op
        4. Retourneert als hex-string
        """
        if not self.hardware_available:
            logger.debug("✗ Hardware niet beschikbaar - retourneer None")
            return None
        
        try:
            start_time = time.time()
            loop_count = 0
            
            while (time.time() - start_time) < timeout:
                loop_count += 1
                
                try:
                    # Stap 1: Wacht op tag
                    self.rdr.wait_for_tag()
                    
                    # Stap 2: Stuur REQUEST naar tag
                    (error, tag_type) = self.rdr.request()
                    
                    if not error:
                        # Stap 3: Bepaal tag UID (anti-collision)
                        (error, uid) = self.rdr.anticoll()
                        
                        if not error:
                            # Stap 4: Formateer UID als hex-string
                            # UID is meestal [byte1, byte2, byte3, byte4, checksum]
                            # We gebruiken de eerste 4 bytes
                            tag_uid = ''.join([f'{x:02X}' for x in uid[:4]])
                            
                            # Debounce: voorkom dubbele scans
                            current_time = time.time()
                            if (tag_uid == self.last_uid and 
                                (current_time - self.last_scan_time) < self.debounce_seconds):
                                logger.debug(f"⊘ Debounce: {tag_uid} genegeerd (recent gescand)")
                                time.sleep(0.1)
                                continue
                            
                            # Succesvol gescand
                            self.last_uid = tag_uid
                            self.last_scan_time = current_time
                            
                            logger.info(f"✓ Tag gescand: {tag_uid}")
                            return tag_uid
                    else:
                        logger.debug(f"✗ Request error: {error}")
                
                except Exception as inner_e:
                    logger.debug(f"✗ Loop exception: {type(inner_e).__name__}: {inner_e}")
                    time.sleep(0.05)
                    continue
                
                time.sleep(0.05)
            
            logger.warning(f"✗ Timeout bereikt na {timeout}s ({loop_count} loops)")
            return None
        
        except Exception as e:
            logger.error(f"✗ Kritieke fout bij lezen tag: {type(e).__name__}: {e}")
            return None
    
    def cleanup(self):
        """Ruim GPIO op"""
        try:
            if IS_RASPBERRY_PI and self.rdr:
                GPIO.cleanup()
                logger.info("✓ GPIO opgeruimd")
        except Exception as e:
            logger.error(f"✗ Fout bij GPIO cleanup: {e}")


def get_reader():
    """
    Krijg de globale RC522-reader instance
    Singleton pattern - één instance per process
    """
    global READER_INSTANCE
    if READER_INSTANCE is None:
        READER_INSTANCE = RC522Reader()
    return READER_INSTANCE


def close_reader():
    """Sluit de reader en cleanup resources"""
    global READER_INSTANCE
    if READER_INSTANCE:
        READER_INSTANCE.cleanup()
        READER_INSTANCE = None


# Test-script
if __name__ == "__main__":
    # Configureer logging voor debug output
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)-8s [%(name)s] %(message)s'
    )
    
    print("\n" + "="*60)
    print("RC522 RFID Reader Test")
    print("="*60)
    print("\nChecklist:")
    print("1. RC522 is op de juiste pins aangesloten")
    print("2. SPI is ingeschakeld (raspi-config → Interface Options → SPI)")
    print("3. Je bent in de spi group (sudo usermod -aG spi $USER)")
    print("\nCommando om test uit te voeren:")
    print("  python3 backend/rfid_reader.py")
    print("\nScan een tag... (Ctrl+C om af te sluiten)")
    print("="*60 + "\n")
    
    reader = get_reader()
    
    if not reader.hardware_available:
        print("\n⚠️  WARNING: RC522 hardware niet gedetecteerd!")
        print("\nOplossingen:")
        print("1. Test of SPI device bestaat:")
        print("   ls -la /dev/spidev*")
        print("\n2. Enable SPI:")
        print("   sudo raspi-config")
        print("   → Interface Options → SPI → Enable → Reboot")
        print("\n3. Voeg jezelf toe aan spi group:")
        print("   sudo usermod -aG spi,gpio $(whoami)")
        print("   sudo reboot")
        print("\n4. Check pin aansluiting (zie code comments)")
        exit(1)
    
    try:
        scan_count = 0
        while True:
            uid = reader.read_tag(timeout=30)
            if uid:
                scan_count += 1
                print(f"\n✓ Scan #{scan_count}: {uid}")
                print(f"  Timestamp: {datetime.now().strftime('%H:%M:%S')}")
            else:
                print("✗ Timeout - geen tag gescand")
    except KeyboardInterrupt:
        print("\n\n✓ Test afgesloten")
        reader.cleanup()
    except Exception as e:
        print(f"\n✗ Fout: {e}")
        reader.cleanup()
        exit(1)
