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

    property int qtMode: ocroverlaymodel.mode
    property string text: ocroverlaymodel.text
    property int mode: OCROverlay.Mode.StandBy
    signal closeRequested()

    onModeChanged: {
        if (mode == OCROverlay.Mode.StandBy) {
            selectionArea.clear();
            textArea.reset();
            canvas.requestPaint();
        }

        textArea.visible = (mode == OCROverlay.Mode.Result || mode == OCROverlay.Mode.Recognizing)
        selectionArea.animationEnabled = (mode == OCROverlay.Mode.Recognizing)
        selectionArea.enabled = (mode == OCROverlay.Mode.Selection || mode == OCROverlay.Mode.Result)
    }

    onVisibleChanged: {
        if (window.visible) {
            overlay.mode = OCROverlay.Mode.Selection
        } else {
            overlay.mode = OCROverlay.Mode.StandBy
        }
    }

    onQtModeChanged: {
        mode = qtMode
    }

    Connections {
        target: ocroverlaymodel

        function onTextCopied() {
            textArea.runCopied();
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
            if (root.mode == OCROverlay.Mode.Recognizing || root.mode == OCROverlay.Mode.StandBy) {
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
            opacity: 0.4
            anchors.fill: parent
            onPaint: {
                var ctx = getContext("2d");
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
            text: root.text
        }

        Button {
            id: btnClose

            width: 48
            height: 48
            anchors.right: parent.right
            background: Rectangle {
                color: "transparent"
            }
            icon.source: "../../resources/icons/close.svg"
            icon.color: "#868686"
            icon.width: 16
            icon.height: 16

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
