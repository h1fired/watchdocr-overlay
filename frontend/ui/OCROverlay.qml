import QtQuick
import QtQuick.Window
import QtQuick.Controls.Basic
import App.Backend
import "components" as Components


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
            if (debugPanel.previewEnabled) {
                Backend.Preview.QmlRequestScreensPreviewImage();
            }
            root.mode = OCROverlay.Mode.Selection
        } else {
            root.mode = OCROverlay.Mode.StandBy
        }
    }

    Components.ScreenPreview {
        id: screensPreview

        anchors.fill: parent

        providerId: "preview_screens"
    }

    Components.OsdViewer {
        id: osdViewer

        anchors.fill: parent

        visible: root.mode === OCROverlay.Mode.Result && debugPanel.osbEnabled

        contentRect: selectionArea.box
    }

    Components.SelectionArea {
        id: selectionArea

        anchors.fill: parent

        enabled: (
            root.mode == OCROverlay.Mode.Selection ||
            root.mode == OCROverlay.Mode.Result ||
            root.mode == OCROverlay.Mode.Selecting
        )
        loading: root.mode == OCROverlay.Mode.Recognizing
    }

    Components.ScreenArea {
        monitor: 0

        Rectangle {
            id: rootRect

            anchors.fill: parent

            color: "transparent"

            Components.ControlToolBar {
                id: controlToolBar

                anchors.topMargin: 8
                anchors.top: parent.top
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Components.TextControlPanel {
                id: textControlPanel

                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 24

                visible: (
                    root.mode == OCROverlay.Mode.Result ||
                    root.mode == OCROverlay.Mode.Recognizing
                )

                sourceLanguages: Backend.Translate.sourceLanguages
                targetLanguages: Backend.Translate.targetLanguages
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

        DebugPanel {
            id: debugPanel

            x: 0
            y: 0
            width: 400

            onPreviewEnabledChanged: {
                screensPreview.visible = previewEnabled;
            }
        }
    }

    Connections {
        target: Backend.Preview

        function onPreviewUpdated() {
            screensPreview.update();
        }
    }

    Connections {
        target: Backend.OcrTranslate

        function onResponseReceived(response) {
            let text = response.text;

            if (response.state == OCROverlay.ResponseStatus.Success) {
                textControlPanel.state = "result"
                root.mode = OCROverlay.Mode.Result;
            } else if (response.state == OCROverlay.ResponseStatus.Error) {
                textControlPanel.state = "status"
                root.mode = OCROverlay.Mode.Result;
                text = "<span style=\"color:red\">" + response.text + "</span>";
            } else if (response.state == OCROverlay.ResponseStatus.Recognizing) {
                root.mode = OCROverlay.Mode.Recognizing;
                textControlPanel.maximized = false;
                textControlPanel.state = "status"
            }
            textControlPanel.text = text;
            textControlPanel.loading = response.state == OCROverlay.ResponseStatus.Recognizing;
        }

        function onDetailsReceived(details) {
            osdViewer.objects = JSON.parse(details);
        }
    }

    Connections {
        target: Backend.System

        function onTextCopiedToClipboard() {
            textControlPanel.runCopied();
        }
    }

    Connections {
        target: selectionArea

        function onBoxReleased() {
            let absoluteBox = selectionArea.relativeToAbsoluteBox(selectionArea.box);
            let sourceLanguage = textControlPanel.sourceLanguage;
            let targetLanguage = textControlPanel.targetLanguage;
            Backend.OcrTranslate.translateArea(absoluteBox, sourceLanguage, targetLanguage);
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
            let absoluteBox = selectionArea.relativeToAbsoluteBox(selectionArea.box);
            let sourceLanguage = textControlPanel.sourceLanguage;
            let targetLanguage = textControlPanel.targetLanguage;
            Backend.OcrTranslate.translateArea(absoluteBox, sourceLanguage, targetLanguage);
        }
    }

    Connections {
        target: textControlPanel

        function onCopied() {
            Backend.System.copyTextToClipboard(textControlPanel.text);
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
        textControlPanel.reset();
    }

}
