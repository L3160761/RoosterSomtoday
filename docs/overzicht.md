# Projectoverzicht — RFID Roosterscherm

## Wat is dit project?

Het RFID Roosterscherm is een systeem waarmee leerlingen op school hun dagrooster kunnen bekijken zonder hun telefoon te gebruiken. Een leerling houdt zijn of haar kluis-tag (RFID/NFC) voor een lezer, en op het scherm verschijnt meteen het rooster van die leerling voor die dag.

Het systeem is bedoeld als een vaste opstelling in de aula of gang: een scherm dat altijd aan is en automatisch reageert op tags.

## Wie hebben dit gebouwd?

**Team:** Tom, Floris, Zine-Eddine, Rekawt

## Waarom bestaat dit project?

Op veel scholen zijn telefoons verboden of ontmoedigd. Toch willen leerlingen snel hun rooster checken. Dit systeem biedt een telefoonvrij alternatief: scan je kluis-tag en je ziet je rooster.

## Hoe werkt het in het kort?

1. Leerling houdt RFID-tag voor de lezer (op een Raspberry Pi)
2. De tag-UID wordt naar de backend gestuurd
3. De backend zoekt de bijbehorende leerling op in de database
4. Het rooster van die leerling wordt geladen
5. Het scherm toont de huidige les, de volgende les en het dagoverzicht
6. Na 45 seconden keert het scherm terug naar het standby-scherm

## Wat zijn de onderdelen?

| Onderdeel | Beschrijving |
|---|---|
| **Raspberry Pi** | Hardware: de computer die alles aanstuurt |
| **RC522 RFID-lezer** | Leest de tag-UID van de leerling |
| **HDMI-scherm** | Toont het rooster |
| **Backend (FastAPI)** | Verwerkt de scan en geeft roosterdata terug |
| **Database (SQLite)** | Slaat tag-koppelingen en leerlingnamen op |
| **Frontend (HTML/JS)** | De webpagina die op het scherm wordt getoond |
| **Fake data** | Testrooster en tagmappings voor ontwikkeling |

## Wat is de huidige stand?

Het project is in een **MVP-/prototypefase**. De basisarchitectuur staat en de kernlogica is gebouwd. Er zijn echter nog inconsistenties tussen de onderdelen die opgelost moeten worden voordat het systeem echt stabiel draait. Zie [`status.md`](status.md) voor een gedetailleerd overzicht.

## Meer lezen

- [Architectuur en datastromen](architectuur.md)
- [Huidige status en bekende problemen](status.md)
- [Vervolgstappen en prioriteiten](vervolgstappen.md)
