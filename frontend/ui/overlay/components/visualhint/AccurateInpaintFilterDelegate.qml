import QtQuick
import App.Backend
import "qrc:/qml/ui/overlay/components"

MatrixDelegate {
    id: root

    ImageProvider {
        id: clearedImage

        visible: false

        layer.enabled: true

        providerId: "text_cleared_overlay"
    }

    Image {
        x: 0
        y: 0
        width: clearedImage.width
        height: clearedImage.height

        source: clearedImage.image.source
    }

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
        }
    }

    Connections {
        target: Backend.Preview

        function onTextClearedImageUpdated() {
            clearedImage.update();
        }
    }
}
