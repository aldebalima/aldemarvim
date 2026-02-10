"""
Serviço de Tradução - Traduz textos do inglês para o português.
Utiliza deep-translator (Google Translate gratuito).
"""

from deep_translator import GoogleTranslator

from src.config import TRANSLATE_SOURCE, TRANSLATE_TARGET


class TranslationService:
    """Serviço responsável pela tradução de textos."""

    def __init__(
        self,
        source: str = TRANSLATE_SOURCE,
        target: str = TRANSLATE_TARGET,
    ):
        self.source = source
        self.target = target
        self.translator = GoogleTranslator(source=source, target=target)

    def translate(self, text: str) -> str:
        """
        Traduz um texto do idioma de origem para o destino.

        Args:
            text: Texto a ser traduzido.

        Returns:
            Texto traduzido.
        """
        if not text or not text.strip():
            return ""

        # deep-translator tem limite de ~5000 chars por request
        # Dividimos em blocos se necessário
        max_chars = 4500
        if len(text) <= max_chars:
            raw = self.translator.translate(text)
            return self._sanitize_for_pdf(raw)

        # Divide em blocos respeitando quebras de linha
        blocks = self._split_text(text, max_chars)
        translated_blocks = []
        for block in blocks:
            translated = self.translator.translate(block)
            translated_blocks.append(self._sanitize_for_pdf(translated))

        return "\n".join(translated_blocks)

    def _split_text(self, text: str, max_chars: int) -> list[str]:
        """Divide texto em blocos menores respeitando parágrafos."""
        paragraphs = text.split("\n")
        blocks = []
        current_block = ""

        for paragraph in paragraphs:
            if len(current_block) + len(paragraph) + 1 > max_chars:
                if current_block:
                    blocks.append(current_block.strip())
                current_block = paragraph
            else:
                current_block += "\n" + paragraph if current_block else paragraph

        if current_block.strip():
            blocks.append(current_block.strip())

        return blocks

    def _sanitize_for_pdf(self, text: str) -> str:
        """
        Remove caracteres que podem atrapalhar a geração do PDF.

        Removidos: | # * @ { } ' "
        (podemos ajustar essa lista conforme necessidade).
        """
        forbidden = "|#*@{}'\""
        table = str.maketrans("", "", forbidden)
        return text.translate(table)
