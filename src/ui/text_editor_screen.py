"""
Tela de edição de texto com navegação por páginas.
Permite editar o texto traduzido de cada página,
navegar entre páginas e reordenar.
"""

import tkinter as tk
from tkinter import messagebox

from src.config import COLORS, FONTS
from src.ui.base import StyledButton, StyledFrame, StyledLabel, StyledText


class TextEditorScreen(tk.Frame):
    """Tela de edição de páginas de uma extração."""

    def __init__(
        self,
        master,
        db_manager,
        extraction_id: int,
        on_back: callable,
        on_add_page: callable,
    ):
        super().__init__(master, bg=COLORS["bg_primary"])
        self.db = db_manager
        self.extraction_id = extraction_id
        self.on_back = on_back
        self.on_add_page = on_add_page

        self.pages = []
        self.current_page_index = 0

        extraction = self.db.get_extraction(extraction_id)
        self.extraction_name = extraction["name"] if extraction else "Sem nome"

        self._load_pages()
        self._build_ui()
        self._display_current_page()

    def _load_pages(self):
        """Carrega as páginas da extração."""
        self.pages = self.db.get_pages(self.extraction_id)

    def _build_ui(self):
        """Constrói a interface."""
        # ── Cabeçalho ──────────────────────────────────────────────────────
        header = StyledFrame(self, style="secondary")
        header.pack(fill="x")

        header_inner = StyledFrame(header, style="secondary")
        header_inner.pack(fill="x", padx=20, pady=12)

        StyledButton(
            header_inner,
            text="← Voltar",
            command=self._go_back,
            style="secondary",
        ).pack(side="left")

        StyledLabel(
            header_inner,
            text=f"✏️ Editar — {self.extraction_name}",
            style="heading",
        ).pack(side="left", padx=15)
        for child in header_inner.winfo_children():
            if isinstance(child, StyledLabel):
                child.config(bg=COLORS["bg_secondary"])

        StyledButton(
            header_inner,
            text="➕ Adicionar Página",
            command=self.on_add_page,
            style="success",
        ).pack(side="right")

        # ── Navegação de páginas ───────────────────────────────────────────
        nav_frame = StyledFrame(self)
        nav_frame.pack(fill="x", padx=20, pady=10)

        self.prev_btn = StyledButton(
            nav_frame,
            text="◀ Anterior",
            command=self._prev_page,
            style="secondary",
        )
        self.prev_btn.pack(side="left")

        self.page_info_label = StyledLabel(
            nav_frame, text="Página 0 / 0", style="heading"
        )
        self.page_info_label.pack(side="left", padx=20)

        self.next_btn = StyledButton(
            nav_frame,
            text="Próxima ▶",
            command=self._next_page,
            style="secondary",
        )
        self.next_btn.pack(side="left")

        # Botões de reordenação
        reorder_frame = StyledFrame(nav_frame)
        reorder_frame.pack(side="right")

        StyledButton(
            reorder_frame,
            text="⬆ Mover Acima",
            command=self._move_page_up,
            style="secondary",
        ).pack(side="left", padx=(0, 5))

        StyledButton(
            reorder_frame,
            text="⬇ Mover Abaixo",
            command=self._move_page_down,
            style="secondary",
        ).pack(side="left")

        # ── Área de edição ─────────────────────────────────────────────────
        edit_container = StyledFrame(self)
        edit_container.pack(expand=True, fill="both", padx=20, pady=(0, 10))

        # Texto original (somente leitura)
        left_frame = StyledFrame(edit_container)
        left_frame.pack(side="left", expand=True, fill="both", padx=(0, 10))

        StyledLabel(
            left_frame, text="Texto Original", style="body_bold"
        ).pack(anchor="w", pady=(0, 5))

        self.original_text = StyledText(left_frame)
        self.original_text.pack(expand=True, fill="both")
        self.original_text.config(state="disabled")

        # Texto traduzido (editável)
        right_frame = StyledFrame(edit_container)
        right_frame.pack(side="left", expand=True, fill="both")

        StyledLabel(
            right_frame, text="Texto Traduzido (Editável)", style="body_bold"
        ).pack(anchor="w", pady=(0, 5))

        self.translated_text = StyledText(right_frame)
        self.translated_text.pack(expand=True, fill="both")

        # ── Rodapé ─────────────────────────────────────────────────────────
        footer = StyledFrame(self)
        footer.pack(fill="x", padx=20, pady=(0, 15))

        StyledButton(
            footer,
            text="💾 Salvar Alterações",
            command=self._save_current_page,
            style="success",
        ).pack(side="left", padx=(0, 10))

        StyledButton(
            footer,
            text="💾 Salvar Tudo",
            command=self._save_all,
            style="primary",
        ).pack(side="left")

    def _display_current_page(self):
        """Exibe a página atual nos campos de texto."""
        if not self.pages:
            self.page_info_label.config(text="Nenhuma página")
            self.original_text.config(state="normal")
            self.original_text.delete("1.0", tk.END)
            self.original_text.config(state="disabled")
            self.translated_text.delete("1.0", tk.END)
            self._update_nav_buttons()
            return

        page = self.pages[self.current_page_index]
        total = len(self.pages)

        self.page_info_label.config(
            text=f"Página {self.current_page_index + 1} / {total}"
        )

        # Original (somente leitura)
        self.original_text.config(state="normal")
        self.original_text.delete("1.0", tk.END)
        self.original_text.insert("1.0", page.get("original_text", ""))
        self.original_text.config(state="disabled")

        # Traduzido (editável)
        self.translated_text.delete("1.0", tk.END)
        self.translated_text.insert("1.0", page.get("translated_text", ""))

        self._update_nav_buttons()

    def _update_nav_buttons(self):
        """Atualiza estado dos botões de navegação."""
        self.prev_btn.config(
            state="normal" if self.current_page_index > 0 else "disabled"
        )
        self.next_btn.config(
            state="normal"
            if self.current_page_index < len(self.pages) - 1
            else "disabled"
        )

    def _save_current_page(self):
        """Salva as alterações da página atual."""
        if not self.pages:
            return

        page = self.pages[self.current_page_index]
        translated = self.translated_text.get("1.0", tk.END).strip()
        self.db.update_page(page["id"], translated_text=translated)
        self.pages[self.current_page_index]["translated_text"] = translated
        messagebox.showinfo("Sucesso", "Página salva com sucesso!")

    def _save_all(self):
        """Salva todas as páginas."""
        # Salva a página atualmente exibida
        self._save_current_visible()
        messagebox.showinfo("Sucesso", "Todas as alterações foram salvas!")

    def _save_current_visible(self):
        """Salva silenciosamente a página visível."""
        if not self.pages:
            return
        page = self.pages[self.current_page_index]
        translated = self.translated_text.get("1.0", tk.END).strip()
        self.db.update_page(page["id"], translated_text=translated)
        self.pages[self.current_page_index]["translated_text"] = translated

    def _prev_page(self):
        """Navega para a página anterior."""
        if self.current_page_index > 0:
            self._save_current_visible()
            self.current_page_index -= 1
            self._display_current_page()

    def _next_page(self):
        """Navega para a próxima página."""
        if self.current_page_index < len(self.pages) - 1:
            self._save_current_visible()
            self.current_page_index += 1
            self._display_current_page()

    def _move_page_up(self):
        """Move a página atual uma posição acima."""
        if self.current_page_index <= 0 or not self.pages:
            return

        self._save_current_visible()
        idx = self.current_page_index

        # Troca posições
        self.pages[idx], self.pages[idx - 1] = self.pages[idx - 1], self.pages[idx]

        # Atualiza números no banco
        page_order = [p["id"] for p in self.pages]
        self.db.reorder_pages(self.extraction_id, page_order)

        self.current_page_index -= 1
        self._load_pages()
        self._display_current_page()

    def _move_page_down(self):
        """Move a página atual uma posição abaixo."""
        if self.current_page_index >= len(self.pages) - 1 or not self.pages:
            return

        self._save_current_visible()
        idx = self.current_page_index

        # Troca posições
        self.pages[idx], self.pages[idx + 1] = self.pages[idx + 1], self.pages[idx]

        # Atualiza números no banco
        page_order = [p["id"] for p in self.pages]
        self.db.reorder_pages(self.extraction_id, page_order)

        self.current_page_index += 1
        self._load_pages()
        self._display_current_page()

    def _go_back(self):
        """Salva e volta à listagem."""
        if self.pages:
            self._save_current_visible()
        self.on_back()

    def refresh(self):
        """Recarrega as páginas (chamado após adicionar nova página)."""
        self._save_current_visible() if self.pages else None
        self._load_pages()
        if self.pages:
            self.current_page_index = len(self.pages) - 1
        self._display_current_page()
