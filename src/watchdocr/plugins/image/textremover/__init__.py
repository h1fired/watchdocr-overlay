from src.common.plugin import PriorityPlugin
from PIL import Image


class ImageTextRemoverPlugin(PriorityPlugin):

    def filter_image(self, image: Image.Image, mask: Image.Image):
        pass
