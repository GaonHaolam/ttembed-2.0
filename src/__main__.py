import os
import sys

# Ensure src directory is in sys.path
sys.path.insert(0, os.path.dirname(__file__))

from app_gui import main

if __name__ == "__main__":
    main()
