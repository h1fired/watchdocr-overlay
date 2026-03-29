from mss.windows import MSS as mss
from PIL import Image, ImageFilter, ImageChops, ImageOps, ImageEnhance
import numpy as np


def grab_window():
    with mss() as sct:
        sct_img = sct.grab()
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        return img


def grab_window_area(box: tuple[int, int, int, int]):
    with mss() as sct:
        sct_img = sct.grab(_box_to_dict(box))
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        return img


def grab_all_screens():
    with mss() as sct:
        sct_img = sct.grab(sct.monitors[0])
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        return img


class ScreenGrabber:
    @staticmethod
    def grab_screen_area(box: tuple[int, int, int, int]):
        with mss() as sct:
            sct_img = sct.grab(_box_to_dict(box))
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            return img

    @staticmethod
    def grab_all_screens():
        with mss() as sct:
            sct_img = sct.grab(sct.monitors[0])
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            return img


def _box_to_dict(box: tuple[int, int, int, int]):
    return {
        'top': box[1],
        'left': box[0],
        'width': box[2],
        'height': box[3]
    }


class OcrImageFilter:
    @staticmethod
    def adjust(image: Image.Image):
        _image = image
        _image = OcrImageFilter.adjust_contrast(image)
        _image = OcrImageFilter.adjust_to_grayscale(image)
        _image = OcrImageFilter.adjust_shadow_remove(_image)
        _image = OcrImageFilter.adjust_sigmoid_threshold(_image, 127, 0.03)
        _image = OcrImageFilter.adjust_levels(_image, 110, 255, 1.5)
        _image = OcrImageFilter.adjust_borders(_image, 10)
        return _image

    @staticmethod
    def adjust_to_grayscale(image: Image.Image):
        return image.convert('L')

    @staticmethod
    def adjust_shadow_remove(image: Image.Image):
        median_image = image.filter(ImageFilter.MedianFilter(size=11))
        diff_img = ImageChops.difference(image, median_image)
        diff_img = ImageOps.invert(diff_img)

        return diff_img

    @staticmethod
    def adjust_contrast(image: Image.Image):
        enhancer = ImageEnhance.Contrast(image)
        _image = enhancer.enhance(2)

        return _image

    @staticmethod
    def adjust_levels(image: Image.Image, black: int, white: int, gamma: float):
        # Clamp to prevent divide by zero
        white = max(white, black + 1)

        # Build lookup table (LUT)
        lut = []
        for i in range(256):
            if i <= black:
                lut.append(0)
            elif i >= white:
                lut.append(255)
            else:
                # Normalize to 0–1, apply gamma, rescale to 0–255
                norm = (i - black) / (white - black)
                val = int((norm ** gamma) * 255)
                lut.append(max(0, min(255, val)))

        return image.point(lut)

    @staticmethod
    def adjust_threshold(image: Image.Image, value=127):
        return image.point(lambda p: 255 if p > value else 0)

    @staticmethod
    def adjust_sigmoid_threshold(image: Image.Image, threshold=127, steepness=0.05):
        arr = np.array(image, dtype=np.float32)
        soft = 255 / (1 + np.exp(-steepness * (arr - threshold)))
        return Image.fromarray(soft.astype(np.uint8))

    @staticmethod
    def adjust_borders(image: Image.Image, size: int):
        return ImageOps.expand(image, border=size, fill='white')
