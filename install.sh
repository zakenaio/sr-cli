#!/bin/bash

# --- Konfiguration ---
COMMAND_NAME="sr-tui"
MAIN_SCRIPT="sr-tui.py" # Huvudfilen som ska köras
PROJECT_DIR=$(pwd)
VENV_DIR="$PROJECT_DIR/.venv"
# ~/.local/bin/ är standardplats för användarspecifika binärer på Linux
BIN_DIR="$HOME/.local/bin"

echo "--- SR-TUI Installationsguide ---"
echo "Kontrollerar beroenden..."

# 1. Kontrollera grundläggande verktyg
if ! command -v python3 &> /dev/null || ! command -v pip &> /dev/null; then
    echo "Fel: Python3 och/eller pip är inte installerat eller hittas inte i PATH."
    echo "Vänligen installera dessa först."
    exit 1
fi

# 2. Skapa den virtuella miljön (.venv)
echo "Skapar virtuell miljö i $VENV_DIR..."
python3 -m venv "$VENV_DIR"

# 3. Aktivera och installera beroenden
# Notera: Vi aktiverar bara för installationsstegen
source "$VENV_DIR/bin/activate"

if [ -f requirements.txt ]; then
    echo "Installerar Python-beroenden från requirements.txt..."
    pip install -r requirements.txt
else
    echo "VARNING: requirements.txt hittades inte. Fortsätter utan att installera beroenden."
fi

# Deaktivera miljön efter installation
deactivate

# 4. Skapa en global 'wrapper' (symbolisk länk)
echo "Skapar en global länk ($COMMAND_NAME) i $BIN_DIR..."

mkdir -p "$BIN_DIR"

# Skapa ett skript i ~/.local/bin/ som pekar på den isolerade Python-miljön
WRAPPER_SCRIPT="$BIN_DIR/$COMMAND_NAME"

# Vi använder en HEREDOC (cat << EOF) för att skriva wrapper-skriptet säkert
cat << EOF > "$WRAPPER_SCRIPT"
#!/bin/bash
# Detta skript kör $MAIN_SCRIPT med dess isolerade virtuella miljö.
# Sökväg till Venv: $VENV_DIR
# Sökväg till Skript: $PROJECT_DIR/$MAIN_SCRIPT

# Kör scriptet med Venv Python-tolken, skicka alla argument (\$@) vidare
"$VENV_DIR/bin/python" "$PROJECT_DIR/$MAIN_SCRIPT" "\$@"

EOF

# Gör wrapper-skriptet körbart
chmod +x "$WRAPPER_SCRIPT"

# 5. Slutförande
echo " "
echo "✅ Installationen är klar!"
echo " "
echo "För att testa, se till att du har '$BIN_DIR' i din PATH."

# Liten check om ~/.local/bin/ redan är i PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "⚠️ NOTERA: $BIN_DIR är inte i din PATH just nu."
    echo "För att uppdatera PATH (kan behöva göras i en ny terminal):"
    echo 'export PATH=$PATH:$HOME/.local/bin'
else
    echo "Kör kommandot:"
fi
echo ">>> $COMMAND_NAME"
echo " "
