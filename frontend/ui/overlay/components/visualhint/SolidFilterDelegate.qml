import QtQuick

Repeater {
    property var boxes: []

    model: parent.visible ? boxes : 0

    Rectangle {
        x: modelData.boundings[0]
        y: modelData.boundings[1]
        width: modelData.boundings[2] - modelData.boundings[0]
        height: modelData.boundings[3] - modelData.boundings[1]

        radius: 6
        color: "black"
    }
}