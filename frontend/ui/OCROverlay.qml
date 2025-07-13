import QtQuick 2.15
import QtQuick.Window 2.15
import "components" as Componenets


Item {
    id: root

    // Controls
    enum Mode {
        Selection = 0,
        Recognizing = 1,
        Result = 2,
        StandBy = 3
    }
    property int qtMode: ocroverlaymodel.mode
    property int mode: OCROverlay.Mode.StandBy
    property string text: ocroverlaymodel.text

    onModeChanged: {
        if (mode == OCROverlay.Mode.StandBy) {
            selectionArea.clear()
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

    // UI
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

        Componenets.SelectionArea {
            id: selectionArea
            anchors.fill: parent

            onBoxChanged: {
                canvas.requestPaint();
            }

            onBoxReleased: {
                var absoluteBox = selectionArea.relativeToAbsoluteBox(selectionArea.box);
                ocroverlaymodel.QMLareaSelected(absoluteBox);
            }
        }

        Componenets.ControlToolBar {
            anchors.topMargin: 8
            anchors.top: parent.top
            anchors.horizontalCenter: parent.horizontalCenter

            onFullscreenSelected: {
                if (mode == OCROverlay.Mode.Recognizing || mode == OCROverlay.Mode.StandBy) {
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

        Componenets.OCRTextArea {
            id: textArea
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 24
            width: 560
            height: 120
            text: root.text
        }
    }
}
