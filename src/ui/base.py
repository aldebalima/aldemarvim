"""
Componentes base e widgets reutilizáveis para a interface.
"""

import tkinter as tk
from tkinter import ttk

from src.config import COLORS, FONTS


class StyledButton(tk.Button):
    """Botão estilizado com hover effect."""

    def __init__(
        self,
        master,
        text: str = "",
        command=None,
        style: str = "primary",
        width: int = None,
        **kwargs,
    ):
        bg_map = {
            "primary": COLORS["accent"],
            "success": COLORS["success"],
            "danger": COLORS["danger"],
            "secondary": COLORS["bg_card"],
        }
        hover_map = {
            "primary": COLORS["accent_hover"],
            "success": "#00d9a3",
            "danger": COLORS["danger_hover"],
            "secondary": COLORS["border"],
        }

        self.bg_color = bg_map.get(style, COLORS["accent"])
        self.hover_color = hover_map.get(style, COLORS["accent_hover"])

        super().__init__(
            master,
            text=text,
            command=command,
            bg=self.bg_color,
            fg=COLORS["button_text"],
            font=FONTS["body_bold"],
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=8,
            activebackground=self.hover_color,
            activeforeground=COLORS["button_text"],
            borderwidth=0,
            highlightthickness=0,
            **kwargs,
        )

        if width:
            self.config(width=width)

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _event):
        self.config(bg=self.hover_color)

    def _on_leave(self, _event):
        self.config(bg=self.bg_color)


class StyledEntry(tk.Entry):
    """Campo de entrada estilizado."""

    def __init__(self, master, placeholder: str = "", **kwargs):
        super().__init__(
            master,
            bg=COLORS["input_bg"],
            fg=COLORS["text_primary"],
            font=FONTS["body"],
            relief="flat",
            insertbackground=COLORS["text_primary"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            **kwargs,
        )

        self.placeholder = placeholder
        self.placeholder_color = COLORS["text_secondary"]
        self.default_fg = COLORS["text_primary"]

        if placeholder:
            self._add_placeholder()
            self.bind("<FocusIn>", self._on_focus_in)
            self.bind("<FocusOut>", self._on_focus_out)

    def _add_placeholder(self):
        self.insert(0, self.placeholder)
        self.config(fg=self.placeholder_color)

    def _on_focus_in(self, _event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.default_fg)

    def _on_focus_out(self, _event):
        if not self.get():
            self._add_placeholder()

    def get_value(self) -> str:
        """Retorna o valor real (ignora placeholder)."""
        value = self.get()
        return "" if value == self.placeholder else value


class StyledText(tk.Text):
    """Área de texto estilizada."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            bg=COLORS["input_bg"],
            fg=COLORS["text_primary"],
            font=FONTS["mono"],
            relief="flat",
            insertbackground=COLORS["text_primary"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            wrap="word",
            padx=10,
            pady=10,
            selectbackground=COLORS["accent"],
            selectforeground=COLORS["button_text"],
            undo=True,
            **kwargs,
        )


class StyledLabel(tk.Label):
    """Label estilizado."""

    def __init__(self, master, text: str = "", style: str = "body", **kwargs):
        font = FONTS.get(style, FONTS["body"])
        super().__init__(
            master,
            text=text,
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"],
            font=font,
            **kwargs,
        )


class StyledFrame(tk.Frame):
    """Frame estilizado."""

    def __init__(self, master, style: str = "primary", **kwargs):
        bg_map = {
            "primary": COLORS["bg_primary"],
            "secondary": COLORS["bg_secondary"],
            "card": COLORS["bg_card"],
        }
        bg = bg_map.get(style, COLORS["bg_primary"])
        super().__init__(master, bg=bg, **kwargs)


class ScrollableFrame(StyledFrame):
    """Frame com scroll vertical."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.canvas = tk.Canvas(
            self, bg=COLORS["bg_primary"], highlightthickness=0, borderwidth=0
        )
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.scrollable = StyledFrame(self.canvas)

        self.scrollable.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas_frame = self.canvas.create_window(
            (0, 0), window=self.scrollable, anchor="nw"
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Ajusta largura do frame interno
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_frame, width=e.width),
        )

        # Scroll com mousewheel
        self.scrollable.bind("<Enter>", self._bind_mousewheel)
        self.scrollable.bind("<Leave>", self._unbind_mousewheel)

    def _bind_mousewheel(self, _event):
        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
        )

    def _unbind_mousewheel(self, _event):
        self.canvas.unbind_all("<MouseWheel>")
