from mss.windows import MSS as mss
from PIL import Image


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
        'top': box[0],
        'left': box[1],
        'width': box[2],
        'height': box[3]
    }
