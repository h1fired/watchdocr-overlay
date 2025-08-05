import pytesseract
from PIL import Image, ImageFilter, ImageChops, ImageOps, ImageEnhance


class OCR:
    def recognize(self, image: Image.Image):
        adjusted_image = OCRImageAdjuster.adjust(image)
        raw_text = pytesseract.image_to_string(adjusted_image)
        return raw_text


class OCRImageAdjuster:
    @staticmethod
    def adjust(image: Image.Image):
        _image = image
        _image = OCRImageAdjuster.adjust_to_grayscale(image)
        _image = OCRImageAdjuster.adjust_shadow_remove(_image)
        _image = OCRImageAdjuster.adjust_levels(_image, 40, 255, gamma=2.0)
        _image = OCRImageAdjuster.adjust_borders(_image, 10)
        return _image

    @staticmethod
    def adjust_to_grayscale(image: Image.Image):
        return image.convert('L')

    @staticmethod
    def adjust_shadow_remove(image: Image.Image):
        median_image = image.filter(ImageFilter.MedianFilter(size=21))
        diff_img = ImageChops.difference(image, median_image)
        diff_img = ImageOps.invert(diff_img)

        return diff_img

    @staticmethod
    def adjust_contrast(image: Image.Image):
        enhancer = ImageEnhance.Contrast(image)
        _image = ImageOps.autocontrast(image, cutoff=0)
        _image = enhancer.enhance(15.0)
        _image = _image.filter(ImageFilter.UnsharpMask(radius=1, percent=200, threshold=2))

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
    def adjust_borders(image: Image.Image, size: int):
        return ImageOps.expand(image, border=size, fill='white')
