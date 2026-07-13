import QtQuick
import App.Backend

Rectangle {
    id: root

    property int dragMargin: 16

    clip: true

    implicitWidth: 500
    implicitHeight: 120

    radius: 15
    color: Qt.rgba(0.024, 0.024, 0.024, 0.5)
    border.width: 1
    border.color: mouse.containsMouse || mouse.drag.active
        ? Qt.rgba(0.3, 0.3, 0.3, 1.0)
        : Qt.rgba(0.3, 0.3, 0.3, 0.0)

    Text {
        id: text

        width: parent.width - (anchors.margins * 2)
        height: Math.max(
            parent.height - (anchors.margins * 2),
            contentHeight
        )

        anchors.horizontalCenter: parent.horizontalCenter
        anchors.margins: 16
        anchors.bottom: parent.bottom

        font.family: "Segoe UI"
        font.weight: 600
        font.pixelSize: 14
        color: text !== "" ? "#E2E2E2" : "#060606"
        wrapMode: Text.WordWrap
    }

    MouseArea {
        id: mouse

        anchors.fill: parent

        hoverEnabled: true
        cursorShape: Qt.SizeAllCursor

        drag.target: parent
        drag.axis: Drag.XAndYAxis
        drag.minimumX: root.dragMargin
        drag.minimumY: root.dragMargin
        drag.maximumX: parent.parent.width - parent.width - root.dragMargin
        drag.maximumY: parent.parent.height - parent.height - root.dragMargin
    }

    Connections {
        target: Backend.Processor
        enabled: root.visible

        function onResultReceived(json) {
            let data = JSON.parse(json);
            text.text = data.translated_text;
        }
    }
}
