import QtQuick
import "MatrixUtils.js" as MatrixUtils

Item {
    id: root

    required property var coordinates
    readonly property var _c: coordinates

    x: _c[0]
    y: _c[1]
    width: Math.sqrt(Math.pow(_c[2] - _c[0], 2) + Math.pow(_c[3] - _c[1], 2))
    height: Math.sqrt(Math.pow(_c[6] - _c[0], 2) + Math.pow(_c[7] - _c[1], 2))

    transform: Matrix4x4 {
        matrix: MatrixUtils.buildMatrix(root.x, root.y, root.width, root.height, root._c)
    }
}