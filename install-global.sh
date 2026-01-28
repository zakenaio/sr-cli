#!/bin/bash

echo "--- SR-TUI Global Installation ---"
echo ""

# Check if mpv is installed
if ! command -v mpv &> /dev/null; then
    echo "❌ Error: mpv not found. Please install mpv first:"
    echo "   sudo apt install mpv  # Debian/Ubuntu"
    echo "   sudo dnf install mpv  # Fedora"
    echo "   sudo pacman -S mpv    # Arch"
    exit 1
fi

# Check if pipx is installed
if ! command -v pipx &> /dev/null; then
    echo "⚠️  pipx not found. Installing pipx..."
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    
    echo ""
    echo "✅ pipx installed. Please restart your terminal or run:"
    echo "   source ~/.bashrc  # or ~/.zshrc or ~/.config/fish/config.fish"
    echo ""
    echo "Then run this script again."
    exit 0
fi

# Install sr-tui with pipx
echo "📦 Installing sr-tui globally with pipx..."
pipx install .

echo ""
echo "✅ Installation complete!"
echo ""
echo "You can now run 'sr-tui' from anywhere!"
echo ""
