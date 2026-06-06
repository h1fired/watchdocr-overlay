import QtQuick
import App.Backend


Item {
    id: root

    property bool boxesVisible: false
    property var _boxes: ([])
    property point offset: Qt.point(0, 0)

    Item {
        visible: root.boxesVisible

        anchors.fill: parent

        Repeater {
            model: root._boxes

            Rectangle {
                x: modelData[1][0] + root.offset.x - 12
                y: modelData[1][1] + root.offset.y - 12
                width: modelData[1][2] - modelData[1][0]
                height: modelData[1][3] - modelData[1][1]

                Text {
                    text: modelData[0]
                }
            }
        }
    }

    // Backend
    Connections {
        target: Backend.Processor

        function onResultReceived(json) {
            let data = JSON.parse(json);
            root._boxes = data.boxes;
            root.boxesVisible = true;
        }
    }
}