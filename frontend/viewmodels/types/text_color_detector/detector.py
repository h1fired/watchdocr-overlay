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


def _detect_text_color_from_crop(crop_arr, assume_minority_is_text=True):
    gray = (
        0.299 * crop_arr[:, :, 0]
        + 0.587 * crop_arr[:, :, 1]
        + 0.114 * crop_arr[:, :, 2]
    )

    thresh = otsu_threshold(gray)

    dark_mask = gray <= thresh
    light_mask = ~dark_mask

    dark_count = int(dark_mask.sum())
    light_count = int(light_mask.sum())

    if assume_minority_is_text:
        text_mask, bg_mask = (
            (dark_mask, light_mask) if dark_count < light_count else (light_mask, dark_mask)
        )
    else:
        text_mask, bg_mask = (
            (dark_mask, light_mask) if dark_count > light_count else (light_mask, dark_mask)
        )

    # Guard against an empty mask (e.g. a totally uniform crop)
    if text_mask.sum() == 0:
        text_mask, bg_mask = bg_mask, text_mask

    text_rgb = crop_arr[text_mask].mean(axis=0)
    bg_rgb = crop_arr[bg_mask].mean(axis=0) if bg_mask.sum() else text_rgb

    def to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(*(int(c) for c in rgb))

    return {
        "text_rgb": tuple(int(c) for c in text_rgb),
        "text_hex": to_hex(text_rgb),
        "text_pixel_count": int(text_mask.sum()),
        "background_rgb": tuple(int(c) for c in bg_rgb),
        "background_hex": to_hex(bg_rgb),
        "background_pixel_count": int(bg_mask.sum()),
        "otsu_threshold": thresh,
    }


def detect_text_colors(qimage, rects, assume_minority_is_text=True, as_hex=True):
    img = qimage_to_pil(qimage)
    img_arr = np.array(img).astype(np.float64)
    H, W = img_arr.shape[:2]

    results = []
    for (x, y, w, h) in rects:
        x0, y0 = max(0, int(x)), max(0, int(y))
        x1, y1 = min(W, int(x + w)), min(H, int(y + h))
        if x1 <= x0 or y1 <= y0:
            results.append("#000000" if as_hex else {})
            continue
        crop_arr = img_arr[y0:y1, x0:x1]
        info = _detect_text_color_from_crop(crop_arr, assume_minority_is_text)
        results.append(info["text_hex"] if as_hex else info)

    return results
