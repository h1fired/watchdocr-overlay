import QtQuick
import QtQuick.Window
import QtQuick.Controls.Basic
import "components" as Components
import App.Backend


Item {
    id: root

    enum Mode {
        StandBy = 0,
        Selection = 1,
        Selecting = 2,
        Sending = 3,
        Recognizing = 4,
        Result = 5
    }

    enum ResponseStatus {
        Error = 0,
        Success = 1,
        Recognizing = 2
    }

    property int mode: OCROverlay.Mode.StandBy

    signal closeRequested()

    onModeChanged: {
        if (mode == OCROverlay.Mode.StandBy) {
            root.clear();
        }
    }

    onVisibleChanged: {
        if (root.visible) {
            root.mode = OCROverlay.Mode.Selection
        } else {
            root.mode = OCROverlay.Mode.StandBy
        }
    }

    Rectangle {
        id: rootRect

        anchors.fill: parent

        color: "transparent"

        Components.MultiScreenSelectionArea {
            id: selectionArea

            anchors.fill: parent

            enabled: (
                root.mode == OCROverlay.Mode.Selection ||
                root.mode == OCROverlay.Mode.Result ||
                root.mode == OCROverlay.Mode.Selecting
            )
            loading: root.mode == OCROverlay.Mode.Recognizing
        }

        Components.ControlToolBar {
            id: controlToolBar

            anchors.topMargin: 8
            anchors.top: parent.top
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Components.OCRTextArea {
            id: textArea

            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 24

            visible: (
                root.mode == OCROverlay.Mode.Result ||
                root.mode == OCROverlay.Mode.Recognizing
            )
        }

        Button {
            id: btnClose

            width: 48
            height: 48

            anchors.right: parent.right

            background: Rectangle {
                color: "transparent"
            }
            icon {
                source: "../../resources/icons/close.svg"
                color: "#868686"
                width: 16
                height: 16
            }

            MouseArea {
                anchors.fill: parent

                cursorShape: Qt.PointingHandCursor 

                onPressed: (mouse) => {
                    mouse.accepted = false;
                    root.closeRequested();
                }
            }
        }
    }

    Connections {
        target: Backend.OcrTranslate

        function onResponseReceived(response) {
            if (response.state == OCROverlay.ResponseStatus.Success) {
                textArea.text = response.text;
                textArea.state = "result"
                root.mode = OCROverlay.Mode.Result;
            } else if (response.state == OCROverlay.ResponseStatus.Error) {
                textArea.status = response.text;
                textArea.state = "status"
                root.mode = OCROverlay.Mode.Result;
            } else if (response.state == OCROverlay.ResponseStatus.Recognizing) {
                root.mode = OCROverlay.Mode.Recognizing;
                textArea.status = response.text;
                textArea.maximized = false;
                textArea.state = "status"
            }
        }
    }

    Connections {
        target: Backend.System

        function onTextCopiedToClipboard() {
            textArea.runCopied();
        }
    }

    Connections {
        target: selectionArea

        function onBoxReleased() {
            var absoluteBox = selectionArea.relativeToAbsoluteBox(selectionArea.box);
            Backend.OcrTranslate.recognizeArea(absoluteBox);
        }

        function onPressed() {
            root.mode = OCROverlay.Mode.Selecting;
        }
    }

    Connections {
        target: controlToolBar

        function onFullscreenSelected() {
            if (
                root.mode == OCROverlay.Mode.Recognizing ||
                root.mode == OCROverlay.Mode.StandBy
            ) {
                return;
            }
            selectionArea.selectPrimaryScreenBox();
            var absoluteBox = selectionArea.relativeToAbsoluteBox(selectionArea.box);
            Backend.OcrTranslate.recognizeArea(absoluteBox);
        }
    }

    Connections {
        target: textArea

        function onCopied() {
            Backend.System.copyTextToClipboard(textArea.text);
        }
    }

    Connections {
        target: btnClose

        function onClicked() {
            Window.close();
        }
    }

    function clear() {
        selectionArea.clear();
        textArea.reset();
    }

}
