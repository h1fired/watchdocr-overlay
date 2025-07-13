import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Shapes 2.15


Item {
    id: root
    width: 800
    height: 600

    property point startPoint: Qt.point(0, 0)
    property point endPoint: Qt.point(0, 0)
    property rect box: Qt.rect(0, 0, 0, 0)
    property rect absoluteBox: Qt.rect(0, 0, 0, 0)
    property bool animationEnabled: false

    Rectangle {
        id: selectionRect
        color: "transparent"
        border.color: "#664CFF"
        border.width: 1
        radius: 6

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
        }

        onPositionChanged: (event) => {
            endPoint = Qt.point(event.x, event.y)
            if (isValidPoints(startPoint, endPoint)) {
                root.box = root.calculateArea(root.startPoint, root.endPoint)
                root.repaintArea()
            }
        }

        onReleased: (event) => {
            endPoint = Qt.point(event.x, event.y)
            if (isValidPoints(startPoint, endPoint)) {
                root.box = root.calculateArea(root.startPoint, root.endPoint)
                root.absoluteBox = root.calculateArea(root.startPoint, root.endPoint, true)
                root.repaintArea()
            }
        }
    }

    function isValidPoints(p1, p2) {
        return (Math.abs(endPoint.x - startPoint.x) > 0 && Math.abs(endPoint.y - startPoint.y) > 0)
    }

    function calculateArea(p1, p2, absolute=false) {
        if (absolute) {
            p1 = root.mapToGlobal(p1)
            p2 = root.mapToGlobal(p2)
        }
        var x = Math.min(p1.x, p2.x)
        var y = Math.min(p1.y, p2.y)
        var w = Math.abs(p2.x - p1.x)
        var h = Math.abs(p2.y - p1.y)
        return Qt.rect(x, y, w, h)
    }

    function repaintArea() {
        selectionRect.x = Math.min(startPoint.x, endPoint.x) - 1
        selectionRect.y = Math.min(startPoint.y, endPoint.y) - 1
        selectionRect.width = Math.abs(endPoint.x - startPoint.x) + 2
        selectionRect.height = Math.abs(endPoint.y - startPoint.y) + 2
    }

    function clear() {
        startPoint = Qt.point(0, 0)
        endPoint = Qt.point(0, 0)
        box = Qt.rect(0, 0, 0, 0)
        absoluteBox = Qt.rect(0, 0, 0, 0)
        repaintArea()
    }
}
