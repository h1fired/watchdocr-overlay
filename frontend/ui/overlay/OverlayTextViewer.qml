import QtQuick
import App.Backend
import "qrc:/qml/ui/common/controls"

Rectangle {
    id: root

    property bool extended: false
    property int dragMargin: 16
    readonly property int minimumWidth: 72
    readonly property int minimumHeight: 72
    readonly property bool dragging: mouse.drag.active || mouseResize.drag.active
    signal closeRequested()

    clip: true

    x: dragMargin
    y: dragMargin

    implicitWidth: 500
    implicitHeight: 120

    radius: 15
    color: Qt.rgba(0.024, 0.024, 0.024, 0.7)
    border.width: 1
    border.color: (
        mouse.containsMouse || mouse.drag.active ||
        mouseResize.containsMouse || mouseResize.drag.active
    )
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

        visible: root.extended
        enabled: root.extended

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

    OButton {
        width: 20
        height: 20

        visible: root.extended
        enabled: root.extended

        anchors.right: parent.right
        anchors.bottom: parent.bottom

        icon.source: "qrc:/qml/resources/icons/resize_angle.svg"
        icon.width: 16
        icon.height: 16
        icon.color: "#414141"

        background: Item {}

        MouseArea {
            id: mouseResize

            property point startPos: Qt.point(0, 0)

            anchors.fill: parent

            hoverEnabled: true
            cursorShape: Qt.SizeFDiagCursor

            onPressed: {
                startPos = Qt.point(mouseX, mouseY);
            }

            onMouseXChanged: {
                if (!pressed)
                    return

                let expWidth = root.width + mouseX - startPos.x;
                if (expWidth < root.minimumWidth)
                    expWidth = root.minimumWidth;

                let maxWidth = root.parent.width - root.x - root.dragMargin;
                expWidth = clampTo(expWidth, 0, maxWidth);

                root.width = expWidth;
            }

            onMouseYChanged: {
                if (!pressed)
                    return

                let expHeight = root.height + mouseY - startPos.y;
                if (expHeight < root.minimumHeight)
                    expHeight = root.minimumHeight;

                let maxHeight = root.parent.height - root.y - root.dragMargin;
                expHeight = clampTo(expHeight, 0, maxHeight);

                root.height = expHeight;
            }

            function clampTo(value, min, max) {
                return Math.min(Math.max(value, min), max);
            }
        }
    }

    OButton {
        id: btnClose

        visible: root.extended

        width: 28
        height: 28

        anchors.top: parent.top
        anchors.topMargin: 8
        anchors.right: parent.right
        anchors.rightMargin: 8

        icon.source: "qrc:/qml/resources/icons/close.svg"
        icon.width: 12
        icon.height: 12
        icon.color: "#E2E2E2"

        background: Item {}

        onClicked: root.closeRequested()
    }

    function clear() {
        text.text = "";
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
