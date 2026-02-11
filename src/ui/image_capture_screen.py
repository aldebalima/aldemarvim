"""
Tela de captura de imagem para extração de texto via OCR.
Permite colar print screen do clipboard ou selecionar arquivo.
Após extração: texto original à esquerda, botão traduzir, texto traduzido à direita.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

from src.config import COLORS, FONTS
from src.services.ocr_service import OCRService
from src.services.translation_service import TranslationService
from src.ui.base import StyledButton, StyledFrame, StyledLabel, StyledText


class ImageCaptureScreen(tk.Frame):
    """Tela de captura e processamento de imagem."""

    def __init__(self, master, db_manager, extraction_id: int, on_back: callable):
        super().__init__(master, bg=COLORS["bg_primary"])
        self.db = db_manager
        self.extraction_id = extraction_id
        self.on_back = on_back
        self.ocr = OCRService()
        self.translator = TranslationService()
        self.current_image = None
        self.image_photo = None

        extraction = self.db.get_extraction(extraction_id)
        self.extraction_name = extraction["name"] if extraction else "Sem nome"

        self._build_ui()

    def _build_ui(self):
        """Constrói a interface."""
        # ── Cabeçalho ──────────────────────────────────────────────────────
        header = StyledFrame(self, style="secondary")
        header.pack(fill="x", padx=0, pady=0)

        header_inner = StyledFrame(header, style="secondary")
        header_inner.pack(fill="x", padx=20, pady=12)

        StyledButton(
            header_inner,
            text="← Voltar",
            command=self.on_back,
            style="secondary",
        ).pack(side="left")

        StyledLabel(
            header_inner,
            text=f"📸 Nova Página — {self.extraction_name}",
            style="heading",
        ).pack(side="left", padx=15)
        # Atualiza bg do label
        for child in header_inner.winfo_children():
            if isinstance(child, StyledLabel):
                child.config(bg=COLORS["bg_secondary"])

        # ── Container principal ────────────────────────────────────────────
        container = StyledFrame(self)
        container.pack(expand=True, fill="both", padx=20, pady=15)

        # ── Seção de imagem (topo) ─────────────────────────────────────────
        image_section = StyledFrame(container)
        image_section.pack(fill="x", pady=(0, 10))

        StyledLabel(
            image_section,
            text="1. Selecione ou cole uma imagem",
            style="heading",
        ).pack(anchor="w", pady=(0, 10))

        btn_row = StyledFrame(image_section)
        btn_row.pack(fill="x", pady=(0, 10))

        StyledButton(
            btn_row,
            text="📋 Colar do Clipboard (Ctrl+V)",
            command=self._paste_from_clipboard,
            style="primary",
        ).pack(side="left", padx=(0, 10))

        StyledButton(
            btn_row,
            text="📁 Selecionar Arquivo",
            command=self._select_file,
            style="secondary",
        ).pack(side="left", padx=(0, 10))

        self.extract_btn = StyledButton(
            btn_row,
            text="🔍 Extrair Texto",
            command=self._extract_text,
            style="success",
        )
        self.extract_btn.pack(side="left")
        self.extract_btn.config(state="disabled")

        # Preview da imagem
        self.image_preview_frame = StyledFrame(image_section, style="secondary")
        self.image_preview_frame.pack(fill="x", pady=(0, 5))

        self.image_label = tk.Label(
            self.image_preview_frame,
            text="Nenhuma imagem selecionada",
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"],
            height=8,
        )
        self.image_label.pack(expand=True, fill="both", padx=10, pady=10)

        # ── Seção de texto (baixo) ─────────────────────────────────────────
        text_section = StyledFrame(container)
        text_section.pack(expand=True, fill="both")

        StyledLabel(
            text_section,
            text="2. Texto extraído e tradução",
            style="heading",
        ).pack(anchor="w", pady=(0, 10))

        # Container com colunas
        columns = StyledFrame(text_section)
        columns.pack(expand=True, fill="both")

        # Coluna esquerda - Texto original
        left_col = StyledFrame(columns)
        left_col.pack(side="left", expand=True, fill="both", padx=(0, 3))

        StyledLabel(left_col, text="Texto Original (EN)", style="body_bold").pack(
            anchor="w", pady=(0, 5)
        )
        self.original_text = StyledText(left_col)
        self.original_text.pack(expand=True, fill="both")

        # Coluna central - Botão traduzir
        center_col = StyledFrame(columns)
        center_col.pack(side="left", fill="y", padx=6)

        # Spacer para centralizar o botão
        tk.Frame(center_col, bg=COLORS["bg_primary"], height=60).pack()

        self.translate_btn = StyledButton(
            center_col,
            text="Traduzir\n EN > PT ",
            command=self._translate_text,
            style="primary",
        )
        self.translate_btn.pack(pady=10)

        # Coluna centro-direita - Texto traduzido
        mid_col = StyledFrame(columns)
        mid_col.pack(side="left", expand=True, fill="both", padx=(3, 3))

        StyledLabel(
            mid_col, text="Texto Traduzido (PT) - Editavel", style="body_bold"
        ).pack(anchor="w", pady=(0, 5))
        self.translated_text = StyledText(mid_col)
        self.translated_text.pack(expand=True, fill="both")

        # Coluna direita - Texto mesclado (somente leitura)
        right_col = StyledFrame(columns)
        right_col.pack(side="left", expand=True, fill="both", padx=(3, 0))

        StyledLabel(
            right_col, text="Mesclado (PT / EN)", style="body_bold"
        ).pack(anchor="w", pady=(0, 5))
        self.merged_text = StyledText(right_col)
        self.merged_text.pack(expand=True, fill="both")
        self.merged_text.config(state="disabled")

        # ── Botões de ação (rodapé) ────────────────────────────────────────
        footer = StyledFrame(container)
        footer.pack(fill="x", pady=(15, 0))

        StyledButton(
            footer,
            text="✅ Salvar Página e Adicionar Nova",
            command=self._save_and_new,
            style="success",
        ).pack(side="left", padx=(0, 10))

        StyledButton(
            footer,
            text="💾 Salvar e Finalizar",
            command=self._save_and_finish,
            style="primary",
        ).pack(side="left")

        # Bind Ctrl+V global
        self.bind_all("<Control-v>", lambda e: self._paste_from_clipboard())

    def _paste_from_clipboard(self):
        """Cola imagem do clipboard."""
        try:
            from PIL import ImageGrab

            image = ImageGrab.grabclipboard()
            if image and isinstance(image, Image.Image):
                self.current_image = image
                self._show_preview(image)
                self.extract_btn.config(state="normal")
            else:
                messagebox.showwarning(
                    "Aviso",
                    "Nenhuma imagem encontrada no clipboard.\n"
                    "Use Print Screen para capturar a tela e tente novamente.",
                )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao colar imagem: {str(e)}")

    def _select_file(self):
        """Abre seletor de arquivo para imagem."""
        file_path = filedialog.askopenfilename(
            title="Selecionar Imagem",
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif"),
                ("Todos os arquivos", "*.*"),
            ],
        )
        if file_path:
            try:
                self.current_image = Image.open(file_path)
                self._show_preview(self.current_image)
                self.extract_btn.config(state="normal")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao abrir imagem: {str(e)}")

    def _show_preview(self, image: Image.Image):
        """Mostra preview da imagem selecionada."""
        # Redimensiona para caber no preview
        max_w, max_h = 700, 150
        img_w, img_h = image.size
        ratio = min(max_w / img_w, max_h / img_h, 1.0)
        new_size = (int(img_w * ratio), int(img_h * ratio))
        preview = image.resize(new_size, Image.LANCZOS)

        self.image_photo = ImageTk.PhotoImage(preview)
        self.image_label.config(
            image=self.image_photo,
            text="",
            height=0,
        )

    def _extract_text(self):
        """Extrai texto da imagem usando OCR."""
        if not self.current_image:
            messagebox.showwarning("Aviso", "Selecione uma imagem primeiro.")
            return

        try:
            self.extract_btn.config(text="⏳ Extraindo...", state="disabled")
            self.update_idletasks()

            text = self.ocr.extract_from_image(self.current_image)

            self.original_text.delete("1.0", tk.END)
            self.original_text.insert("1.0", text)

            self.extract_btn.config(text="🔍 Extrair Texto", state="normal")

            if not text.strip():
                messagebox.showinfo(
                    "Aviso",
                    "Nenhum texto foi detectado na imagem.\n"
                    "Tente com uma imagem mais nítida.",
                )

        except Exception as e:
            self.extract_btn.config(text="🔍 Extrair Texto", state="normal")
            messagebox.showerror("Erro OCR", f"Erro na extração: {str(e)}")

    def _translate_text(self):
        """Traduz o texto original para portugues e gera texto mesclado."""
        text = self.original_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Aviso", "Extraia o texto primeiro.")
            return

        try:
            self.translate_btn.config(text="Traduzindo...", state="disabled")
            self.update_idletasks()

            translated = self.translator.translate(text)

            self.translated_text.delete("1.0", tk.END)
            self.translated_text.insert("1.0", translated)

            # Gera texto mesclado PT/EN
            self._update_merged_text(text, translated)

            self.translate_btn.config(text="Traduzir\n EN > PT ", state="normal")

        except Exception as e:
            self.translate_btn.config(text="Traduzir\n EN > PT ", state="normal")
            messagebox.showerror("Erro", f"Erro na traducao: {str(e)}")

    def _update_merged_text(self, original: str = None, translated: str = None):
        """Atualiza a caixa de texto mesclado PT/EN (somente leitura)."""
        if original is None:
            original = self.original_text.get("1.0", tk.END).strip()
        if translated is None:
            translated = self.translated_text.get("1.0", tk.END).strip()

        merged = TranslationService.merge_texts(original, translated)

        self.merged_text.config(state="normal")
        self.merged_text.delete("1.0", tk.END)
        self.merged_text.insert("1.0", merged)
        self.merged_text.config(state="disabled")

    def _get_page_data(self) -> dict | None:
        """Coleta os dados da página atual."""
        original = self.original_text.get("1.0", tk.END).strip()
        translated = self.translated_text.get("1.0", tk.END).strip()

        if not original and not translated:
            messagebox.showwarning(
                "Aviso", "Extraia o texto da imagem antes de salvar."
            )
            return None

        return {
            "original_text": original,
            "translated_text": translated,
        }

    def _save_and_new(self):
        """Salva a página atual e limpa para uma nova."""
        data = self._get_page_data()
        if not data:
            return

        page_num = self.db.get_next_page_number(self.extraction_id)
        self.db.add_page(
            extraction_id=self.extraction_id,
            page_number=page_num,
            original_text=data["original_text"],
            translated_text=data["translated_text"],
        )

        messagebox.showinfo("Sucesso", f"Página {page_num} salva com sucesso!")

        # Limpa tudo para nova página
        self.current_image = None
        self.image_photo = None
        self.image_label.config(
            image="",
            text="Nenhuma imagem selecionada",
            height=8,
        )
        self.original_text.delete("1.0", tk.END)
        self.translated_text.delete("1.0", tk.END)
        self.merged_text.config(state="normal")
        self.merged_text.delete("1.0", tk.END)
        self.merged_text.config(state="disabled")
        self.extract_btn.config(state="disabled")

    def _save_and_finish(self):
        """Salva a página atual e retorna à listagem."""
        data = self._get_page_data()
        if data:
            page_num = self.db.get_next_page_number(self.extraction_id)
            self.db.add_page(
                extraction_id=self.extraction_id,
                page_number=page_num,
                original_text=data["original_text"],
                translated_text=data["translated_text"],
            )

        self.on_back()
