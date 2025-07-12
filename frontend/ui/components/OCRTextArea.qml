import QtQuick 2.15


Item {
    id: root
    property string text

    Rectangle {
        anchors.fill: parent
        color: "#000000"
        border.width: 1
        border.color: "#1F1F1F"
        radius: 6
    }

    Text {
        anchors.fill: parent
        anchors.margins: 12
        id: textBlock

        color: "#FFFFFF"

        text: root.text
        wrapMode: Text.WordWrap
        anchors.centerIn: parent
        font.pointSize: 10
        elide: Text.ElideRight
    }
}