"""
Ponto de entrada principal do sistema Aldemarvin Extractor.
Gerencia a navegação entre telas e ciclo de vida da aplicação.
"""

import tkinter as tk
import sys
import os

# Adiciona o diretório raiz ao path para importações
if getattr(sys, "frozen", False):
    _root = os.path.dirname(sys.executable)
else:
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from src.config import (
    COLORS,
    WINDOW_TITLE,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
)
from src.database.db_manager import DatabaseManager
from src.ui.splash_screen import SplashScreen
from src.ui.main_screen import MainScreen
from src.ui.extraction_form import ExtractionFormDialog
from src.ui.image_capture_screen import ImageCaptureScreen
from src.ui.text_editor_screen import TextEditorScreen


class AldeMarvinApp:
    """Aplicação principal — controla navegação e ciclo de vida."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Esconde enquanto mostra splash
        self.root.title(WINDOW_TITLE)
        self.root.configure(bg=COLORS["bg_primary"])
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        # Centraliza janela principal
        self._center_window(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        # Banco de dados
        self.db = DatabaseManager()

        # Frame container para troca de telas
        self.container = tk.Frame(self.root, bg=COLORS["bg_primary"])
        self.container.pack(expand=True, fill="both")

        self.current_screen = None

        # Protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _center_window(self, width: int, height: int):
        """Centraliza a janela na tela."""
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _clear_container(self):
        """Remove a tela atual do container."""
        if self.current_screen:
            self.current_screen.destroy()
            self.current_screen = None

    def _show_screen(self, screen_class, *args, **kwargs):
        """Exibe uma nova tela no container."""
        self._clear_container()
        self.current_screen = screen_class(self.container, *args, **kwargs)
        self.current_screen.pack(expand=True, fill="both")

    # ─── Navegação ─────────────────────────────────────────────────────────

    def show_main_screen(self):
        """Exibe a tela principal de listagem."""
        self._show_screen(
            MainScreen,
            db_manager=self.db,
            on_new_extraction=self.show_new_extraction_form,
            on_edit=self.show_editor,
            on_continue=self.show_image_capture,
        )

    def show_new_extraction_form(self):
        """Abre o formulário de nova extração."""
        ExtractionFormDialog(
            self.root,
            self.db,
            on_save=self._on_extraction_created,
        )

    def _on_extraction_created(self, extraction_id: int):
        """Callback quando uma extração é criada — abre captura de imagem."""
        self.show_image_capture(extraction_id)

    def show_image_capture(self, extraction_id: int):
        """Exibe a tela de captura de imagem."""
        self._show_screen(
            ImageCaptureScreen,
            db_manager=self.db,
            extraction_id=extraction_id,
            on_back=self.show_main_screen,
        )

    def show_editor(self, extraction_id: int):
        """Exibe o editor de texto com navegação de páginas."""
        self._show_screen(
            TextEditorScreen,
            db_manager=self.db,
            extraction_id=extraction_id,
            on_back=self.show_main_screen,
            on_add_page=lambda: self.show_image_capture(extraction_id),
        )

    # ─── Lifecycle ─────────────────────────────────────────────────────────

    def _on_close(self):
        """Fecha a aplicação de forma limpa."""
        self.db.close()
        self.root.destroy()

    def run(self):
        """Inicia a aplicação com splash screen."""
        # Mostra splash primeiro
        splash = SplashScreen(self.root, on_complete=self._after_splash)
        self.root.mainloop()

    def _after_splash(self):
        """Callback após splash — mostra janela principal."""
        self.root.deiconify()  # Mostra a janela principal
        self.show_main_screen()


def main():
    """Função de entrada."""
    app = AldeMarvinApp()
    app.run()


if __name__ == "__main__":
    main()
