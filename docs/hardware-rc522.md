# Hardwarehandleiding — RC522 op Raspberry Pi 4B

Deze handleiding laat zien hoe je een RC522 RFID-lezer aansluit op een Raspberry Pi 4B via SPI.

## Belangrijk vooraf

- Gebruik **altijd 3.3V** voor de RC522 (geen 5V)
- Zorg dat **SPI is ingeschakeld** op de Raspberry Pi
- `IRQ` is voor deze basisopstelling niet nodig

## Aansluitschema (standaard SPI)

| RC522 pin | Raspberry Pi 4B | Fysieke pin |
|---|---|---:|
| VCC | 3.3V | pin 1 (of 17) |
| GND | GND | pin 6 |
| RST | GPIO25 | pin 22 |
| SDA / SS | CE0 / GPIO8 | pin 24 |
| SCK | GPIO11 / SCLK | pin 23 |
| MOSI | GPIO10 | pin 19 |
| MISO | GPIO9 | pin 21 |
| IRQ | Niet gebruiken | — |

## SPI inschakelen op Raspberry Pi

```bash
sudo raspi-config
```

Ga naar:
1. **Interface Options**
2. **SPI**
3. **Enable**

Herstart daarna de Raspberry Pi.

## Praktische tips voor leerlingen

- Zet de Pi uit voordat je bedrading wijzigt
- Controleer elke draad dubbel op juiste pin
- Als de lezer niet werkt: controleer eerst voeding (3.3V) en SPI-instelling
- Test stap voor stap: eerst backend werkend, daarna pas hardware uitlezen

