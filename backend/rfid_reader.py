"""
RC522 RFID-lezer integratie voor Raspberry Pi 4B
Leest NFC-tags via SPI en retourneert de tag UID
"""

import time
import logging

logger = logging.getLogger(__name__)

# Flag om aan te geven of we op een Raspberry Pi zijn
IS_RASPBERRY_PI = False

try:
    import RPi.GPIO as GPIO
    from pirc522 import PIRC522
    IS_RASPBERRY_PI = True
    logger.info("Raspberry Pi GPIO gedetecteerd - RC522 hardware-mode actief")
except ImportError:
    logger.warning("Raspberry Pi GPIO niet beschikbaar - RC522 in test-mode")
except RuntimeError as e:
    logger.warning(f"GPIO fout (mogelijk niet op Pi): {e} - RC522 in test-mode")


class RC522Reader:
    """
    RC522 RFID-lezer wrapper
    Werkt in hardware-mode op Raspberry Pi, test-mode op andere platforms
    """
    
    def __init__(self, rst_pin=25, cs_pin=8):
        """
        Initialiseer RC522-lezer
        
        Args:
            rst_pin: GPIO pin voor RST (default: 25 / pin 22)
            cs_pin: GPIO pin voor CS/SS (default: 8 / pin 24)
        """
        self.rst_pin = rst_pin
        self.cs_pin = cs_pin
        self.rdr = None
        self.hardware_available = False
        
        if IS_RASPBERRY_PI:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
                self.rdr = PIRC522(GPIO_RST=rst_pin, GPIO_IRQ=None)
                self.hardware_available = True
                logger.info(f"RC522 succesvol geïnitialiseerd (RST={rst_pin}, CS={cs_pin})")
            except Exception as e:
                logger.error(f"Fout bij initialisatie RC522: {e}")
                self.hardware_available = False
    
    def read_tag(self, timeout=10):
        """
        Lees een RFID-tag
        
        Args:
            timeout: Maximale wachttijd in seconden
            
        Returns:
            Tag UID als string (bijv. "04A1B23C9F") of None als timeout/fout
        """
        if not self.hardware_available:
            logger.debug("Hardware niet beschikbaar - retourneer None")
            return None
        
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # Wacht tot een tag dicht genoeg is
                self.rdr.wait_for_tag()
                
                # Vraag om tag
                (error, tag_type) = self.rdr.request()
                if not error:
                    # Bepaal tag UID
                    (error, uid) = self.rdr.anticoll()
                    if not error:
                        # Formateer UID als hex-string (eerste 4 bytes)
                        tag_uid = ''.join(['{:02X}'.format(x) for x in uid[:4]])
                        logger.info(f"Tag gescand: {tag_uid}")
                        return tag_uid
                
                time.sleep(0.05)
            
            logger.warning(f"Timeout bereikt na {timeout} seconden - geen tag gescand")
            return None
        
        except Exception as e:
            logger.error(f"Fout bij lezen tag: {e}")
            return None
    
    def cleanup(self):
        """Ruim GPIO op"""
        try:
            if IS_RASPBERRY_PI:
                GPIO.cleanup()
                logger.info("GPIO opgeruimd")
        except Exception as e:
            logger.error(f"Fout bij GPIO opruiming: {e}")


# Globale reader instance
_reader_instance = None


def get_reader():
    """Krijg de globale RC522-reader instance"""
    global _reader_instance
    if _reader_instance is None:
        _reader_instance = RC522Reader()
    return _reader_instance


# Test-script (zet als __main__ uit)
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print("RC522 Test - Scan een tag (Ctrl+C om af te sluiten)...")
    
    reader = get_reader()
    
    try:
        while True:
            uid = reader.read_tag(timeout=30)
            if uid:
                print(f"✓ Tag gescand: {uid}")
            else:
                print("✗ Geen tag gescand")
    except KeyboardInterrupt:
        print("\nAfgesloten")
        reader.cleanup()
