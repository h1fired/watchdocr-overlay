import QtQuick

Delegate {
    id: root

    Repeater {

        model: parent.visible ? root.boxes : 0

        MatrixDelegateBox {
            id: box

            required property var modelData

            coordinates: root.expandQuad(modelData.coordinates, root.rectMargin)

            Rectangle {

                anchors.fill: parent

                radius: 6
                color: "black"
            }
        }
    }
}
