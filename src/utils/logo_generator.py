"""
Gerador de logo para o splash screen.
Cria uma logo programática usando PIL para uso no Tkinter.
"""

import math
from PIL import Image, ImageDraw, ImageFont


class LogoGenerator:
    """Gera a logo do Aldemarvin programaticamente."""

    @staticmethod
    def create_logo(size: int = 200) -> Image.Image:
        """
        Cria uma logo circular estilizada.

        Args:
            size: Tamanho da imagem (largura e altura).

        Returns:
            Objeto PIL Image com a logo.
        """
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        center = size // 2
        radius = size // 2 - 10

        # Círculo externo com gradiente (simulado com anéis)
        for i in range(8):
            r = radius - i * 2
            alpha = 255 - i * 20
            color = (233, 69, 96, alpha)  # accent color
            draw.ellipse(
                [center - r, center - r, center + r, center + r],
                outline=color,
                width=3,
            )

        # Círculo interno preenchido
        inner_r = radius - 25
        draw.ellipse(
            [
                center - inner_r,
                center - inner_r,
                center + inner_r,
                center + inner_r,
            ],
            fill=(26, 26, 46, 230),  # bg_primary
            outline=(233, 69, 96, 255),
            width=3,
        )

        # Letra "A" estilizada no centro
        try:
            font = ImageFont.truetype("arial.ttf", size // 3)
        except (OSError, IOError):
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size // 3)
            except (OSError, IOError):
                font = ImageFont.load_default()

        text = "A"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = center - text_w // 2
        text_y = center - text_h // 2 - 5

        draw.text((text_x, text_y), text, fill=(233, 69, 96, 255), font=font)

        # Pequenos detalhes decorativos (pontos ao redor)
        num_dots = 12
        dot_radius = 4
        orbit_radius = radius - 5
        for i in range(num_dots):
            angle = (2 * math.pi * i) / num_dots
            x = center + int(orbit_radius * math.cos(angle))
            y = center + int(orbit_radius * math.sin(angle))
            alpha = 150 + int(105 * abs(math.sin(angle)))
            draw.ellipse(
                [x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius],
                fill=(233, 69, 96, alpha),
            )

        return img

    @staticmethod
    def rotate_image(image: Image.Image, angle: float) -> Image.Image:
        """Rotaciona a imagem mantendo a transparência."""
        return image.rotate(angle, resample=Image.BICUBIC, expand=False)
