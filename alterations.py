import cv2
import numpy as np
import random
import math


class Alteration:
    #Abstract base class for all image alteration types.
    def __init__(self, region: tuple):
        """
        Parameters
        ----------
        region : (x, y, w, h) — top-left corner plus width/height
        """
        self.region = region   
        self.name   = "base"

    def apply(self, image: np.ndarray) -> np.ndarray:
        #Apply the alteration to image in-place and return it.
        raise NotImplementedError("Subclasses must implement apply()")

    def get_center(self) -> tuple:
        """Return the center (cx, cy) of the alteration region."""
        x, y, w, h = self.region
        return (x + w // 2, y + h // 2)

    def __repr__(self):
        return f"{self.__class__.__name__}(region={self.region})"


class ColourShiftAlteration(Alteration):
    #Shift the colour channels of a rectangular region.

    def __init__(self, region: tuple):
        super().__init__(region)
        self.name    = "colour_shift"
        self.b_shift = random.randint(-60, 60)
        self.g_shift = random.randint(-60, 60)
        self.r_shift = random.randint(-60, 60)
        # Ensure at least one channel is noticeably shifted
        while abs(self.b_shift) < 30 and abs(self.g_shift) < 30 and abs(self.r_shift) < 30:
            self.r_shift = random.randint(-60, 60)

    def apply(self, image: np.ndarray) -> np.ndarray:
        x, y, w, h = self.region
        roi = image[y:y + h, x:x + w].astype(np.int16)
        roi[:, :, 0] = np.clip(roi[:, :, 0] + self.b_shift, 0, 255)
        roi[:, :, 1] = np.clip(roi[:, :, 1] + self.g_shift, 0, 255)
        roi[:, :, 2] = np.clip(roi[:, :, 2] + self.r_shift, 0, 255)
        image[y:y + h, x:x + w] = roi.astype(np.uint8)
        return image


class BlurAlteration(Alteration):
    #Apply Gaussian blur to a rectangular region.

    def __init__(self, region: tuple):
        super().__init__(region)
        self.name        = "blur"
        self.kernel_size = random.choice([15, 21, 25])

    def apply(self, image: np.ndarray) -> np.ndarray:
        x, y, w, h = self.region
        roi = image[y:y + h, x:x + w]
        image[y:y + h, x:x + w] = cv2.GaussianBlur(
            roi, (self.kernel_size, self.kernel_size), 0
        )
        return image


class BrightnessAlteration(Alteration):
    #Increase or decrease brightness of a rectangular region.

    def __init__(self, region: tuple):
        super().__init__(region)
        self.name   = "brightness"
        self.factor = random.choice([-70, -55, 55, 70])

    def apply(self, image: np.ndarray) -> np.ndarray:
        x, y, w, h = self.region
        roi = image[y:y + h, x:x + w].astype(np.int16)
        roi = np.clip(roi + self.factor, 0, 255).astype(np.uint8)
        image[y:y + h, x:x + w] = roi
        return image


class NoiseAlteration(Alteration):
    #Add salt-and-pepper noise to a rectangular region.

    def __init__(self, region: tuple):
        super().__init__(region)
        self.name    = "noise"
        self.density = random.uniform(0.08, 0.15)

    def apply(self, image: np.ndarray) -> np.ndarray:
        x, y, w, h = self.region
        roi         = image[y:y + h, x:x + w].copy()
        total       = roi.shape[0] * roi.shape[1]
        num_noisy   = int(total * self.density)
        for _ in range(num_noisy):
            py = random.randint(0, roi.shape[0] - 1)
            px = random.randint(0, roi.shape[1] - 1)
            roi[py, px] = 255 if random.random() > 0.5 else 0
        image[y:y + h, x:x + w] = roi
        return image


class ContrastAlteration(Alteration):
    #Compress the contrast of a rectangular region.

    def __init__(self, region: tuple):
        super().__init__(region)
        self.name  = "contrast"
        self.alpha = random.uniform(0.4, 0.65)   # < 1 reduces contrast

    def apply(self, image: np.ndarray) -> np.ndarray:
        x, y, w, h = self.region
        roi  = image[y:y + h, x:x + w].astype(np.float32)
        mean = roi.mean()
        roi  = np.clip((roi - mean) * self.alpha + mean, 0, 255).astype(np.uint8)
        image[y:y + h, x:x + w] = roi
        return image