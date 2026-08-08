import numpy as np
from PIL.ImageQt import fromqimage
from PIL import Image, ImageDraw
from qt.gui import QColor
from dataclasses import dataclass, asdict
import math


def otsu_threshold(gray):
    hist, _ = np.histogram(gray, bins=256, range=(0, 256))
    hist = hist.astype(np.float64)
    total = hist.sum()

    sum_total = np.sum(np.arange(256) * hist)
    sum_bg = 0.0
    weight_bg = 0.0

    best_thresh = 0
    best_variance = -1.0

    for t in range(256):
        weight_bg += hist[t]
        if weight_bg == 0:
            continue
        weight_fg = total - weight_bg
        if weight_fg == 0:
            break

        sum_bg += t * hist[t]
        mean_bg = sum_bg / weight_bg
        mean_fg = (sum_total - sum_bg) / weight_fg

        variance = weight_bg * weight_fg * (mean_bg - mean_fg) ** 2

        if variance > best_variance:
            best_variance = variance
            best_thresh = t

    return best_thresh


def qimage_to_pil(qimage):
    return fromqimage(qimage).convert("RGB")


def color_diff(color1: QColor, color2: QColor):
    h1, s1, l1 = color1.hue(), color1.saturation(), color1.lightness()
    h2, s2, l2 = color2.hue(), color2.saturation(), color2.lightness()
    d = math.sqrt((h2-h1)**2+(s2-s1)**2+(l2-l1)**2)
    p = d / math.sqrt(255**2+255**2+255**2)
    return p


@dataclass(slots=True)
class DetectColorOutput:
    text: QColor
    has_border: bool
    border: QColor

    def to_dict(self):
        return asdict(self)


_DEFAULT = DetectColorOutput(QColor('#FFFFFF'), False, QColor('#000000'))


def _detect_text_color_from_masked(crop_arr, shape_mask, ring_px=2):
    if crop_arr.size == 0 or shape_mask.sum() < 4:
        return _DEFAULT

    gray = (
        0.299 * crop_arr[:, :, 0]
        + 0.587 * crop_arr[:, :, 1]
        + 0.114 * crop_arr[:, :, 2]
    )

    thresh = otsu_threshold(gray[shape_mask])

    dark_mask = (gray <= thresh) & shape_mask
    light_mask = (gray > thresh) & shape_mask

    # boundary ring of the polygon, not of the bounding box
    ring = shape_mask & ~_erode(shape_mask, ring_px)
    if ring.sum() == 0:
        ring = shape_mask

    dark_border_frac = dark_mask[ring].mean()
    light_border_frac = light_mask[ring].mean()

    if dark_border_frac > light_border_frac:
        bg_mask, text_mask = dark_mask, light_mask
    else:
        bg_mask, text_mask = light_mask, dark_mask

    if text_mask.sum() == 0:
        text_mask, bg_mask = bg_mask, text_mask
    if text_mask.sum() == 0:
        return _DEFAULT

    text_rgb = np.median(crop_arr[text_mask], axis=0)
    bg_rgb = np.median(crop_arr[bg_mask], axis=0) if bg_mask.sum() else text_rgb

    text_color = QColor(*(int(c) for c in text_rgb))
    bg_color = QColor(*(int(c) for c in bg_rgb))

    border_color = QColor('#000000')
    has_border = color_diff(text_color, bg_color) < 0.1
    if has_border:
        border_color = (
            text_color.darker(150) if text_color.lightness() > 128
            else text_color.lighter(150)
        )

    return DetectColorOutput(text_color, has_border, border_color)


def _polygon_mask(points, x0, y0, w, h):
    """Rasterize polygon (absolute coords) into a bool mask of the bbox."""
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon(
        [(float(px) - x0, float(py) - y0) for px, py in points], fill=255
    )
    return np.array(m) > 0


def _erode(mask, iterations=1):
    """4-neighbour erosion; outside the array counts as background."""
    for _ in range(iterations):
        e = np.zeros_like(mask)
        e[1:-1, 1:-1] = (
            mask[1:-1, 1:-1]
            & mask[:-2, 1:-1] & mask[2:, 1:-1]
            & mask[1:-1, :-2] & mask[1:-1, 2:]
        )
        mask = e
    return mask


def _normalize(region):
    if not region:
        raise ValueError('Empty region')

    # already a sequence of point pairs?
    first = region[0]
    if isinstance(first, (tuple, list)):
        return [(float(p[0]), float(p[1])) for p in region]

    if len(region) % 2 != 0:
        raise ValueError(f'Flat region needs an even number of values, got {len(region)}')

    if len(region) == 4:
        x1, y1, x2, y2 = map(float, region)
        return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

    it = iter(map(float, region))
    return list(zip(it, it))


def detect_text_colors(qimage, regions):
    img = qimage_to_pil(qimage)
    img_arr = np.array(img).astype(np.float64)
    H, W = img_arr.shape[:2]

    results = []
    for region in regions:
        pts = _normalize(region)

        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x0, y0 = max(0, int(math.floor(min(xs)))), max(0, int(math.floor(min(ys))))
        x1, y1 = min(W, int(math.ceil(max(xs)))), min(H, int(math.ceil(max(ys))))

        if x1 <= x0 or y1 <= y0:
            results.append(_DEFAULT.to_dict())
            continue

        crop_arr = img_arr[y0:y1, x0:x1]
        mask = _polygon_mask(pts, x0, y0, x1 - x0, y1 - y0)
        results.append(_detect_text_color_from_masked(crop_arr, mask).to_dict())

    return results
