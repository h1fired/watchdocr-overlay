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

                // Natural text dimensions: top-edge length × left-edge length
                // For rotated text this differs dramatically from the AABB
                readonly property var _c: modelData.coordinates ?? []
                readonly property bool _hasPerspective: _c.length === 8

                x: _hasPerspective
                    ? _c[0] - root._boxExpansion
                    : modelData.boundings[0] - root._boxExpansion
                y: _hasPerspective
                    ? _c[1] - root._boxExpansion
                    : modelData.boundings[1] - root._boxExpansion
                width: _hasPerspective
                    ? Math.sqrt(Math.pow(_c[2] - _c[0], 2) + Math.pow(_c[3] - _c[1], 2)) + root._boxExpansion * 2
                    : modelData.boundings[2] - modelData.boundings[0] + root._boxExpansion * 2
                height: _hasPerspective
                    ? Math.sqrt(Math.pow(_c[6] - _c[0], 2) + Math.pow(_c[7] - _c[1], 2)) + root._boxExpansion * 2
                    : modelData.boundings[3] - modelData.boundings[1] + root._boxExpansion * 2

                provider: root.provider
                text: root.parts[index]
                internalPadding: root._boxExpansion

                coordinates: _c
            }
        }
    }

    function clear() {
        root.boxes = ([]);
    }
}