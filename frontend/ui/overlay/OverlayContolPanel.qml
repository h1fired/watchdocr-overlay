import QtQuick
import QtQuick.Layouts
import "../common/controls"
import "components"


Rectangle {
    id: root

    radius: 12
    color: "#070B14"
    border.width: 1
    border.color: "#21242D"

    implicitWidth: row.implicitWidth + (row.anchors.leftMargin * 2)

    RowLayout {
        id: row

        anchors.fill: parent
        anchors.margins: 6
        anchors.leftMargin: 12
        anchors.rightMargin: 12

        ActivityBar {
            Layout.fillHeight: true
            Layout.topMargin: 4
            Layout.bottomMargin: 4
        }

        Rectangle {
            width: 2

            Layout.fillHeight: true
            Layout.topMargin: 8
            Layout.bottomMargin: 8

            color: "#1A1C26"
        }

        TranslationSelector {
            Layout.fillHeight: true
            Layout.topMargin: 4
            Layout.bottomMargin: 4
        }

        Rectangle {
            width: 2

            Layout.fillHeight: true
            Layout.topMargin: 8
            Layout.bottomMargin: 8

            color: "#1A1C26"
        }

        OButton {
            id: btnPlayPause

            Layout.preferredWidth: 80
            Layout.fillHeight: true

            text: "Play"
            font.family: "Segoe UI"
            font.weight: 700
            font.pixelSize: 12

            icon.color: "#FAF9FF"
            icon.width: 12
            icon.height: 12

            background: Rectangle {
                color: parent.hovered ? "#7C3AED" : "#8B5CF6"
                radius: 6
            }

            state: "run"
            states: [
                State {
                    name: "run"
                    PropertyChanges {
                        target: btnPlayPause
                        text: "Run"
                        icon.source: "../../../resources/icons/play.svg"
                    }
                },
                State {
                    name: "pause"
                    PropertyChanges {
                        target: btnPlayPause
                        text: "Pause"
                        icon.source: "../../../resources/icons/pause.svg"
                    }
                }
            ]
        }

        Rectangle {
            width: 2

            Layout.fillHeight: true
            Layout.topMargin: 8
            Layout.bottomMargin: 8

            color: "#1A1C26"
        }

        OButton {
            Layout.fillHeight: true
            Layout.preferredWidth: height

            icon.source: "../../../resources/icons/selection.svg"
            icon.color: hovered ? "#94A3B8" : "#475569"
            icon.width: 22
            icon.height: 22

            background: Rectangle {
                color: parent.hovered ? "#1B1E28" : "transparent"
                radius: 6
            }
        }

        Rectangle {
            width: 2

            Layout.fillHeight: true
            Layout.topMargin: 8
            Layout.bottomMargin: 8

            color: "#1A1C26"
        }

        OButton {
            Layout.fillHeight: true
            Layout.preferredWidth: height

            icon.source: "../../../resources/icons/settings.svg"
            icon.color: hovered ? "#94A3B8" : "#475569"
            icon.width: 22
            icon.height: 22

            background: Rectangle {
                color: parent.hovered ? "#1B1E28" : "transparent"
                radius: 6
            }
        }

        Item {
            Layout.fillWidth: true
        }
    }

}
