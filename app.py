 # app.py
 


import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
from PIL import Image, ImageTk
import math

from image_processor import ImageProcessor
from game_state import GameState


class SpotTheDifferenceApp(tk.Tk):
    # Main applications window for the Spot the Differences game.
    # Demonstrate inheritance,  class interaction and encapsulation.

    CANVAS_W = 700
    CANVAS_H = 600
    BG_COLOR = "#1e1e2e"
    ACCENT = "#cba6f7"
    TEXT_FG = "#cdd6f4"
    FOUND_COL = (255, 80, 80)     # red for correct found
    REVEAL_COL = (80, 80, 255)    # blue for revealed unfound

    def __init__(self):
        super().__init__()

        self.title("HIT137 — Spot the Difference")
        self.configure(bg=self.BG_COLOR)
        self.resizable(True, True)

        # Core components
        self.processor = ImageProcessor()
        self.state = GameState()

        # Display state
        self._orig_display: np.ndarray | None = None
        self._mod_display: np.ndarray | None = None
        self._tk_orig: ImageTk.PhotoImage | None = None
        self._tk_mod: ImageTk.PhotoImage | None = None
        self._game_active: bool = False

        self._build_ui()

    # UI Construction

    def _build_ui(self):
        # Builds all Tkinter widgets.

        # Top control bar
        ctrl = tk.Frame(self, bg=self.BG_COLOR)
        ctrl.pack(fill=tk.X, padx=12, pady=(12, 4))

        btn_style = dict(
            bg=self.ACCENT,
            fg="#1e1e2e",
            font=("Helvetica", 11, "bold"),
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2"
        )

        self.load_btn = tk.Button(
            ctrl,
            text="📂  Load Image",
            command=self._load_image,
            **btn_style
        )
        self.load_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.reveal_btn = tk.Button(
            ctrl,
            text="👁  Reveal All",
            command=self._reveal_all,
            state=tk.DISABLED,
            bg="#45475a",
            fg=self.TEXT_FG,
            font=("Helvetica", 11, "bold"),
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2"
        )
        self.reveal_btn.pack(side=tk.LEFT)

        # Score bar
        score_frame = tk.Frame(self, bg=self.BG_COLOR)
        score_frame.pack(fill=tk.X, padx=12, pady=(0, 4))

        lbl_style = dict(
            bg=self.BG_COLOR,
            fg=self.TEXT_FG,
            font=("Helvetica", 11)
        )

        self.remaining_lbl = tk.Label(
            score_frame,
            text="Remaining: —",
            **lbl_style
        )
        self.remaining_lbl.pack(side=tk.LEFT, padx=(0, 20))

        self.mistakes_lbl = tk.Label(
            score_frame,
            text="Mistakes: 0 / 3",
            **lbl_style
        )
        self.mistakes_lbl.pack(side=tk.LEFT, padx=(0, 20))

        self.total_lbl = tk.Label(
            score_frame,
            text="Total Found: 0",
            **lbl_style
        )
        self.total_lbl.pack(side=tk.LEFT)

        self.status_lbl = tk.Label(
            score_frame,
            text="",
            font=("Helvetica", 11, "bold"),
            bg=self.BG_COLOR,
            fg="#f38ba8"
        )
        self.status_lbl.pack(side=tk.RIGHT)

        # Image canvases
        img_frame = tk.Frame(self, bg=self.BG_COLOR)
        img_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        for col, title in enumerate(["Original", "Modified (click here)"]):
            tk.Label(
                img_frame,
                text=title,
                bg=self.BG_COLOR,
                fg=self.ACCENT,
                font=("Helvetica", 12, "bold")
            ).grid(row=0, column=col, pady=(0, 4))

        self.orig_canvas = tk.Canvas(
            img_frame,
            bg="#313244",
            relief=tk.FLAT,
            highlightthickness=0,
            width=self.CANVAS_W,
            height=self.CANVAS_H
        )
        self.orig_canvas.grid(row=1, column=0, padx=(0, 8))

        self.mod_canvas = tk.Canvas(
            img_frame,
            bg="#313244",
            relief=tk.FLAT,
            highlightthickness=0,
            width=self.CANVAS_W,
            height=self.CANVAS_H
        )
        self.mod_canvas.grid(row=1, column=1)

        self.mod_canvas.bind("<Button-1>", self._on_click)

        img_frame.columnconfigure(0, weight=1)
        img_frame.columnconfigure(1, weight=1)

    # Event Handlers

    def _load_image(self):
        # Open file dialog, load image, and start a new round.

        path = filedialog.askopenfilename(
            title="Choose an image",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp")]
        )

        if not path:
            return

        if not self.processor.load_image(
            path,
            max_dim=max(self.CANVAS_W, self.CANVAS_H)
        ):
            messagebox.showerror(
                "Error",
                "Could not load the selected image."
            )
            return

        self.state.new_round(self.processor.alterations)

        self._orig_display = self.processor.get_original_rgb()
        self._mod_display = self.processor.get_modified_rgb()

        self._game_active = True

        self._refresh_canvases()
        self._refresh_labels()

        self.reveal_btn.configure(
            state=tk.NORMAL,
            bg="#89b4fa",
            fg="#1e1e2e"
        )

        self.status_lbl.configure(text="")

    def _on_click(self, event):
        # Handle click on modified image canvas.

        if not self._game_active or self.state.locked:
            return

        img_x, img_y = self._canvas_to_image(
            event.x,
            event.y,
            self.mod_canvas
        )

        if img_x is None:
            return

        idx, already = self.state.check_click(img_x, img_y)

        if already:
            return

        if idx >= 0:
            # Correct click
            alt = self.processor.alterations[idx]

            self._orig_display, self._mod_display = (
                self.processor.draw_circle_on_images(
                    self._orig_display,
                    self._mod_display,
                    alt,
                    self.FOUND_COL
                )
            )

            self._refresh_canvases()
            self._refresh_labels()

            if self.state.all_found():
                self._game_active = False

                self.status_lbl.configure(
                    text="🎉 All found!",
                    fg="#a6e3a1"
                )

                messagebox.showinfo(
                    "Congratulations!",
                    f"You found all 5 differences!\n"
                    f"Total found across all images: "
                    f"{self.state.total_found}\n\n"
                    "Load a new image to keep playing."
                )

        else:
            # Wrong click
            self._refresh_labels()

            if self.state.locked:
                self._game_active = False

                self.status_lbl.configure(
                    text="❌ Too many mistakes!",
                    fg="#f38ba8"
                )

                messagebox.showwarning(
                    "Game Over",
                    f"You made 3 mistakes!\n"
                    f"Differences found: "
                    f"{ImageProcessor.NUM_DIFFERENCES - self.state.remaining()} / 5\n\n"
                    "Press 'Reveal All' or load a new image."
                )

    def _reveal_all(self):
        # Reveal all unfound difference with blue circles.

        if not self._orig_display is not None:
            return

        for alt in self.state.unfound_alterations():
            self._orig_display, self._mod_display = (
                self.processor.draw_circle_on_images(
                    self._orig_display,
                    self._mod_display,
                    alt,
                    self.REVEAL_COL
                )
            )

        for i in range(len(self.state.found_flags)):
            self.state.found_flags[i] = True

        self._game_active = False

        self._refresh_canvases()
        self._refresh_labels()

        self.status_lbl.configure(
            text="Differences revealed",
            fg="#89dceb"
        )

        self.reveal_btn.configure(
            state=tk.DISABLED,
            bg="#45475a",
            fg=self.TEXT_FG
        )

    # Helper Methods

    def _refresh_canvases(self):
        # Convert numpy arrays to PhotoImage and draw on the canvases.

        self._tk_orig = self._np_to_tk(self._orig_display)
        self._tk_mod = self._np_to_tk(self._mod_display)

        for canvas, tk_img in (
            (self.orig_canvas, self._tk_orig),
            (self.mod_canvas, self._tk_mod)
        ):

            canvas.delete("all")

            iw = tk_img.width()
            ih = tk_img.height()

            cw = canvas.winfo_width() or self.CANVAS_W
            ch = canvas.winfo_height() or self.CANVAS_H

            ox = max(0, (cw - iw) // 2)
            oy = max(0, (ch - ih) // 2)

            canvas.create_image(
                ox,
                oy,
                anchor=tk.NW,
                image=tk_img
            )

            canvas._img_offset = (ox, oy)

    def _refresh_labels(self):
        # Update score and status labels.

        self.remaining_lbl.configure(
            text=f"Remaining: {self.state.remaining()}"
        )

        self.mistakes_lbl.configure(
            text=f"Mistakes: {self.state.mistakes} / {GameState.MAX_MISTAKES}",
            fg="#f38ba8" if self.state.mistakes >= 2 else self.TEXT_FG
        )

        self.total_lbl.configure(
            text=f"Total Found: {self.state.total_found}"
        )

    def _canvas_to_image(self, cx: int, cy: int, canvas) -> tuple:
        # Convert canvas coordinates to image coordinates.

        offset = getattr(canvas, "_img_offset", (0, 0))

        ix = cx - offset[0]
        iy = cy - offset[1]

        if self._mod_display is None:
            return None, None

        h, w = self._mod_display.shape[:2]

        if 0 <= ix < w and 0 <= iy < h:
            return ix, iy

        return None, None

    @staticmethod
    def _np_to_tk(arr: np.ndarray) -> ImageTk.PhotoImage:
        # Convert to numpy RGB array to Tkinter PhotoImage.
        return ImageTk.PhotoImage(
            Image.fromarray(arr.astype(np.uint8))
        )