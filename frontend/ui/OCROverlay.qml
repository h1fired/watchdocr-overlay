import QtQuick 2.15
import QtQuick.Window 2.15
import "components"


Item {
    id: root

    // Controls
    enum Mode {
        Selection = 0,
        Recognizing = 1,
        Result = 2
    }
    property string mode: OCROverlay.Mode.Result

    // UI
    Rectangle {
        anchors.fill: parent
        color: "#111111"

        SelectionArea {
            anchors.fill: parent
            enabled: root.mode == OCROverlay.Mode.Selection
            animationEnabled: root.mode == OCROverlay.Mode.Recognizing
        }

        ControlToolBar {
            anchors.topMargin: 8
            anchors.top: parent.top
            anchors.horizontalCenter: parent.horizontalCenter
            items: [
                {
                    "id": "fullscreen",
                    "text": "",
                    "icon": "../../../resources/icons/fullscreen.svg"
                },
                {
                    "id": "selection",
                    "text": "",
                    "icon": "../../../resources/icons/selection.svg"
                },
            ]
        }

        OCRTextArea {
            visible: mode == OCROverlay.Mode.Result

            width: 560
            height: 120

            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 24
        }
    }

}