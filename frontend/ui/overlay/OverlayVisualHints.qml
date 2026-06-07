import QtQuick
import App.Backend


Item {
    id: root

    property bool boxesVisible: false
    property var _boxes: ([])
    property point offset: Qt.point(0, 0)
    property int _expand: 4

    Item {
        visible: root.boxesVisible

        anchors.fill: parent

        Repeater {
            model: root._boxes

            Rectangle {
                x: modelData[1][0] + root.offset.x - root._expand
                y: modelData[1][1] + root.offset.y - root._expand
                width: modelData[1][2] - modelData[1][0] + root._expand
                height: modelData[1][3] - modelData[1][1] + root._expand

                Text {
                    anchors.fill: parent

                    text: modelData[0]
                    fontSizeMode: Text.Fit
                    font.pixelSize: height
                    font.weight: 600
                    minimumPixelSize: 6
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
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