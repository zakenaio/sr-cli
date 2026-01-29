# SR TUI 🎵

Ett modernt och vackert kommandoradsverktyg för att lyssna på Sveriges Radio direkt i terminalen. Stöder både **live-radio** och **poddar**. Inspirerat av Spotify's design.

## Funktioner

- **Radio & Poddar:** Stöd för livekanaler och uppspelning av poddavsnitt.
- **Spotify-inspirerat gränssnitt:** Mörkt tema med gröna accenter (#1DB954).
- **Dynamisk Layout:** Två/Trekolumnslayout beroende på läge.
- **Full Tangentbordsnavigering:** Navigera, byt läge och sök utan att lämna gränssnittet.
- **Sökfunktion:** Filtrera kanaler/poddar i realtid.
- **Live-metadata:** Visar nuvarande program och låt (för radio).
- **Podcast-kontroll:** Spola framåt/bakåt (15 sek) och visa uppspelningsposition.
- **Smidig hantering:** Byt mellan kanaler/avsnitt utan att starta om appen.

## Förutsättningar

Du behöver ha följande installerat:

- **Python 3.7+**
- **mpv** (för ljuduppspelning)

### Installation av mpv

- **Ubuntu/Debian:** `sudo apt install mpv`
- **Arch Linux (CachyOS):** `sudo pacman -S mpv`
- **macOS (Homebrew):** `brew install mpv`

## Installation

Installationen är automatiserad med ett skript. Det skapar en virtuell miljö (`.venv`) och en global länk (`sr-tui`) i `~/.local/bin/`.

1. Klona eller ladda ner projektet.
2. Gå till projektmappen och gör installationsskriptet körbart:
   ```bash
   chmod +x install.sh
   ```
3. Kör installationsskriptet:
   ```bash
   ./install.sh
   ```
4. **Starta:** Öppna en ny terminal eller uppdatera din PATH (om det behövs) och kör:
   ```bash
   sr-tui
   ```

## Tangentbordskommandon

| Tangent | Läge | Funktion |
|---------|----------|----------|
| `Tab` | Alla | Växla mellan Radio och Podcast-läge |
| `↑` / `↓` | Alla | Navigera upp/ner i listor |
| `Enter` | Radio | Spela vald kanal |
| `Enter` | Podcast | Välj Podd (ladda avsnitt) / Spela avsnitt |
| `Space` | Alla | Pausa/Återuppta uppspelning |
| `→` | Podcast | Hoppa till Avsnittslistan / Spola framåt 15 sek |
| `←` | Podcast | Hoppa till Poddlistan / Spola bakåt 15 sek |
| `/` | Alla | Sök/filtrera listor |
| `Esc` | Alla | Rensa sökning (Radio) / Avsluta sökning (Podcast) |
| `q` | Alla | Avsluta programmet |

## Design

Gränssnittet är inspirerat av Spotify och använder:
- **Färgschema:** Mörk bakgrund (#191414) med Spotify-grön accent (#1DB954)
- **Layout:** Dynamisk layout med listor och "Now Playing"-vy
- **Typografi:** Tydlig och modern textformering med `rich`-biblioteket

## 🛠️ Teknisk information

Byggt med:
- **requests** - API-anrop till Sveriges Radio
- **rich** - Modern TUI med färger och layout
- **mpv** - Ljuduppspelning

## Att göra:
- **Möjlighet till att byta kanal/program direkt i cli utan att avsluta**
- **Snygga till gränssnitt, bättre användande av yta**
- **Offline-funktioner** - Möjlighet att ladda ner poddavsnitt för offline-lyssning
- **Favoriter** - Spara favoritkanaler/poddar
