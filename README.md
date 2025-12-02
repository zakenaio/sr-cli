# SR CLI

Ett enkelt och kraftfullt kommandoradsverktyg för att lyssna på Sveriges Radio direkt i terminalen.

## Funktioner

- **Interaktivt läge:** Bläddra och välj bland alla SR:s kanaler.
- **Direktval:** Starta en kanal direkt med argument (t.ex. `sr-cli p3`).
- **TUI (Text User Interface):** Snyggt gränssnitt som visar nuvarande program och låt.
- **Metadata:** Uppdaterar automatiskt information om vad som spelas.

## Förutsättningar

Du behöver ha `mpv` installerat för ljuduppspelning.

### Installation av mpv

- **Ubuntu/Debian:** `sudo apt install mpv`
- **Arch Linux:** `sudo pacman -S mpv`
- **macOS (Homebrew):** `brew install mpv`

## Installation

1. Ladda ner skriptet `sr-cli.py`.
2. Gör det körbart:
   ```bash
   chmod +x sr-cli.py
   ```
3. (Valfritt) Installera det globalt:
   ```bash
   sudo mv sr-cli.py /usr/local/bin/sr-cli
   ```

## Användning

### Interaktivt
Kör bara kommandot utan argument:
```bash
sr-cli
```

### Direktval
Ange kanalens namn:
```bash
sr-cli p1
sr-cli "p4 stockholm"
sr-cli "din gata"
```

### Avsluta
Tryck `Ctrl+C` för att stoppa uppspelningen och avsluta.


### Att göra 
Make it pretty. 
Snygga till gränssnitt, bättre användande av yta. 
Möjlighet till att byta kanal/program direkt i cli utan att avsluta.

