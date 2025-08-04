import QtQuick
import QtQuick.Window
import QtQuick.Controls.Basic
import "components" as Components


Item {
    id: root

    enum Mode {
        Selection = 0,
        Recognizing = 1,
        Result = 2,
        StandBy = 3
    }

    enum ResponseStatus {
        Success = 0,
        Error = 1,
        Recognizing = 2
    }

    property int mode: OCROverlay.Mode.StandBy

    signal closeRequested()

    onModeChanged: {
        if (mode == OCROverlay.Mode.StandBy) {
            selectionArea.clear();
            textArea.reset();
            canvas.requestPaint();
        }
    }

    onVisibleChanged: {
        if (window.visible) {
            root.mode = OCROverlay.Mode.Selection
        } else {
            root.mode = OCROverlay.Mode.StandBy
        }
    }

    Connections {
        target: ocroverlaymodel

        function onTextCopied() {
            textArea.runCopied();
        }

        function onResponseReceived() {
            let response = ocroverlaymodel.QMLgetResponse();
            
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
        target: selectionArea

        function onBoxReleased() {
            var absoluteBox = selectionArea.relativeToAbsoluteBox(selectionArea.box);
            ocroverlaymodel.QMLareaSelected(absoluteBox);
        }

        function onBoxChanged() {
            canvas.requestPaint();
        }
    }

    Connections {
        target: controlToolBar

        function onFullscreenSelected() {
            if (
                root.mode == OCROverlay.Mode.Recognizing ||
                root.mode == OCROverlay.Mode.StandBy
            ) {
                return
            }
            selectionArea.selectBox(Qt.rect(
                root.x,
                root.y,
                root.width,
                root.height,
            ))
            var absoluteBox = selectionArea.relativeToAbsoluteBox(selectionArea.box);
            ocroverlaymodel.QMLareaSelected(absoluteBox);
        }
    }

    Connections {
        target: textArea

        function onCopied() {
            ocroverlaymodel.QMLtextCopied(textArea.text);
        }
    }

    Connections {
        target: btnClose

        function onClicked() {
            Window.close();
        }
    }

    Rectangle {
        id: rootRect

        anchors.fill: parent
        color: "transparent"

        Canvas {
            id: canvas

            anchors.fill: parent
    
            opacity: 0.4

            onPaint: {
                let ctx = getContext("2d");
                ctx.fillStyle = "black";

                // Draw a rectangle with a transparent box
                ctx.beginPath();
                ctx.fillRect(0, 0, parent.width, parent.height);
                ctx.globalCompositeOperation = "destination-out";
                ctx.fillStyle = "black";
                ctx.fillRect(
                    selectionArea.box.x,
                    selectionArea.box.y,
                    selectionArea.box.width,
                    selectionArea.box.height,
                );
                ctx.globalCompositeOperation = "source-over";
            }
        }

        Components.SelectionArea {
            id: selectionArea

            anchors.fill: parent

            enabled: {
                return (
                    root.mode == OCROverlay.Mode.Selection ||
                    root.mode == OCROverlay.Mode.Result
                )
            }
            animationEnabled: root.mode == OCROverlay.Mode.Recognizing
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

}
