import QtQuick

Delegate {
    id: root

    rectMargin: 2

    Repeater {
        model: parent.visible ? root.boxes : 0

        MatrixDelegateBox {
            id: box

            required property int index
            required property var modelData

            coordinates: root.expandQuad(modelData.coordinates, root.rectMargin)

            VisualHintText {
                id: textLabel

                anchors.fill: parent

                leftPadding: root.rectMargin * 2
                
                text: root.parts[index] ?? ""
            }
        }
    }
}
