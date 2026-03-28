import QtQuick
import QtQuick.Layouts
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

                TextConsoleStatus {}

                Item {
                    Layout.fillWidth: true
                }

                AccuracyBar {
                    Layout.fillHeight: true
                    Layout.rightMargin: 8
                }

                CopyButton {
                    Layout.fillHeight: true
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

                TextEdit {
                    id: responseTextEdit

                    anchors.fill: parent
                    anchors.leftMargin: 16
                    anchors.rightMargin: 16

                    readOnly: true

                    text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec elementum, odio at pretium cursus, magna massa porttitor nunc, a imperdiet massa tellus sed eros. Integer justo ex, fermentum quis magna eu, fringilla ornare libero. Quisque ornare sed elit sed cursus. Vivamus quis enim mi. Suspendisse blandit velit ut ipsum sodales ultrices. Duis nec odio dapibus, volutpat turpis sit amet, sollicitudin enim. Nam euismod non dui ac maximus. Interdum et malesuada fames ac ante ipsum primis in faucibus. Aenean non ipsum a risus consequat consequat at ut mi."
                
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

        function onTextResultReceived(text) {
            responseTextEdit.text = text;
        }
    }
}