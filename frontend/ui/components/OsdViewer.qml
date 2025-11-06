import QtQuick


Item {
    id: root

    property rect contentRect: Qt.rect(0, 0, 0, 0)
    property var objects: []

    Repeater {
        model: root.objects

        Rectangle {
            x: modelData[1][0] + root.contentRect.x - 12
            y: modelData[1][1] + root.contentRect.y - 12

            width: modelData[1][2] - modelData[1][0] + 4
            height: modelData[1][3] - modelData[1][1] + 4

            border.width: 1
            border.color: "black"
            color: "green"

            Text {
                anchors.fill: parent

                padding: 0
                leftPadding: 4

                text: modelData[0]
                color: "white"


                font.family: "Roboto"
                font.weight: 600
                fontSizeMode: Text.Fit
                font.pixelSize: 1200
                minimumPixelSize: 12
            }
        }
    }
}
