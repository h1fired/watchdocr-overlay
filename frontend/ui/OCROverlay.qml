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
    property int mode: ocroverlaymodel.mode
    property string text: ocroverlaymodel.text

    // UI
    Rectangle {
        anchors.fill: parent
        color: "transparent"

        Canvas {
            id: canvas
            opacity: 0.4
            anchors.fill: parent
            onPaint: {
                var ctx = getContext("2d");
                ctx.fillStyle = "black";

                // Draw a rectangle with a transparent hole
                ctx.beginPath();
                ctx.fillRect(0, 0, parent.width, parent.height); // Outer rectangle
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

        SelectionArea {
            id: selectionArea
            anchors.fill: parent
            enabled: root.mode != OCROverlay.Mode.Recognizing
            animationEnabled: root.mode == OCROverlay.Mode.Recognizing

            onAbsoluteBoxChanged: {
                ocroverlaymodel.QMLareaSelected(absoluteBox);
            }
            onBoxChanged: {
                canvas.requestPaint();
            }
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

            text: root.text
        }
    }

}