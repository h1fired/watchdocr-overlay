import QtQuick

Delegate {
    id: root

    function buildMatrix(x, y, w, h, coordinates) {
        let c = coordinates;

        // Translate to local space
        let local = [
            c[0] - x,  c[1] - y,   // TL
            c[2] - x,  c[3] - y,   // TR
            c[4] - x,  c[5] - y,   // BR
            c[6] - x,  c[7] - y    // BL
        ]

        let E = 0
        let W = w - 2 * E
        let H = h - 2 * E

        return quadToMatrix4x4(local, W, H, E)
    }

    function quadToMatrix4x4(q, W, H, E) {
        let x0 = q[0], y0 = q[1]
        let x1 = q[2], y1 = q[3]
        let x2 = q[4], y2 = q[5]
        let x3 = q[6], y3 = q[7]

        let dx1 = x1 - x2, dx2 = x3 - x2, dx3 = x0 - x1 + x2 - x3
        let dy1 = y1 - y2, dy2 = y3 - y2, dy3 = y0 - y1 + y2 - y3

        let a, b, c = x0, d, e, f = y0, g, hh

        if (dx3 === 0 && dy3 === 0) {
            // Affine (parallelogram) case
            a = x1 - x0;  b = x3 - x0
            d = y1 - y0;  e = y3 - y0
            g = 0;        hh = 0
        } else {
            // Perspective case
            let det = dx1 * dy2 - dx2 * dy1
            if (det === 0) det = 0.0001
            g  = (dx3 * dy2 - dx2 * dy3) / det
            hh = (dx1 * dy3 - dx3 * dy1) / det
            a = x1 - x0 + g * x1;  b = x3 - x0 + hh * x3
            d = y1 - y0 + g * y1;  e = y3 - y0 + hh * y3
        }

        let sx = W > 0 ? 1 / W : 0
        let sy = H > 0 ? 1 / H : 0

        let m00 = a * sx
        let m01 = b * sy
        let m03 = -a * sx * E - b * sy * E + c

        let m10 = d * sx
        let m11 = e * sy
        let m13 = -d * sx * E - e * sy * E + f

        let m30 = g * sx
        let m31 = hh * sy
        let m33 = -g * sx * E - hh * sy * E + 1

        return Qt.matrix4x4(
            m00, m01, 0, m03,
            m10, m11, 0, m13,
            0,   0,   1, 0,
            m30, m31, 0, m33
        )
    }

    function expandQuad(c, margin) {
        if (margin === 0)
            return c

        return [
            c[0] - margin, c[1] - margin,
            c[2] + margin, c[3] - margin,
            c[4] + margin, c[5] + margin,
            c[6] - margin, c[7] + margin
        ]
    }
}