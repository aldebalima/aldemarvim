"""
Converte Aldemarvim.png para .ico para uso no PyInstaller.
Uso: python scripts/create_icon.py
"""

import os
from PIL import Image

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PNG_PATH = os.path.join(ROOT_DIR, "assets", "Aldemarvim.png")
ICO_PATH = os.path.join(ROOT_DIR, "assets", "Aldemarvim.ico")


def create_icon():
    """Converte PNG para ICO com múltiplas resoluções."""
    print("Convertendo Aldemarvim.png para Aldemarvim.ico...")
    
    img = Image.open(PNG_PATH)
    
    # Gera múltiplas resoluções para o .ico (Windows suporta várias)
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ICO_PATH, format="ICO", sizes=icon_sizes)
    
    print(f"OK - Icone criado em: {ICO_PATH}")


if __name__ == "__main__":
    create_icon()
