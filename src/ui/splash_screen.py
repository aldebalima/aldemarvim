"""
Tela de Splash / Loading - Exibida ao iniciar o sistema.
Mostra logo rotacionando, texto ALDEMARVIM e barra de loading por 3 segundos.
"""

import tkinter as tk
from PIL import ImageTk

from src.config import COLORS, FONTS, SPLASH_DURATION_MS
from src.utils.logo_generator import LogoGenerator


class SplashScreen(tk.Toplevel):
    """Tela de splash com logo rotacionando e barra de loading."""

    def __init__(self, master, on_complete: callable):
        super().__init__(master)
        self.on_complete = on_complete

        # ── Configuração da janela ─────────────────────────────────────────
        self.overrideredirect(True)  # Remove borda da janela
        self.configure(bg=COLORS["bg_primary"])

        # Centraliza na tela
        width, height = 500, 450
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Mantém no topo
        self.attributes("-topmost", True)
        self.focus_force()

        # ── Gera a logo ───────────────────────────────────────────────────
        self.logo_size = 180
        self.logo_generator = LogoGenerator()
        self.original_logo = self.logo_generator.create_logo(self.logo_size)
        self.rotation_angle = 0
        self.logo_photo = None

        # ── Layout ─────────────────────────────────────────────────────────
        self._build_ui()

        # ── Animações ──────────────────────────────────────────────────────
        self.progress_value = 0
        self.elapsed_ms = 0
        self._animate_logo()
        self._animate_loading()

    def _build_ui(self):
        """Constrói a interface da splash screen."""
        # Container principal
        main_frame = tk.Frame(self, bg=COLORS["bg_primary"])
        main_frame.pack(expand=True, fill="both", padx=30, pady=30)

        # Espaço superior
        tk.Frame(main_frame, bg=COLORS["bg_primary"], height=20).pack()

        # ── Logo ───────────────────────────────────────────────────────────
        self.logo_label = tk.Label(
            main_frame,
            bg=COLORS["bg_primary"],
            borderwidth=0,
            highlightthickness=0,
        )
        self.logo_label.pack(pady=(10, 20))
        self._update_logo_image()

        # ── Texto ALDEMARVIM ───────────────────────────────────────────────
        title_label = tk.Label(
            main_frame,
            text="ALDEMARVIM",
            font=FONTS["splash_title"],
            bg=COLORS["bg_primary"],
            fg=COLORS["accent"],
        )
        title_label.pack(pady=(5, 5))

        # Subtítulo
        subtitle_label = tk.Label(
            main_frame,
            text="Extrator de Texto Inteligente",
            font=FONTS["subtitle"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_secondary"],
        )
        subtitle_label.pack(pady=(0, 30))

        # ── Barra de Loading ──────────────────────────────────────────────
        loading_frame = tk.Frame(main_frame, bg=COLORS["bg_primary"])
        loading_frame.pack(fill="x", padx=40)

        # Fundo da barra
        self.loading_canvas = tk.Canvas(
            loading_frame,
            height=8,
            bg=COLORS["loading_bg"],
            highlightthickness=0,
            borderwidth=0,
        )
        self.loading_canvas.pack(fill="x")

        # Barra de progresso
        self.progress_bar = self.loading_canvas.create_rectangle(
            0, 0, 0, 8, fill=COLORS["loading_bar"], outline=""
        )

        # Texto de loading
        self.loading_text = tk.Label(
            main_frame,
            text="Carregando...",
            font=FONTS["small"],
            bg=COLORS["bg_primary"],
            fg=COLORS["text_secondary"],
        )
        self.loading_text.pack(pady=(10, 0))

    def _update_logo_image(self):
        """Atualiza a imagem da logo com a rotação atual."""
        rotated = LogoGenerator.rotate_image(self.original_logo, self.rotation_angle)
        self.logo_photo = ImageTk.PhotoImage(rotated)
        self.logo_label.config(image=self.logo_photo)

    def _animate_logo(self):
        """Anima a rotação da logo."""
        self.rotation_angle = (self.rotation_angle - 3) % 360  # Rotação suave
        self._update_logo_image()

        if self.elapsed_ms < SPLASH_DURATION_MS:
            self.after(30, self._animate_logo)  # ~33 FPS

    def _animate_loading(self):
        """Anima a barra de loading progressivamente por 3 segundos."""
        step_ms = 30
        self.elapsed_ms += step_ms
        total_steps = SPLASH_DURATION_MS / step_ms
        self.progress_value = min(self.elapsed_ms / SPLASH_DURATION_MS, 1.0)

        # Atualiza a barra
        canvas_width = self.loading_canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = 380  # Largura padrão se não renderizou ainda
        bar_width = int(canvas_width * self.progress_value)
        self.loading_canvas.coords(self.progress_bar, 0, 0, bar_width, 8)

        # Atualiza texto
        percent = int(self.progress_value * 100)
        messages = [
            (30, "Inicializando módulos..."),
            (60, "Carregando banco de dados..."),
            (85, "Preparando interface..."),
            (100, "Pronto!"),
        ]
        for threshold, msg in messages:
            if percent <= threshold:
                self.loading_text.config(text=f"{msg} {percent}%")
                break

        if self.elapsed_ms < SPLASH_DURATION_MS:
            self.after(step_ms, self._animate_loading)
        else:
            # Loading completo - fecha splash e abre tela principal
            self.after(300, self._finish)

    def _finish(self):
        """Finaliza a splash e chama o callback."""
        self.destroy()
        self.on_complete()
