import QtQuick
import QtQuick.Layouts
import QtQuick.Controls.Basic
import App.Backend
import "qrc:/qml/ui/common/controls"

Item {
    id: root

    property var section: null

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 44
            Layout.leftMargin: 16
            Layout.rightMargin: 12

            OText {
                Layout.fillWidth: true
                text: root.section?.title ?? ""
                font.weight: 700
                font.pixelSize: 13
                color: "#f1f1f1"
                elide: Text.ElideRight
            }

            OButton {
                id: btnReset

                visible: root.section !== null
                implicitWidth: resetText.implicitWidth + 20
                implicitHeight: 24

                ToolTip.visible: hovered
                ToolTip.delay: 600
                ToolTip.text: "Reset this section to defaults"

                contentItem: OText {
                    id: resetText
                    text: "Reset"
                    font.pixelSize: 11
                    color: btnReset.hovered ? "#d4d4d4" : "#8a8a8a"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }

                background: Rectangle {
                    radius: 6
                    color: btnReset.hovered ? "#262626" : "transparent"
                    border.width: 1
                    border.color: "#2C2C2C"
                }

                onClicked: Backend.Settings.resetSection(root.section.id)
            }
        }

        ListView {
            id: fieldsList

            Layout.fillWidth: true
            Layout.fillHeight: true

            clip: true
            boundsBehavior: Flickable.StopAtBounds

            model: root.section ? root.section.fields : []

            delegate: ColumnLayout {
                id: fieldItem

                required property var modelData
                required property int index

                readonly property bool showHeader: modelData.header !== "" && (
                    index === 0 || fieldsList.model[index - 1].header !== modelData.header)

                width: ListView.view.width
                spacing: 0

                OText {
                    Layout.fillWidth: true
                    Layout.topMargin: 10
                    Layout.bottomMargin: 4
                    Layout.leftMargin: 16
                    visible: fieldItem.showHeader

                    text: fieldItem.modelData.header.toUpperCase()

                    font.weight: 700
                    font.pixelSize: 9
                    font.letterSpacing: 1.2
                    color: "#4d4d4d"
                }

                SettingsFieldRow {
                    Layout.fillWidth: true
                    field: fieldItem.modelData
                    owner: root.section.owner
                }
            }

            footer: Item {
                width: ListView.view.width
                height: 12
            }

            ScrollBar.vertical: ScrollBar {
                id: scrollBar

                policy: ScrollBar.AsNeeded

                contentItem: Rectangle {
                    implicitWidth: 4
                    radius: 2
                    color: "#3a3a3a"
                    opacity: scrollBar.size < 1.0 ? (scrollBar.active ? 1.0 : 0.5) : 0.0

                    Behavior on opacity {
                        NumberAnimation { duration: 150 }
                    }
                }
            }
        }
    }
}
