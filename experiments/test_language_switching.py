#!/usr/bin/env python3
"""
Test script to verify dynamic language switching works without restart.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication
from gui import MainWindow


def main():
    """Test language switching functionality."""
    app = QApplication(sys.argv)

    # Create main window
    window = MainWindow()
    window.show()

    print("Language switching test ready.")
    print("Try changing the language using the dropdown at the top.")
    print("The UI should update immediately without restart.")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
