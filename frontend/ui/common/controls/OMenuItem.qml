import QtQuick
import QtQuick.Controls.Basic

MenuItem {
    id: root

    implicitHeight: 40

    contentItem: Text {
        text: parent.text
        color: highlighted ? "#FFFFFF" : "#BDBDBD"
        verticalAlignment: Text.AlignVCenter
        leftPadding: 8
    }

    background: Rectangle {
        radius: 6
        color: highlighted ? "#2C2C2C" : "transparent"
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

            checked: root.checked

            onCheckedChanged: {
                root.checked = checked;
            }
        }
    }
}