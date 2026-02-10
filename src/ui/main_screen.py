"""
Tela principal - Lista de Extrações Disponíveis.
Exibe todas as extrações com ações: Editar, Deletar, Visualizar PDF, Continuar.
Botão lateral direito para Nova Extração.
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from src.config import COLORS, FONTS
from src.services.pdf_service import PDFService
from src.ui.base import (
    StyledButton,
    StyledFrame,
    StyledLabel,
    ScrollableFrame,
)


class MainScreen(tk.Frame):
    """Tela principal com listagem de extrações."""

    def __init__(
        self,
        master,
        db_manager,
        on_new_extraction: callable,
        on_edit: callable,
        on_continue: callable,
    ):
        super().__init__(master, bg=COLORS["bg_primary"])
        self.db = db_manager
        self.on_new_extraction = on_new_extraction
        self.on_edit = on_edit
        self.on_continue = on_continue
        self.pdf_service = PDFService()

        self._build_ui()
        self.refresh_list()

    def _build_ui(self):
        """Constrói a interface da listagem."""
        # ── Cabeçalho ──────────────────────────────────────────────────────
        header = StyledFrame(self, style="secondary")
        header.pack(fill="x")

        header_inner = StyledFrame(header, style="secondary")
        header_inner.pack(fill="x", padx=25, pady=15)

        # Título
        title_frame = StyledFrame(header_inner, style="secondary")
        title_frame.pack(side="left")

        tk.Label(
            title_frame,
            text="📚",
            font=("Segoe UI", 24),
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
        ).pack(side="left", padx=(0, 10))

        tk.Label(
            title_frame,
            text="Extrações Disponíveis",
            font=FONTS["title"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"],
        ).pack(side="left")

        # Botão Nova Extração (direita)
        StyledButton(
            header_inner,
            text="➕ Nova Extração",
            command=self.on_new_extraction,
            style="primary",
        ).pack(side="right")

        # ── Contador ───────────────────────────────────────────────────────
        info_bar = StyledFrame(self)
        info_bar.pack(fill="x", padx=25, pady=(15, 5))

        self.count_label = StyledLabel(
            info_bar, text="0 extrações encontradas", style="small"
        )
        self.count_label.pack(side="left")

        # Botão atualizar
        StyledButton(
            info_bar,
            text="🔄 Atualizar",
            command=self.refresh_list,
            style="secondary",
        ).pack(side="right")

        # ── Lista de extrações (scrollable) ────────────────────────────────
        self.list_container = ScrollableFrame(self)
        self.list_container.pack(expand=True, fill="both", padx=25, pady=(5, 20))

    def refresh_list(self):
        """Recarrega a lista de extrações do banco."""
        # Limpa a lista atual
        for widget in self.list_container.scrollable.winfo_children():
            widget.destroy()

        extractions = self.db.get_all_extractions()
        self.count_label.config(text=f"{len(extractions)} extração(ões) encontrada(s)")

        if not extractions:
            self._show_empty_state()
            return

        for extraction in extractions:
            self._create_card(extraction)

    def _show_empty_state(self):
        """Mostra mensagem quando não há extrações."""
        empty_frame = StyledFrame(self.list_container.scrollable)
        empty_frame.pack(expand=True, fill="both", pady=80)

        tk.Label(
            empty_frame,
            text="📭",
            font=("Segoe UI", 48),
            bg=COLORS["bg_primary"],
        ).pack(pady=(0, 15))

        tk.Label(
            empty_frame,
            text="Nenhuma extração encontrada",
            font=FONTS["heading"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_secondary"],
        ).pack(pady=(0, 10))

        tk.Label(
            empty_frame,
            text='Clique em "Nova Extração" para começar.',
            font=FONTS["body"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_secondary"],
        ).pack()

    def _create_card(self, extraction: dict):
        """Cria um card para uma extração na lista."""
        card = tk.Frame(
            self.list_container.scrollable,
            bg=COLORS["bg_card"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=20,
            pady=15,
        )
        card.pack(fill="x", pady=(0, 8))

        # ── Info (lado esquerdo) ───────────────────────────────────────────
        info_frame = tk.Frame(card, bg=COLORS["bg_card"])
        info_frame.pack(side="left", fill="both", expand=True)

        # Título
        name = extraction.get("name", "Sem nome")
        version = extraction.get("version", "")
        doc_type = extraction.get("doc_type", "")

        title_text = f"{name}"
        if version:
            title_text += f"  •  v{version}"
        if doc_type:
            title_text += f"  •  {doc_type}"

        tk.Label(
            info_frame,
            text=title_text,
            font=FONTS["heading"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_primary"],
            anchor="w",
        ).pack(anchor="w")

        # Detalhes
        page_count = extraction.get("page_count", 0)
        created = extraction.get("created_at", "")
        try:
            created_dt = datetime.fromisoformat(created)
            created_str = created_dt.strftime("%d/%m/%Y %H:%M")
        except (ValueError, TypeError):
            created_str = created

        detail_text = f"📄 {page_count} página(s)  •  📅 Criado em {created_str}"
        tk.Label(
            info_frame,
            text=detail_text,
            font=FONTS["small"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_secondary"],
            anchor="w",
        ).pack(anchor="w", pady=(3, 0))

        # ── Botões (lado direito) ──────────────────────────────────────────
        btn_frame = tk.Frame(card, bg=COLORS["bg_card"])
        btn_frame.pack(side="right")

        doc_id = extraction.get("id", extraction.doc_id)

        # Visualizar PDF
        StyledButton(
            btn_frame,
            text="📖 Visualizar",
            command=lambda eid=doc_id: self._view_pdf(eid),
            style="primary",
        ).pack(side="left", padx=(0, 5))

        # Continuar (adicionar páginas)
        StyledButton(
            btn_frame,
            text="📸 Continuar",
            command=lambda eid=doc_id: self.on_continue(eid),
            style="success",
        ).pack(side="left", padx=(0, 5))

        # Editar
        StyledButton(
            btn_frame,
            text="✏️ Editar",
            command=lambda eid=doc_id: self.on_edit(eid),
            style="secondary",
        ).pack(side="left", padx=(0, 5))

        # Deletar
        StyledButton(
            btn_frame,
            text="🗑️ Deletar",
            command=lambda eid=doc_id, n=name: self._delete(eid, n),
            style="danger",
        ).pack(side="left")

    def _view_pdf(self, extraction_id: int):
        """Gera e abre o PDF da extração."""
        extraction = self.db.get_extraction(extraction_id)
        if not extraction:
            messagebox.showerror("Erro", "Extração não encontrada.")
            return

        pages = self.db.get_pages(extraction_id)
        if not pages:
            messagebox.showwarning(
                "Aviso", "Esta extração não possui páginas para visualizar."
            )
            return

        try:
            title = f"{extraction['name']} - v{extraction.get('version', '')}"
            filename = f"{extraction['name']}_{extraction.get('version', '')}_{extraction.get('doc_type', '')}"
            pdf_path = self.pdf_service.generate_pdf(title, pages, filename)
            self.pdf_service.open_pdf(pdf_path)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {str(e)}")

    def _delete(self, extraction_id: int, name: str):
        """Abre diálogo de confirmação para deletar."""
        from src.ui.delete_dialog import DeleteConfirmDialog

        def confirm():
            self.db.delete_extraction(extraction_id)
            self.refresh_list()
            messagebox.showinfo("Sucesso", f'Extração "{name}" removida com sucesso.')

        DeleteConfirmDialog(self.winfo_toplevel(), name, confirm)
