from mss.windows import MSS as mss
from PIL import Image


def grab_window():
    with mss() as sct:
        sct_img = sct.grab()
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        return img


def grab_window_area(box: tuple[int, int, int, int]):
    with mss() as sct:
        sct_img = sct.grab(box)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        return img
