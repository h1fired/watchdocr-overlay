import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Shapes 2.15


Item {
    id: root
    width: 800
    height: 600

    property bool selecting: false
    property point startPoint: Qt.point(0, 0)
    property point endPoint: Qt.point(0, 0)
    property bool animationEnabled: false
    property rect box: Qt.rect(0, 0, 0, 0)

    Rectangle {
        id: selectionRect
        color: "#21223140"
        border.color: "#664CFF"
        border.width: 1
        radius: 6
        visible: selecting

        x: Math.min(startPoint.x, endPoint.x)
        y: Math.min(startPoint.y, endPoint.y)
        width: Math.abs(endPoint.x - startPoint.x)
        height: Math.abs(endPoint.y - startPoint.y)

        Rectangle {
            id: selectionRectGradient
            visible: animationEnabled
            anchors.fill: parent
            radius: 6

            property var gradientPos: 0.0

            gradient: Gradient {
                orientation: Qt.Horizontal
                GradientStop {
                    position: selectionRectGradient.gradientPos - 1.0;
                    color: Qt.rgba(0.4, 0.298, 1.0, 0.0)
                }
                GradientStop {
                    position: selectionRectGradient.gradientPos
                    color: Qt.rgba(0.4, 0.298, 1.0, 0.3)
                }
                GradientStop {
                    position: selectionRectGradient.gradientPos + 1.0;
                    color: Qt.rgba(0.4, 0.298, 1.0, 0.0)
                }
            }

            NumberAnimation on gradientPos {
                from: -1.0
                to: 2.0
                duration: 1500
                loops: Animation.Infinite
                easing.type: Easing.InOutQuad
                running: root.animationEnabled
            }
        }

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
            // selecting = false

            var x = Math.min(root.startPoint.x, root.endPoint.x)
            var y = Math.min(root.startPoint.y, root.endPoint.y)
            var w = Math.abs(root.endPoint.x - root.startPoint.x)
            var h = Math.abs(root.endPoint.y - root.startPoint.y)
            root.box = Qt.rect(x, y, w, h)
        }
    }
}
