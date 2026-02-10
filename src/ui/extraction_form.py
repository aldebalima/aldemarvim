"""
Formulário para criação de nova extração.
Campos: Nome, Versão, Tipo (texto livre).
A combinação Nome + Versão + Tipo deve ser única.
"""

import tkinter as tk

from src.config import COLORS, FONTS
from src.ui.base import StyledButton, StyledEntry, StyledFrame, StyledLabel


class ExtractionFormDialog(tk.Toplevel):
    """Diálogo modal para criar uma nova extração."""

    def __init__(self, master, db_manager, on_save: callable):
        super().__init__(master)
        self.db = db_manager
        self.on_save = on_save
        self.extraction_id = None

        # ── Configuração ───────────────────────────────────────────────────
        self.title("Nova Extração")
        self.configure(bg=COLORS["bg_primary"])
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        # Centraliza
        width, height = 500, 520
        x = master.winfo_rootx() + (master.winfo_width() - width) // 2
        y = master.winfo_rooty() + (master.winfo_height() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        # ── Layout ─────────────────────────────────────────────────────────
        self._build_ui()

        # Bind ESC
        self.bind("<Escape>", lambda e: self.destroy())

    def _build_ui(self):
        """Constrói a interface do formulário."""
        main = StyledFrame(self)
        main.pack(expand=True, fill="both", padx=30, pady=25)

        # Título
        StyledLabel(
            main, text="📝 Nova Extração", style="title"
        ).pack(anchor="w", pady=(0, 20))

        # ── Nome ───────────────────────────────────────────────────────────
        StyledLabel(main, text="Nome da Extração *", style="body_bold").pack(
            anchor="w", pady=(0, 5)
        )
        self.name_entry = StyledEntry(main, placeholder="Ex: Clean Code")
        self.name_entry.pack(fill="x", pady=(0, 15), ipady=6)

        # ── Versão ─────────────────────────────────────────────────────────
        StyledLabel(main, text="Versão *", style="body_bold").pack(
            anchor="w", pady=(0, 5)
        )
        self.version_entry = StyledEntry(main, placeholder="Ex: 1ª Edição")
        self.version_entry.pack(fill="x", pady=(0, 15), ipady=6)

        # ── Tipo ───────────────────────────────────────────────────────────
        StyledLabel(main, text="Tipo *", style="body_bold").pack(
            anchor="w", pady=(0, 5)
        )
        self.type_entry = StyledEntry(main, placeholder="Ex: Livro, Artigo, Manual...")
        self.type_entry.pack(fill="x", pady=(0, 15), ipady=6)

        # ── Erro ───────────────────────────────────────────────────────────
        self.error_label = tk.Label(
            main,
            text="",
            font=FONTS["small"],
            bg=COLORS["bg_primary"],
            fg=COLORS["danger"],
            wraplength=420,
        )
        self.error_label.pack(pady=(0, 10))

        # ── Botões ─────────────────────────────────────────────────────────
        btn_frame = StyledFrame(main)
        btn_frame.pack(fill="x", pady=(10, 0))

        StyledButton(
            btn_frame,
            text="Cancelar",
            command=self.destroy,
            style="secondary",
        ).pack(side="left")

        StyledButton(
            btn_frame,
            text="Salvar e Iniciar Extração",
            command=self._save,
            style="primary",
        ).pack(side="right")

        # Focus no primeiro campo
        self.name_entry.focus_set()
        self.name_entry.bind("<Return>", lambda e: self.version_entry.focus_set())
        self.version_entry.bind("<Return>", lambda e: self.type_entry.focus_set())
        self.type_entry.bind("<Return>", lambda e: self._save())

    def _save(self):
        """Valida e salva a nova extração."""
        name = self.name_entry.get_value().strip()
        version = self.version_entry.get_value().strip()
        doc_type = self.type_entry.get_value().strip()

        # Validação
        if not name:
            self.error_label.config(text="O nome da extração é obrigatório.")
            self.name_entry.focus_set()
            return
        if not version:
            self.error_label.config(text="A versão é obrigatória.")
            self.version_entry.focus_set()
            return
        if not doc_type:
            self.error_label.config(text="O tipo é obrigatório.")
            self.type_entry.focus_set()
            return

        # Verifica unicidade
        if self.db.extraction_exists(name, version, doc_type):
            self.error_label.config(
                text=f"Já existe uma extração '{name}' com versão '{version}' e tipo '{doc_type}'."
            )
            return

        try:
            self.extraction_id = self.db.create_extraction(name, version, doc_type)
            self.on_save(self.extraction_id)
            self.destroy()
        except Exception as e:
            self.error_label.config(text=f"Erro ao salvar: {str(e)}")
