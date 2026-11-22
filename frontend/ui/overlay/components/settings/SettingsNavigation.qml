import QtQuick
import QtQuick.Layouts
import "qrc:/qml/ui/common/controls"

// List of Settings Sections, app ones first, then the plugin ones
ListView {
    id: root

    property string currentSectionId: ""
    signal sectionSelected(string sectionId)

    clip: true
    boundsBehavior: Flickable.StopAtBounds
    topMargin: 8
    bottomMargin: 8
    spacing: 2

    delegate: ColumnLayout {
        id: navItem

        required property var modelData
        required property int index

        readonly property bool selected: modelData.id === root.currentSectionId
        readonly property bool firstPlugin: modelData.plugin && (
            index === 0 || !root.model[index - 1].plugin)

        width: ListView.view.width
        spacing: 0

        OText {
            Layout.fillWidth: true
            Layout.topMargin: 12
            Layout.bottomMargin: 4
            Layout.leftMargin: 18
            visible: navItem.firstPlugin

            text: "PLUGINS"

            font.weight: 700
            font.pixelSize: 9
            font.letterSpacing: 1.2
            color: "#4d4d4d"
        }

        Item {
            Layout.fillWidth: true
            implicitHeight: 32

            Rectangle {
                anchors.fill: parent
                anchors.leftMargin: 8
                anchors.rightMargin: 8
                radius: 6
                color: navItem.selected
                    ? "#2A2A2A"
                    : itemHover.containsMouse ? "#202020" : "transparent"
            }

            OText {
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.leftMargin: 18
                anchors.rightMargin: 18

                text: navItem.modelData.title
                font.pixelSize: 12
                font.weight: navItem.selected ? 600 : 400
                color: navItem.selected ? "#f1f1f1" : "#8a8a8a"
                elide: Text.ElideRight
            }

            MouseArea {
                id: itemHover

                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor

                onClicked: root.sectionSelected(navItem.modelData.id)
            }
        }
    }
}
