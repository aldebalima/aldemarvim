"""
Serviço de PDF - Gera PDFs a partir das páginas de uma extração.
Utiliza fpdf2.
"""

import os
import platform
import subprocess

from fpdf import FPDF

from src.config import EXPORTS_DIR


class PDFService:
    """Serviço responsável pela geração e visualização de PDFs."""

    def __init__(self):
        os.makedirs(EXPORTS_DIR, exist_ok=True)

    def generate_pdf(
        self,
        title: str,
        pages: list[dict],
        output_filename: str | None = None,
    ) -> str:
        """
        Gera um PDF a partir das páginas de uma extração.

        Args:
            title: Título do documento.
            pages: Lista de dicts com 'page_number' e 'translated_text'
                   (ou 'original_text' se não traduzido).
            output_filename: Nome do arquivo de saída (sem extensão).

        Returns:
            Caminho completo do PDF gerado.
        """
        if output_filename is None:
            safe_title = "".join(
                c if c.isalnum() or c in (" ", "-", "_") else "_" for c in title
            )
            output_filename = safe_title.strip()

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=20)

        # ── Capa ───────────────────────────────────────────────────────────
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 28)
        pdf.ln(80)
        pdf.cell(0, 20, title, align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 12)
        pdf.ln(10)
        pdf.cell(
            0,
            10,
            f"Total de páginas: {len(pages)}",
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.ln(20)
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(
            0,
            10,
            "Gerado por Aldemarvin Extractor",
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )

        # ── Páginas ────────────────────────────────────────────────────────
        for page in pages:
            pdf.add_page()
            page_num = page.get("page_number", "?")

            # Cabeçalho da página
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(
                0,
                8,
                f"Página {page_num}",
                align="R",
                new_x="LMARGIN",
                new_y="NEXT",
            )
            pdf.ln(5)

            # Texto (prioriza traduzido, senão usa original)
            text = page.get("translated_text") or page.get("original_text", "")
            pdf.set_font("Helvetica", "", 11)
            # Usa multi_cell para texto longo com quebra automática
            pdf.multi_cell(0, 6, text)

        # ── Salva ──────────────────────────────────────────────────────────
        output_path = os.path.join(EXPORTS_DIR, f"{output_filename}.pdf")
        pdf.output(output_path)
        return output_path

    @staticmethod
    def open_pdf(file_path: str) -> None:
        """Abre o PDF no visualizador padrão do sistema."""
        system = platform.system()
        if system == "Windows":
            os.startfile(file_path)
        elif system == "Linux":
            subprocess.Popen(["xdg-open", file_path])
        elif system == "Darwin":
            subprocess.Popen(["open", file_path])
