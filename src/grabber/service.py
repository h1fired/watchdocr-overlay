from common.service import Service
from common.event import IEvent
from PIL import Image
from src.grabber.window import grab_window, grab_window_area


class _ImageGrabberWindowAreaCaptureEvent(IEvent):
    image: Image.Image


class ImageGrabberService(Service):
    class Events:
        IMAGE_CAPTURE = _ImageGrabberWindowAreaCaptureEvent

    def on_init(self):
        return super().on_init()

    def grab_window(self):
        return grab_window()

    def grab_window_area(self, box: tuple[int, int, int, int]):
        image = grab_window_area(box)
        self.event.dispatch(self.Events.IMAGE_CAPTURE, {'image': image})
        return image
