import QtQuick 2.15


import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root
    width: 800
    height: 600

    property bool selecting: false
    property point startPoint: Qt.point(0, 0)
    property point endPoint: Qt.point(0, 0)

    Rectangle {
        id: selectionRect
        color: "#21223140"
        border.color: "#664CFF"
        border.width: 1
        radius: 3
        visible: selecting

        x: Math.min(startPoint.x, endPoint.x)
        y: Math.min(startPoint.y, endPoint.y)
        width: Math.abs(endPoint.x - startPoint.x)
        height: Math.abs(endPoint.y - startPoint.y)
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        onPressed: (event) => {
            startPoint = Qt.point(event.x, event.y)
            endPoint = startPoint
            selecting = true
        }

        onPositionChanged: (event) => {
            if (selecting) {
                endPoint = Qt.point(event.x, event.y)
            }
        }

        onReleased: (event) => {
            endPoint = Qt.point(event.x, event.y)
            selecting = false

            console.log("Selection area:", 
                        selectionRect.x, selectionRect.y, 
                        selectionRect.width, selectionRect.height)
        }
    }
}
