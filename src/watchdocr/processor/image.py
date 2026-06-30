from mss.windows import MSS as mss
from PIL import Image


def _box_to_dict(box: tuple[int, int, int, int]):
    return {
        'top': box[1],
        'left': box[0],
        'width': box[2],
        'height': box[3]
    }


class ScreenGrabber:
    @staticmethod
    def grab_screen_area(box: tuple[int, int, int, int]):
        try:
            with mss() as sct:
                sct_img = sct.grab(_box_to_dict(box))
                img = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
                return img
        except Exception:
            return None

    @staticmethod
    def grab_all_screens():
        try:
            with mss() as sct:
                sct_img = sct.grab(sct.monitors[0])
                img = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
                return img
        except Exception:
            return None
