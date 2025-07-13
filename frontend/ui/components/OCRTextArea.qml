import QtQuick 2.15
import QtQuick.Controls.Basic 2.15


Item {
    id: root
    property string text

    ScrollView {
        id: scrollView
        anchors.fill: parent

        ScrollBar.horizontal: ScrollBar {
            policy: ScrollBar.AlwaysOff
        }
        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AsNeeded
            anchors.top: scrollView.top
            anchors.left: scrollView.right
            anchors.bottom: scrollView.bottom
            height: scrollView.availableHeight
            width: 12

            background: Rectangle {
                color: "#000000"
                topRightRadius: 6
                bottomRightRadius: 6
            }

            contentItem: Rectangle {
                implicitWidth: 4
                implicitHeight: 10
                anchors.leftMargin: 10

                radius: 16
                color: "#1F1F1F"
            }
        }
        background: Rectangle {
            color: "#000000"
            topLeftRadius: 6
            bottomLeftRadius: 6
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
}