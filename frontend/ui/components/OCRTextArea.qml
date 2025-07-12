import QtQuick 2.15


Item {
    id: root
    property string text

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

        text: root.text
        wrapMode: Text.WordWrap
        anchors.centerIn: parent
        font.pointSize: 10
        elide: Text.ElideRight
    }
}