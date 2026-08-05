import numpy as np
from PIL.ImageQt import fromqimage


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


def _detect_text_color_from_crop(crop_arr):
    if crop_arr.size == 0 or crop_arr.shape[0] == 0 or crop_arr.shape[1] == 0:
        return {
            'text_hex': '#FFFFFF',
            'background_hex': '#000000'
        }

    gray = (
        0.299 * crop_arr[:, :, 0]
        + 0.587 * crop_arr[:, :, 1]
        + 0.114 * crop_arr[:, :, 2]
    )

    thresh = otsu_threshold(gray)

    dark_mask = gray <= thresh
    light_mask = ~dark_mask

    border = np.zeros_like(dark_mask, dtype=bool)
    border[0, :] = True
    border[-1, :] = True
    border[:, 0] = True
    border[:, -1] = True

    dark_border_frac = dark_mask[border].mean() if border.any() else 0.0
    light_border_frac = light_mask[border].mean() if border.any() else 0.0

    if dark_border_frac > light_border_frac:
        bg_mask, text_mask = dark_mask, light_mask
    else:
        bg_mask, text_mask = light_mask, dark_mask

    if text_mask.sum() == 0:
        text_mask, bg_mask = bg_mask, text_mask

    text_rgb = np.median(crop_arr[text_mask], axis=0)
    bg_rgb = np.median(crop_arr[bg_mask], axis=0) if bg_mask.sum() else text_rgb

    def to_hex(rgb):
        return '#{:02x}{:02x}{:02x}'.format(*(int(c) for c in rgb))

    return {
        'text_hex': to_hex(text_rgb),
        'background_hex': to_hex(bg_rgb),
    }


def detect_text_colors(qimage, rects):
    img = qimage_to_pil(qimage)
    img_arr = np.array(img).astype(np.float64)

    results = []
    for (x1, y1, x2, y2) in rects:
        if x2 <= x1 or y2 <= y1:
            results.append('#FFFFFF')
            continue

        crop_arr = img_arr[y1:y2, x1:x2]
        info = _detect_text_color_from_crop(crop_arr)
        results.append(info['text_hex'])

    return results
