from src.watchdocr.plugins.image.textremover import ImageTextRemoverPlugin
from PIL import Image
import numpy as np
import cv2


__plugin_meta__ = {
    'id': 'watchdocr-image-textremover-inpaint',
    'name': 'InpaintTextRemover',
    'version': (0, 1, 0)
}
__plugin_main__ = 'InpaintTextRemoverPlugin'


LOG_TITLE = f'{__plugin_meta__["name"]} Plugin'


class InpaintTextRemoverPlugin(ImageTextRemoverPlugin):

    def filter_image(self, image, mask):
        image = np.array(image)
        mask = np.array(mask)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask_e = cv2.dilate(mask, kernel)

        dst = cv2.inpaint(image, mask_e, 2, cv2.INPAINT_NS)

        feather = cv2.GaussianBlur(mask_e, (7, 7), 0).astype(np.float32) / 255.0
        feather = feather[..., None]
        dst = (
            image.astype(np.float32) * (1 - feather) +
            dst.astype(np.float32) * feather
        ).astype(np.uint8)

        mask_b = cv2.GaussianBlur(mask, (51, 51), 0)
        dst_b = cv2.blur(dst, (55, 55))

        alpha = mask_b.astype(np.float32) / 255.0
        alpha = alpha[..., None]

        dst = (
            dst.astype(np.float32) * (1 - alpha) +
            dst_b.astype(np.float32) * alpha
        ).astype(np.uint8)

        # Remove background by mask
        dst = np.dstack((dst, mask_e))

        return Image.fromarray(dst, 'RGBA')
