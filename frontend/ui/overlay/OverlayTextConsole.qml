import QtQuick
import QtQuick.Layouts
import QtQuick.Controls.Basic
import App.Backend
import "qrc:/qml/ui/common/controls"
import "qrc:/qml/ui/overlay/components"

Rectangle {
    id: root

    property bool enableSizeAdaptivity: false
    property TranslationInfo translationInfo: translationInfo
    property string ocrProvider: Backend.Ocr.providerName
    property string translatorProvider: Backend.Translation.providerName

    width: 500
    height: 180

    radius: 15
    color: "#060606"

    MouseArea {
        anchors.fill: parent
    }

    ColumnLayout {
        id: column

        anchors.fill: parent

        spacing: 4

        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 44

            RowLayout {
                anchors.fill: parent
                anchors.margins: 6
                anchors.leftMargin: 16

                spacing: 0

                TranslationInfo {
                    id: translationInfo

                    Layout.fillHeight: true
                }

                Item {
                    Layout.fillWidth: true
                }

                CopyButton {
                    Layout.fillHeight: true

                    onCopied: {
                        Backend.Utils.copyTextToClipboard(responseTextEdit.text);
                    }
                }

                OButton {
                    Layout.fillHeight: true
                    Layout.preferredWidth: height

                    icon.source: (
                        root.height === 180
                        ? "qrc:/qml/resources/icons/maximize.svg"
                        : "qrc:/qml/resources/icons/minimize.svg"
                    )
                    icon.color: "#D2D2D2"
                    icon.width: 18
                    icon.height: 18

                    background: Rectangle {
                        color: parent.hovered ? "#292929" : "transparent"
                        radius: 6
                    }

                    onClicked: {
                        root.width = (root.width === 500 ? 720 : 500);
                        root.height = (root.height === 180 ? 340 : 180);
                    } 
                }
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            Flickable {
                id: responseFlickable

                anchors.fill: parent

                contentHeight: Math.max(responseTextEdit.implicitHeight, height)

                clip: true
                boundsBehavior: Flickable.StopAtBounds

                Behavior on contentY {
                    SmoothedAnimation { velocity: 300; easing.type: Easing.InOutQuad }
                }

                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AlwaysOn

                    contentItem: Rectangle {
                        implicitWidth: 6
                        color: parent.pressed ? "#2c2c2c" : "#2c2c2c"
                        opacity: parent.active ? 1.0 : 0.5

                        Behavior on opacity {
                            NumberAnimation { duration: 200 }
                        }
                    }
                }

                TextEdit {
                    id: responseTextEdit

                    anchors.fill: parent
                    anchors.leftMargin: 16
                    anchors.rightMargin: 16

                    readOnly: true

                    font.family: "Segoe UI"
                    font.weight: 600
                    font.pixelSize: 14
                    color: text !== "" ? "#FAF9FF" : "#060606"
                    wrapMode: Text.WordWrap

                    TextConsoleResponseLoader {
                        id: textConsoleResponseLoader

                        visible: state === "processing"
                        opacity: visible ? 1 : 0

                        Behavior on opacity {
                            NumberAnimation {
                                duration: 200
                                easing.type: Easing.InOutQuad
                            }
                        }
                    }

                    onVisibleChanged: {
                        if (!visible) {
                            root.width = 500;
                            root.height = 180;
                        }
                    }

                    Behavior on color {
                        ColorAnimation {
                            duration: 200
                            easing.type: Easing.InOutQuad
                        }
                    }

                    onCursorRectangleChanged: {
                        // Auto-scroll Flickable to keep the selection cursor visible
                        let cursorBottom = cursorRectangle.y + cursorRectangle.height;
                        let cursorTop    = cursorRectangle.y;
                        let visibleTop   = responseFlickable.contentY;
                        let visibleBottom = visibleTop + responseFlickable.height;

                        if (cursorBottom > visibleBottom) {
                            responseFlickable.contentY = cursorBottom - responseFlickable.height;
                        } else if (cursorTop < visibleTop) {
                            responseFlickable.contentY = cursorTop;
                        }
                    }

                    function isOverflowing() {
                        return contentHeight > responseFlickable.height;
                    }
                }

            }
        }
    }

    Behavior on width {
        NumberAnimation { duration: 200; easing.type: Easing.InOutQuad }
    }

    Behavior on height {
        NumberAnimation { duration: 200; easing.type: Easing.InOutQuad }
    }

    // Backend
    Connections {
        target: Backend.Processor

        function onResultReceived(json) {
            let data = JSON.parse(json);
            responseTextEdit.text = data.translated_text;

            if (root.enableSizeAdaptivity && responseTextEdit.isOverflowing()) {
                root.width = 720;
                root.height = 340;
            }
        }

        function onRecognizerStatusChanged(status) {
            if (status === 0) {
                textConsoleResponseLoader.state = "idle";
            } else if (status === 1) {
                textConsoleResponseLoader.state = "processing";
                responseTextEdit.text = "";
            }
        }
    }
}