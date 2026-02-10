"""
Script auxiliar para executar o Aldemarvin Extractor.
Uso: python run.py
"""

import sys
import os

# Garante que o diretório raiz está no path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.main import main

if __name__ == "__main__":
    main()
