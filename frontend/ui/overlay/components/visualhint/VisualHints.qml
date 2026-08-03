import QtQuick

Item {
    id: root

    enum Style {
        Solid
        // SimpleInpaint,
        // AccurateInpaint,
    }

    property int style: VisualHints.Style.Solid
    property alias boxes: container.boxes
    property alias parts: container.parts
    property bool usePerspective: false

    VisualHintContainer {
        id: container

        anchors.fill: parent

        filterDelegate: {
            switch (root.style) {
                default:
                    return filterDelegateSolid;
            }
        }
        textDelegate: {
            switch (root.style) {
                default:
                    return textDelegateSolid;
            }
        }
    }

    function clear() {
        container.clear();
    }

    Component {
        id: filterDelegateSolid

        SolidFilterDelegate {
            boxes: root.boxes
            usePerspective: root.usePerspective
        }
    }

    Component {
        id: textDelegateSolid

        SolidTextDelegate {
            text: modelData
        }
    }
}