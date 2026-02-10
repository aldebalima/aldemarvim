"""
Configurações globais do sistema Aldemarvin Extractor.
"""

import os
import sys

# ─── Diretórios ────────────────────────────────────────────────────────────────
APP_NAME = "Aldemarvin"
APP_VERSION = "1.0.0"

# Diretório base da aplicação (funciona tanto em dev quanto empacotado)
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
DB_DIR = os.path.join(DATA_DIR, "db")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
EXPORTS_DIR = os.path.join(DATA_DIR, "exports")

# Garante que os diretórios existam
for d in [DATA_DIR, DB_DIR, ASSETS_DIR, EXPORTS_DIR]:
    os.makedirs(d, exist_ok=True)

# ─── Banco de Dados ───────────────────────────────────────────────────────────
DB_PATH = os.path.join(DB_DIR, "aldemarvin.json")

# ─── Janela ────────────────────────────────────────────────────────────────────
WINDOW_TITLE = f"{APP_NAME} - Extrator de Texto"
WINDOW_MIN_WIDTH = 1100
WINDOW_MIN_HEIGHT = 700
SPLASH_DURATION_MS = 3000  # 3 segundos

# ─── Cores (tema escuro moderno) ──────────────────────────────────────────────
COLORS = {
    "bg_primary": "#1a1a2e",
    "bg_secondary": "#16213e",
    "bg_card": "#0f3460",
    "accent": "#e94560",
    "accent_hover": "#ff6b6b",
    "text_primary": "#eaeaea",
    "text_secondary": "#a8a8a8",
    "success": "#00b894",
    "warning": "#fdcb6e",
    "danger": "#d63031",
    "danger_hover": "#e17055",
    "border": "#2d3748",
    "input_bg": "#1e2a3a",
    "button_bg": "#e94560",
    "button_text": "#ffffff",
    "loading_bar": "#e94560",
    "loading_bg": "#2d3748",
}

# ─── Fontes ────────────────────────────────────────────────────────────────────
FONTS = {
    "title": ("Segoe UI", 24, "bold"),
    "subtitle": ("Segoe UI", 16),
    "heading": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 12),
    "body_bold": ("Segoe UI", 12, "bold"),
    "small": ("Segoe UI", 10),
    "splash_title": ("Segoe UI", 32, "bold"),
    "mono": ("Consolas", 11),
}

# ─── OCR ───────────────────────────────────────────────────────────────────────
# Caminho do Tesseract embutido (quando empacotado como .exe)
if getattr(sys, "frozen", False):
    _bundled = os.path.join(BASE_DIR, "tesseract", "tesseract.exe")
else:
    _bundled = None

# Ordem de busca: embutido → instalação padrão Windows → PATH do sistema
TESSERACT_PATHS_WIN = [
    p for p in [
        _bundled,
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ] if p is not None
]
TESSERACT_CMD_LINUX = "/usr/bin/tesseract"
OCR_LANG = "eng"  # Idioma padrão para OCR

# ─── Tradução ─────────────────────────────────────────────────────────────────
TRANSLATE_SOURCE = "en"
TRANSLATE_TARGET = "pt"
