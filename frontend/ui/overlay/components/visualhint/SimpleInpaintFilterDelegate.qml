import QtQuick
import Qt5Compat.GraphicalEffects
import "qrc:/qml/ui/overlay/components"

MatrixDelegate {
    id: root

    required property ImageProvider provider

    Repeater {

        model: parent.visible ? root.boxes : 0

        Item {
            id: box

            readonly property var _c: modelData.coordinates ?? []
            readonly property var _b: modelData.boundings ?? []
            readonly property bool _hasPerspective: root.usePerspective && modelData.has_perspective

            x: box._hasPerspective
                ? _c[0]
                : _b[0]
            y: box._hasPerspective
                ? _c[1]
                : _b[1]
            width: box._hasPerspective
                ? Math.sqrt(Math.pow(_c[2] - _c[0], 2) + Math.pow(_c[3] - _c[1], 2))
                : _b[2] - _b[0]
            height: box._hasPerspective
                ? Math.sqrt(Math.pow(_c[6] - _c[0], 2) + Math.pow(_c[7] - _c[1], 2))
                : _b[3] - _b[1]

            transform: Matrix4x4 {
                matrix: box._hasPerspective
                    ? root.buildMatrix(box.x, box.y, box.width, box.height, box._c)
                    : Qt.matrix4x4()
            }

            // Inpaint
            ShaderEffectSource {
                id: rawBoxCapture

                visible: false

                live: true
                sourceItem: root.provider
                sourceRect: Qt.rect(
                    box.x,
                    box.y,
                    box.width,
                    box.height
                )
            }

            ShaderEffect {
                id: cleanBackgroundBox

                property variant source: rawBoxCapture
                property vector2d pixelSize: Qt.vector2d(4, 4)

                anchors.fill: parent

                layer.enabled: true
                opacity: 0

                fragmentShader: "qrc:/qml/ui/shaders/average.frag.qsb" 
            }

            Rectangle {
                id: boxMask

                visible: false

                anchors.fill: parent

                radius: 6
                color: "black"
            }

            OpacityMask {
                id: maskedBackground

                anchors.fill: parent

                source: cleanBackgroundBox
                maskSource: boxMask
            }
        }
    }
}
