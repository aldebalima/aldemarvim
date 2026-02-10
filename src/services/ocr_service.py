"""
Serviço de OCR - Extração de texto a partir de imagens.
Utiliza Tesseract OCR via pytesseract.
Busca o Tesseract embutido (build .exe), instalado no sistema, ou no PATH.
"""

import platform
import os
from PIL import Image, ImageGrab
import pytesseract

from src.config import TESSERACT_PATHS_WIN, TESSERACT_CMD_LINUX, OCR_LANG


class OCRService:
    """Serviço responsável pela extração de texto de imagens."""

    def __init__(self):
        self._configure_tesseract()

    def _configure_tesseract(self) -> None:
        """
        Configura o caminho do Tesseract baseado no SO.
        Ordem de busca no Windows:
          1. Tesseract embutido (pasta tesseract/ ao lado do .exe)
          2. Instalação padrão em Program Files
          3. Instalação em Program Files (x86)
        """
        system = platform.system()
        if system == "Windows":
            for path in TESSERACT_PATHS_WIN:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    # Define TESSDATA_PREFIX para o Tesseract encontrar os idiomas
                    tessdata = os.path.join(os.path.dirname(path), "tessdata")
                    if os.path.isdir(tessdata):
                        os.environ["TESSDATA_PREFIX"] = tessdata
                    return
        elif system == "Linux":
            if os.path.exists(TESSERACT_CMD_LINUX):
                pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD_LINUX

    def extract_from_file(self, file_path: str, lang: str = OCR_LANG) -> str:
        """
        Extrai texto de um arquivo de imagem.

        Args:
            file_path: Caminho do arquivo de imagem.
            lang: Idioma para OCR (padrão: inglês).

        Returns:
            Texto extraído da imagem.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        image = Image.open(file_path)
        text = pytesseract.image_to_string(image, lang=lang)
        return text.strip()

    def extract_from_image(self, image: Image.Image, lang: str = OCR_LANG) -> str:
        """
        Extrai texto de um objeto PIL Image.

        Args:
            image: Objeto PIL Image.
            lang: Idioma para OCR (padrão: inglês).

        Returns:
            Texto extraído da imagem.
        """
        text = pytesseract.image_to_string(image, lang=lang)
        return text.strip()

    def extract_from_clipboard(self, lang: str = OCR_LANG) -> str:
        """
        Extrai texto de uma imagem na área de transferência (clipboard).

        Args:
            lang: Idioma para OCR (padrão: inglês).

        Returns:
            Texto extraído da imagem do clipboard.

        Raises:
            ValueError: Se não houver imagem no clipboard.
        """
        try:
            image = ImageGrab.grabclipboard()
        except Exception:
            raise ValueError("Não foi possível acessar a área de transferência.")

        if image is None:
            raise ValueError(
                "Nenhuma imagem encontrada na área de transferência. "
                "Copie uma imagem (Print Screen) e tente novamente."
            )

        if not isinstance(image, Image.Image):
            raise ValueError(
                "O conteúdo da área de transferência não é uma imagem válida."
            )

        text = pytesseract.image_to_string(image, lang=lang)
        return text.strip()

    @staticmethod
    def is_tesseract_available() -> bool:
        """Verifica se o Tesseract está instalado e acessível."""
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False
