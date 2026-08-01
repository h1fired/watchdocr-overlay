import QtQuick
import "qrc:/qml/ui/overlay/components"

Item {
    id: root

    required property ImageProvider provider
    property var boxes: ([])
    property var parts: ([])
    property bool perspectiveMode: true
    property int _boxExpansion: height > 12 ? 2 : 0

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

                provider: root.provider

                text: root.parts[index]
                internalPadding: root._boxExpansion

                perspectiveMode: root.perspectiveMode
                perspectiveSupported: modelData.has_perspective

                coordinates: modelData.coordinates
                boundings: modelData.boundings
            }
        }
    }

    function clear() {
        root.boxes = ([]);
        root.parts = ([]);
    }
}