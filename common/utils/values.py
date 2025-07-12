import math


def normalize(value: float, old_range=(0, 1), new_range=(0, 1)):
    slope = (new_range[1] - new_range[0]) / (old_range[1] - old_range[0])
    return (value - old_range[0]) * slope + new_range[0]


def reformat_boundings(boundings):
    x1, y1, x2, y2 = boundings
    w, h = x2 - x1, y2 - y1
    x1n, y1n = x1 + min(w, 0), y1 + min(h, 0)
    wn, hn = abs(w), abs(h)

    return x1n, y1n, x1n + wn, y1n + hn


def contains(value, range):
    x, y = range
    return x <= value <= y


def contains2D(x, y, range_x, range_y):
    x1, x2 = range_x
    y1, y2 = range_y

    return x1 <= x <= x2 and y1 <= y <= y2


def limit(value, minv: int | float, maxv: int | float):
    return min(max(value, minv), maxv)


def rad_to_deg(radians_list):
    return [float(math.degrees(r)) for r in radians_list]
