import QtQuick 2.15
import QtQuick.Window 2.15
import "components"


Item {
    id: root

    // Controls
    property var modes: ["selection", "recognizing", "result"]
    property string mode: modes[0]


    // UI
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
            visible: mode == "result"

            width: 560
            height: 120

            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 24
        }
    }

}