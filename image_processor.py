
import cv2
import numpy as np
import random
import math

from alterations import (
    Alteration,
    ColourShiftAlteration,
    BlurAlteration,
    BrightnessAlteration,
    NoiseAlteration,
    ContrastAlteration,
)


class ImageProcessor:

#Handles all image loading and modification using OpenCV.
    NUM_DIFFERENCES  = 5
    REGION_MIN_SIZE  = 40     # minimum px size for a difference region
    REGION_MAX_SIZE  = 90     # maximum px size for a difference region
    MAX_PLACE_TRIES  = 500    # max attempts to place non-overlapping regions

# All available alteration types (polymorphism — picked randomly at runtime)
    ALTERATION_CLASSES = [
        ColourShiftAlteration,
        BlurAlteration,
        BrightnessAlteration,
        NoiseAlteration,
        ContrastAlteration,
    ]

    def __init__(self):
        self.original_bgr : np.ndarray | None = None
        self.modified_bgr : np.ndarray | None = None
        self.alterations  : list               = []
        self.img_width    : int                = 0
        self.img_height   : int                = 0

    # ── Public methods ───────────────────────────────────────

    def load_image(self, path: str, max_dim: int = 700) -> bool:
        
        #Load, scale image, and generate 5 differences.
        #Returns True on success, False if file could not be read.
    
        img = cv2.imread(path)
        if img is None:
            return False
        img = self._scale_image(img, max_dim)
        self.original_bgr             = img
        self.img_height, self.img_width = img.shape[:2]
        self._generate_modified()
        return True

    def get_original_rgb(self) -> np.ndarray:
        #Return original image as RGB numpy array
        return cv2.cvtColor(self.original_bgr, cv2.COLOR_BGR2RGB)

    def get_modified_rgb(self) -> np.ndarray:
        #Return modified image as RGB numpy array (for Tkinter display)
        return cv2.cvtColor(self.modified_bgr, cv2.COLOR_BGR2RGB)

    def draw_circle_on_images(
        self,
        orig       : np.ndarray,
        mod        : np.ndarray,
        alteration : Alteration,
        colour     : tuple,
        thickness  : int = 3,
    ) -> tuple:
        
        #Draw a circle around an alteration region on both image arrays.
        
        cx, cy     = alteration.get_center()
        x, y, w, h = alteration.region
        radius     = int(math.hypot(w, h) / 2) + 8
        cv2.circle(orig, (cx, cy), radius, colour, thickness)
        cv2.circle(mod,  (cx, cy), radius, colour, thickness)
        return orig, mod

    #Private methods

    def _scale_image(self, img: np.ndarray, max_dim: int) -> np.ndarray:
        #Scale image so its largest dimension fits within max_dim.
        h, w  = img.shape[:2]
        scale = min(max_dim / w, max_dim / h, 1.0)
        if scale < 1.0:
            new_w = int(w * scale)
            new_h = int(h * scale)
            img   = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return img

    def _generate_modified(self):
        #Clone the original and apply exactly 5 non-overlapping alterations.
        self.modified_bgr = self.original_bgr.copy()
        self.alterations  = []
        placed_regions    = []

        tries = 0
        while len(self.alterations) < self.NUM_DIFFERENCES and tries < self.MAX_PLACE_TRIES:
            tries += 1
            region = self._random_region()

            if self._overlaps(region, placed_regions):
                continue

            # Pick a random alteration type — polymorphism at runtime
            alt_cls    = random.choice(self.ALTERATION_CLASSES)
            alteration = alt_cls(region)
            alteration.apply(self.modified_bgr)

            placed_regions.append(region)
            self.alterations.append(alteration)

    def _random_region(self) -> tuple:
        #Generate a random (x, y, w, h) region within the image bounds.
        w = random.randint(self.REGION_MIN_SIZE, self.REGION_MAX_SIZE)
        h = random.randint(self.REGION_MIN_SIZE, self.REGION_MAX_SIZE)
        x = random.randint(0, max(1, self.img_width  - w))
        y = random.randint(0, max(1, self.img_height - h))
        return (x, y, w, h)

    @staticmethod
    def _overlaps(region: tuple, existing: list, margin: int = 10) -> bool:
        """Return True if region overlaps with any region in existing list."""
        x1, y1, w1, h1 = region
        for (x2, y2, w2, h2) in existing:
            if not (
                x1 + w1 + margin <= x2 or
                x2 + w2 + margin <= x1 or
                y1 + h1 + margin <= y2 or
                y2 + h2 + margin <= y1
            ):
                return True
        return False