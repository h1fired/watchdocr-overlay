import QtQuick
import App.ImageText
import "qrc:/qml/ui/overlay/components"

MatrixDelegate {
    id: root

    required property ImageProvider provider
    rectMargin: 2

    TextColorDetector {
        id: detector

        rects: root.boxes
        image: provider.providerId
    }

    Repeater {
        model: parent.visible ? root.boxes : 0

        Item {
            id: box

            readonly property var _c: root.expandQuad(modelData.coordinates, root.rectMargin) ?? []
            readonly property var _b: modelData.boundings ?? []
            readonly property bool _hasPerspective: root.usePerspective && modelData.has_perspective

            x: box._hasPerspective
                ? _c[0]
                : _b[0] - root.rectMargin
            y: box._hasPerspective
                ? _c[1]
                : _b[1] - root.rectMargin
            width: box._hasPerspective
                ? Math.sqrt(Math.pow(_c[2] - _c[0], 2) + Math.pow(_c[3] - _c[1], 2))
                : _b[2] - _b[0] + (root.rectMargin * 2)
            height: box._hasPerspective
                ? Math.sqrt(Math.pow(_c[6] - _c[0], 2) + Math.pow(_c[7] - _c[1], 2))
                : _b[3] - _b[1] + (root.rectMargin * 2)

            transform: Matrix4x4 {
                matrix: box._hasPerspective
                    ? root.buildMatrix(box.x, box.y, box.width, box.height, box._c)
                    : Qt.matrix4x4()
            }

            VisualHintText {
                id: textLabel

                anchors.fill: parent

                leftPadding: root.rectMargin * 2
                
                text: root.parts[index] ?? ""
                color: detector.colorsOutput[index]
                    ? detector.colorsOutput[index].text
                    : "#FFFFFF"
                style: detector.colorsOutput[index]
                    && detector.colorsOutput[index].has_border
                    ? Text.Outline
                    : Text.Normal
                styleColor: detector.colorsOutput[index]
                    && detector.colorsOutput[index].has_border
                    ? detector.colorsOutput[index].border
                    : "#000000"
            }
        }
    }
}
