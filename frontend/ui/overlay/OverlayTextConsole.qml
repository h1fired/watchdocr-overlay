import QtQuick
import QtQuick.Layouts
import QtQuick.Controls.Basic
import App.Backend
import "../common/controls"
import "components"


Rectangle {
    id: root

    width: 500
    height: 180

    radius: 12
    color: "#070B14"
    border.width: 1
    border.color: "#21242D"

    MouseArea {
        anchors.fill: parent
    }

    ColumnLayout {
        id: column

        anchors.fill: parent

        spacing: 4

        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 40

            RowLayout {
                anchors.fill: parent
                anchors.margins: 6
                anchors.leftMargin: 16

                spacing: 0

                TextConsoleStatus {
                    id: textConsoleStatus
                }

                Item {
                    Layout.fillWidth: true
                }

                AccuracyBar {
                    id: accuracyBar

                    Layout.fillHeight: true
                    Layout.rightMargin: 8
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
                        ? "../../../resources/icons/maximize.svg"
                        : "../../../resources/icons/minimize.svg"
                    )
                    icon.color: hovered ? "#94A3B8" : "#475569"
                    icon.width: 16
                    icon.height: 16

                    background: Rectangle {
                        color: parent.hovered ? "#1B1E28" : "transparent"
                        radius: 6
                    }

                    onClicked: {
                        root.height = (root.height === 180 ? 320 : 180);
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

                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AlwaysOn

                    contentItem: Rectangle {
                        implicitWidth: 6
                        color: parent.pressed ? "#21242D" : "#21242D"
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
                    color: "#FAF9FF"
                    wrapMode: Text.WordWrap
                }

            }
        }

        Item {
            Layout.fillWidth: true
            height: 36

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                anchors.bottomMargin: 4

                TranslationInfo {
                    Layout.fillHeight: true
                }

                Item {
                    Layout.fillWidth: true
                }

                Text {
                    Layout.alignment: Qt.AlignVCenter

                    text: "None  ·  None"

                    font.family: "Segoe UI"
                    font.weight: 500
                    font.pixelSize: 12
                    color: "#475569"
                }
            }
        }
    }

    // Backend
    Connections {
        target: Backend.Processor

        function onResultReceived(json) {
            let data = JSON.parse(json);
            accuracyBar.accuracy = data.confidence
            responseTextEdit.text = data.translated_text;
        }

        function onRecognizerStatusChanged(status) {
            if (status === 0) {
                textConsoleStatus.state = "idle";
            } else if (status === 1) {
                textConsoleStatus.state = "processing";
            }
        }
    }
}