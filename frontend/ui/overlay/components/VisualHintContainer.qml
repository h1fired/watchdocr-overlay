import QtQuick
import "qrc:/qml/ui/overlay/components"

Item {
    id: root

    required property ImageProvider provider
    property var boxes: ([])
    property int _boxExpansion: 2

    Item {
        x: provider.x
        y: provider.y
        width: provider.width
        height: provider.height

        Repeater {
            model: root.boxes

            delegate: VisualHintBox {
                required property var modelData

                x: modelData[1][0]
                y: modelData[1][1] - root._boxExpansion
                width: modelData[1][2] - modelData[1][0]
                height: modelData[1][3] - modelData[1][1] + (root._boxExpansion * 2)

                provider: root.provider
                text: modelData[0]
            }
        }
    }

    function clear() {
        root.boxes = ([]);
    }
}