import QtQuick
import "qrc:/qml/ui/overlay/components"

Item {
    id: root

    enum Style {
        Solid,
        SimpleInpaint
    }

    property int style: VisualHints.Style.Solid
    property alias boxes: container.boxes
    property alias parts: container.parts
    property bool usePerspective: false
    required property ImageProvider provider

    VisualHintContainer {
        id: container

        anchors.fill: parent

        filterDelegate: {
            switch (root.style) {
                case VisualHints.Style.SimpleInpaint:
                    return filterDelegateSimpleInpaint;
                default:
                    return filterDelegateSolid;
            }
        }
        textDelegate: {
            switch (root.style) {
                case VisualHints.Style.SimpleInpaint:
                    return textDelegateSimpleInpaint;
                default:
                    return textDelegateSolid;
            }
        }
    }

    function clear() {
        root.boxes = [];
        root.parts = [];
    }

    Component {
        id: filterDelegateSolid

        SolidFilterDelegate {
            usePerspective: root.usePerspective
        }
    }

    Component {
        id: filterDelegateSimpleInpaint

        SimpleInpaintFilterDelegate {
            usePerspective: root.usePerspective
            provider: root.provider
        }
    }

    Component {
        id: textDelegateSolid

        SolidTextDelegate {
            usePerspective: root.usePerspective
        }
    }

    Component {
        id: textDelegateSimpleInpaint

        SimpleInpaintTextDelegate {
            usePerspective: root.usePerspective
            provider: root.provider
        }
    }
}