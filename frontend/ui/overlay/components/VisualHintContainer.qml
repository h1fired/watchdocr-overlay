import QtQuick
import "qrc:/qml/ui/overlay/components"

Item {
    id: root

    required property ImageProvider provider
    property var boxes: ([])
    property var parts: ([])
    property int _boxExpansion: 2

    Item {
        x: provider.x
        y: provider.y
        width: provider.width
        height: provider.height

        Repeater {
            model: root.visible ? root.boxes : 0

            delegate: VisualHintBox {
                required property int index
                required property var modelData

                x: modelData.boundings[0] - root._boxExpansion
                y: modelData.boundings[1] - root._boxExpansion
                width: modelData.boundings[2] - modelData.boundings[0] + (root._boxExpansion * 2)
                height: modelData.boundings[3] - modelData.boundings[1] + (root._boxExpansion * 2)

                provider: root.provider
                text: root.parts[index]
                internalPadding: root._boxExpansion
            }
        }
    }

    function clear() {
        root.boxes = ([]);
    }
}