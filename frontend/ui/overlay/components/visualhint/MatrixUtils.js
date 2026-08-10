.pragma library

let EPS = 1e-7

function _identity() {
    return Qt.matrix4x4(
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
    );
}

function _normalize(coordinates) {
    if (!coordinates)
        return null;

    let c = [];
    for (let i = 0; i < 8; ++i) {
        let v = Number(coordinates[i]);
        if (!isFinite(v))
            return null;
        c.push(v);
    }

    let area = 0;
    for (let j = 0; j < 4; ++j) {
        let k = (j + 1) % 4;
        area += c[j*2] * c[k*2+1] - c[k*2] * c[j*2+1];
    }
    if (area < 0) {
        c = [c[0], c[1], c[6], c[7], c[4], c[5], c[2], c[3]];
    }

    return c;
}

function quadSize(coordinates) {
    let c = _normalize(coordinates);

    if (!c)
        return { width: 0, height: 0 };

    let top = Math.hypot(c[2]-c[0], c[3]-c[1]);
    let bottom = Math.hypot(c[4]-c[6], c[5]-c[7]);
    let left = Math.hypot(c[6]-c[0], c[7]-c[1]);
    let right = Math.hypot(c[4]-c[2], c[5]-c[3]);

    return { width: Math.max(top, bottom), height: Math.max(left, right) };
}

function buildMatrix(coordinates) {
    let c = _normalize(coordinates);
    if (!c) {
        return _identity();
    }

    let size = quadSize(c);
    let W = size.width, H = size.height;
    if (!(W > 0) || !(H > 0)) {
        return _identity();
    }

    let x0 = 0, y0 = 0;
    let x1 = c[2] - c[0], y1 = c[3] - c[1];
    let x2 = c[4] - c[0], y2 = c[5] - c[1];
    let x3 = c[6] - c[0], y3 = c[7] - c[1];

    let dx1 = x1 - x2, dx2 = x3 - x2, dx3 = x0 - x1 + x2 - x3;
    let dy1 = y1 - y2, dy2 = y3 - y2, dy3 = y0 - y1 + y2 - y3;

    let mag = Math.max(
        Math.abs(dx1), Math.abs(dx2),
        Math.abs(dy1), Math.abs(dy2),
        1
    );

    let a, b, d, e, g, h;

    if (Math.abs(dx3) < EPS * mag && Math.abs(dy3) < EPS * mag) {
        a = x1 - x0;
        b = x3 - x0;
        d = y1 - y0;
        e = y3 - y0;
        g = 0;
        h = 0;
    } else {
        let det = dx1 * dy2 - dx2 * dy1;
        if (Math.abs(det) < EPS * mag * mag) {
            return _identity();
        }

        g = (dx3 * dy2 - dx2 * dy3) / det;
        h = (dx1 * dy3 - dx3 * dy1) / det;

        a = x1 - x0 + g * x1;  b = x3 - x0 + h * x3;
        d = y1 - y0 + g * y1;  e = y3 - y0 + h * y3;
    }

    let sx = 1 / W;
    let sy = 1 / H;

    return Qt.matrix4x4(
        a * sx, b * sy, 0, 0,
        d * sx, e * sy, 0, 0,
        0,      0,      1, 0,
        g * sx, h * sy, 0, 1
    );
}