import QtQuick 2.15


Item {
    id: root

    Rectangle {
        anchors.fill: parent
        color: "#000000"
        radius: 6
    }

    Text {
        anchors.fill: parent
        anchors.margins: 12
        id: textBlock

        color: "#FFFFFF"

        text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
        wrapMode: Text.WordWrap
        anchors.centerIn: parent
        font.pointSize: 12
        elide: Text.ElideRight
    }
}