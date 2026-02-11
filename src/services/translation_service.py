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

    @staticmethod
    def merge_texts(original: str, translated: str) -> str:
        """
        Mescla texto original (EN) e traduzido (PT) linha a linha.
        Para cada frase/linha traduzida, exibe a versão PT seguida da EN.

        Exemplo:
            Meu nome é Aldemarvim
            My name is Aldemarvim

            Eu gosto de programar
            I like to program

        Args:
            original: Texto original em inglês.
            translated: Texto traduzido em português.

        Returns:
            Texto mesclado PT/EN.
        """
        if not original and not translated:
            return ""

        original_lines = [l.strip() for l in original.strip().splitlines()]
        translated_lines = [l.strip() for l in translated.strip().splitlines()]

        # Remove linhas vazias consecutivas para alinhamento melhor
        original_lines = [l for l in original_lines if l]
        translated_lines = [l for l in translated_lines if l]

        max_len = max(len(original_lines), len(translated_lines))
        merged = []

        for i in range(max_len):
            pt_line = translated_lines[i] if i < len(translated_lines) else ""
            en_line = original_lines[i] if i < len(original_lines) else ""

            if pt_line:
                merged.append(pt_line)
            if en_line:
                merged.append(en_line)
            merged.append("")  # Linha em branco separadora

        return "\n".join(merged).strip()

    def _sanitize_for_pdf(self, text: str) -> str:
        """
        Remove caracteres que podem atrapalhar a geração do PDF.

        Removidos: | # * @ { } ' "
        (podemos ajustar essa lista conforme necessidade).
        """
        forbidden = "|#*@{}'\""
        table = str.maketrans("", "", forbidden)
        return text.translate(table)
