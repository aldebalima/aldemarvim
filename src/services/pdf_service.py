"""
Serviço de PDF - Gera PDFs a partir das páginas de uma extração.
Utiliza fpdf2.
"""

import os
import platform
import subprocess
from dataclasses import dataclass

from fpdf import FPDF

from src.config import EXPORTS_DIR

# Helvetica (fonte core do fpdf2) só aceita Latin-1.
_LATIN1 = "latin-1"
_CONTEXT_RADIUS = 20


@dataclass(frozen=True)
class EncodingIssue:
    """Um caractere incompatível encontrado em título ou página."""

    location: str  # ex.: "capa/título" ou "Página 3"
    char: str
    position: int
    context: str

    @property
    def codepoint(self) -> str:
        return f"U+{ord(self.char):04X}"


class PDFTextEncodingError(Exception):
    """Texto contém caracteres incompatíveis com Helvetica/Latin-1."""

    def __init__(self, issues: list[EncodingIssue]):
        self.issues = issues
        super().__init__(self.format_message())

    def format_message(self) -> str:
        lines = [
            "Não foi possível gerar o PDF: caracteres incompatíveis "
            "com a fonte Helvetica.",
            "",
        ]
        for issue in self.issues:
            char_display = issue.char if issue.char.isprintable() else "?"
            lines.append(
                f'{issue.location}: caractere "{char_display}" '
                f"({issue.codepoint}) perto de: \"...{issue.context}...\""
            )
        lines.append("")
        lines.append(
            "Abra Editar, vá até essas páginas e substitua os caracteres especiais."
        )
        return "\n".join(lines)


def _context_snippet(text: str, index: int, radius: int = _CONTEXT_RADIUS) -> str:
    start = max(0, index - radius)
    end = min(len(text), index + radius + 1)
    snippet = text[start:end].replace("\n", " ").replace("\r", " ")
    return snippet


def _find_latin1_issues(text: str, location: str) -> list[EncodingIssue]:
    """Retorna todos os caracteres fora de Latin-1 em um texto."""
    if not text:
        return []

    issues: list[EncodingIssue] = []
    for i, ch in enumerate(text):
        try:
            ch.encode(_LATIN1)
        except UnicodeEncodeError:
            issues.append(
                EncodingIssue(
                    location=location,
                    char=ch,
                    position=i,
                    context=_context_snippet(text, i),
                )
            )
    return issues


def _collect_encoding_issues(title: str, pages: list[dict]) -> list[EncodingIssue]:
    """Valida título e textos das páginas contra Latin-1."""
    issues = _find_latin1_issues(title or "", "Capa/título")

    for page in pages:
        page_num = page.get("page_number", "?")
        text = page.get("translated_text") or page.get("original_text", "")
        issues.extend(_find_latin1_issues(text, f"Página {page_num}"))

    return issues


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

        Raises:
            PDFTextEncodingError: Se título ou páginas tiverem caracteres
                incompatíveis com Helvetica/Latin-1.
        """
        issues = _collect_encoding_issues(title, pages)
        if issues:
            raise PDFTextEncodingError(issues)

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
