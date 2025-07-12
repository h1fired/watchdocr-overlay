import QtQuick 2.15
import QtQuick.Window 2.15
import "components"


Window {
    visible: true
    width: 640
    height: 480
    title: "OCR Overlay"

    Rectangle {
        anchors.fill: parent
        color: "#111111"

        SelectionArea {
            anchors.fill: parent
        }

        ControlToolBar {
            anchors.topMargin: 8
            anchors.top: parent.top
            anchors.horizontalCenter: parent.horizontalCenter
            items: [
                {
                    "id": "fullscreen",
                    "text": "",
                    "icon": "../../resources/icons/fullscreen.svg"
                },
                {
                    "id": "selection",
                    "text": "",
                    "icon": "../../resources/icons/selection.svg"
                },
            ]
        }

        OCRTextArea {
            width: 560
            height: 120

            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 24
        }
    }
}
