import QtQuick
import "MatrixUtils.js" as MatrixUtils

Item {
    id: root

    required property var coordinates
    readonly property var _c: coordinates
    readonly property var _size: MatrixUtils.quadSize(_c)

    x: _c[0]
    y: _c[1]
    width: _size.width
    height: _size.height

    transform: Matrix4x4 {
        matrix: MatrixUtils.buildMatrix(root._c)
    }
}