import QtQuick
import Qt5Compat.GraphicalEffects

Item {
    id: root

    required property ImageProvider provider
    required property string text
    property int internalPadding: 0
    property var coordinates: []
    property bool perspectiveMode: true

    transform: Matrix4x4 {
        matrix: root.perspective
            ? root._buildMatrix()
            : Qt.matrix4x4()
    }

    // ShaderEffectSource {
    //     id: rawBoxCapture

    //     visible: false
    //     live: true

    //     sourceItem: provider
    //     sourceRect: Qt.rect(
    //         root.x + root.internalPadding,
    //         root.y + root.internalPadding,
    //         root.width - (root.internalPadding * 2),
    //         root.height - (root.internalPadding * 2)
    //     )
    // }

    // ShaderEffect {
    //     id: cleanBackgroundBox

    //     property variant source: rawBoxCapture
    //     property vector2d pixelSize: Qt.vector2d(4, 4)

    //     anchors.fill: parent
    //     layer.enabled: true
    //     opacity: 0

    //     fragmentShader: "qrc:/qml/ui/shaders/average.frag.qsb" 
    // }

    Rectangle {
        id: boxMask

        visible: true

        anchors.fill: parent
        radius: 6
        color: "black"
    }

    // OpacityMask {
    //     id: maskedBackground

    //     anchors.fill: parent

    //     source: cleanBackgroundBox
    //     maskSource: boxMask
    // }

    // Box text with background blending
    Text {
        id: textLabel

        visible: true

        anchors.fill: parent
        leftPadding: root.internalPadding * 2
        
        text: root.text
        fontSizeMode: Text.Fit
        font.pixelSize: height
        font.weight: 600
        minimumPixelSize: 8
        horizontalAlignment: Text.AlignLeft
        verticalAlignment: Text.AlignVCenter
        padding: 0

        renderType: Text.QtRendering
        antialiasing: true

        color: "white"
    }

    // ShaderEffectSource {
    //     id: textMaskSource

    //     visible: false

    //     sourceItem: textLabel
    //     live: true
    //     smooth: true
    //     samples: 4
    // }

    // ShaderEffect {
    //     anchors.fill: parent

    //     property variant background: cleanBackgroundBox
    //     property variant textMask: textMaskSource

    //     fragmentShader: "qrc:/qml/ui/shaders/text_difference.frag.qsb"

    //     smooth: true
    // }

    function _buildMatrix() {
        var c = root.coordinates  // [x0,y0, x1,y1, x2,y2, x3,y3] absolute
        // Translate to local space (subtract item's top-left position)
        var local = [
            c[0] - root.x,  c[1] - root.y,   // TL
            c[2] - root.x,  c[3] - root.y,   // TR
            c[4] - root.x,  c[5] - root.y,   // BR
            c[6] - root.x,  c[7] - root.y    // BL
        ]
        
        var E = root.internalPadding
        var W = root.width - 2 * E
        var H = root.height - 2 * E

        return quadToMatrix4x4(local, W, H, E)
    }

    // Maps item coordinates [E..W+E] x [E..H+E] → arbitrary quad q[]
    function quadToMatrix4x4(q, W, H, E) {
        var x0 = q[0], y0 = q[1]
        var x1 = q[2], y1 = q[3]
        var x2 = q[4], y2 = q[5]
        var x3 = q[6], y3 = q[7]

        var dx1 = x1 - x2, dx2 = x3 - x2, dx3 = x0 - x1 + x2 - x3
        var dy1 = y1 - y2, dy2 = y3 - y2, dy3 = y0 - y1 + y2 - y3

        var a, b, c = x0, d, e, f = y0, g, hh

        if (dx3 === 0 && dy3 === 0) {
            // Affine (parallelogram) case
            a = x1 - x0;  b = x3 - x0
            d = y1 - y0;  e = y3 - y0
            g = 0;        hh = 0
        } else {
            // Perspective case
            var det = dx1 * dy2 - dx2 * dy1
            if (det === 0) det = 0.0001
            g  = (dx3 * dy2 - dx2 * dy3) / det
            hh = (dx1 * dy3 - dx3 * dy1) / det
            a = x1 - x0 + g * x1;  b = x3 - x0 + hh * x3
            d = y1 - y0 + g * y1;  e = y3 - y0 + hh * y3
        }

        var sx = W > 0 ? 1 / W : 0
        var sy = H > 0 ? 1 / H : 0

        var m00 = a * sx
        var m01 = b * sy
        var m03 = -a * sx * E - b * sy * E + c

        var m10 = d * sx
        var m11 = e * sy
        var m13 = -d * sx * E - e * sy * E + f

        var m30 = g * sx
        var m31 = hh * sy
        var m33 = -g * sx * E - hh * sy * E + 1

        return Qt.matrix4x4(
            m00, m01, 0, m03,
            m10, m11, 0, m13,
            0,   0,   1, 0,
            m30, m31, 0, m33
        )
    }
}