import QtQuick
import QtQuick.Controls.Basic

MenuItem {
    id: root

    implicitHeight: 40

    contentItem: Text {
        text: parent.text
        color: highlighted ? "#ffffff" : "#bdbdbd"
        verticalAlignment: Text.AlignVCenter
        leftPadding: 8
    }

    background: Rectangle {
        radius: 6
        color: highlighted ? "#2f2f2f" : "transparent"
    }

    indicator: Item {
        anchors.fill: parent

        MouseArea {
            anchors.fill: parent

            cursorShape: Qt.PointingHandCursor

            onClicked: switchControl.checked = !switchControl.checked
        }

        OSwitch {
            id: switchControl

            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: 12

            onCheckedChanged: {
                root.checked = checked;
            }
        }
    }
}