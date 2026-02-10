"""
Diálogo de confirmação de exclusão.
O usuário deve digitar "deletar" para confirmar.
"""

import tkinter as tk

from src.config import COLORS, FONTS
from src.ui.base import StyledButton, StyledEntry, StyledFrame


class DeleteConfirmDialog(tk.Toplevel):
    """Diálogo modal de confirmação de exclusão por escrita."""

    def __init__(self, master, item_name: str, on_confirm: callable):
        super().__init__(master)
        self.on_confirm = on_confirm
        self.result = False

        # ── Configuração ───────────────────────────────────────────────────
        self.title("Confirmar Exclusão")
        self.configure(bg=COLORS["bg_primary"])
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        # Centraliza (altura um pouco maior para garantir que os botões apareçam
        # mesmo em monitores com escala > 100%)
        width, height = 450, 340
        x = master.winfo_rootx() + (master.winfo_width() - width) // 2
        y = master.winfo_rooty() + (master.winfo_height() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        # ── Layout ─────────────────────────────────────────────────────────
        main = StyledFrame(self)
        main.pack(expand=True, fill="both", padx=25, pady=25)

        # Ícone de alerta
        tk.Label(
            main,
            text="⚠️",
            font=("Segoe UI", 36),
            bg=COLORS["bg_primary"],
            fg=COLORS["danger"],
        ).pack(pady=(0, 10))

        # Texto de aviso
        tk.Label(
            main,
            text=f'Deseja excluir "{item_name}"?',
            font=FONTS["heading"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"],
            wraplength=380,
        ).pack(pady=(0, 5))

        tk.Label(
            main,
            text='Digite "deletar" para confirmar:',
            font=FONTS["body"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_secondary"],
        ).pack(pady=(0, 10))

        # Campo de entrada
        self.confirm_entry = StyledEntry(main, width=30)
        self.confirm_entry.pack(pady=(0, 5), ipady=4)
        self.confirm_entry.focus_set()
        self.confirm_entry.bind("<Return>", lambda e: self._try_confirm())

        # Mensagem de erro
        self.error_label = tk.Label(
            main,
            text="",
            font=FONTS["small"],
            bg=COLORS["bg_primary"],
            fg=COLORS["danger"],
        )
        self.error_label.pack(pady=(0, 10))

        # Botões
        btn_frame = StyledFrame(main)
        btn_frame.pack(fill="x")

        StyledButton(
            btn_frame,
            text="Cancelar",
            command=self.destroy,
            style="secondary",
        ).pack(side="left", padx=(0, 10))

        StyledButton(
            btn_frame,
            text="Confirmar Exclusão",
            command=self._try_confirm,
            style="danger",
        ).pack(side="right")

        # Bind ESC para fechar
        self.bind("<Escape>", lambda e: self.destroy())

    def _try_confirm(self):
        """Verifica se o texto digitado é 'deletar'."""
        text = self.confirm_entry.get().strip().lower()
        if text == "deletar":
            self.result = True
            self.on_confirm()
            self.destroy()
        else:
            self.error_label.config(
                text='Texto incorreto. Digite exatamente "deletar".'
            )
            self.confirm_entry.delete(0, tk.END)
            self.confirm_entry.focus_set()
