import QtQuick 2.15
import QtQuick.Controls 2.15


Item {
    id: root

    width: 800
    height: 600

    property rect box: Qt.rect(0, 0, 0, 0)
    property bool animationEnabled: false
    property bool drawBorders: true

    signal boxReleased()
    signal pressed()

    MouseArea {
        anchors.fill: parent

        onPressed: (event) => {
            root.pressed();
            privates.startPoint = Qt.point(event.x, event.y);
            privates.endPoint = privates.startPoint;
        }

        onPositionChanged: (event) => {
            privates.endPoint = Qt.point(event.x, event.y);
            root.box = root._redesignRect(root.rectFromPoints(privates.startPoint, privates.endPoint));
        }

        onReleased: (event) => {
            privates.endPoint = Qt.point(event.x, event.y);
            root.box = root._redesignRect(root.rectFromPoints(privates.startPoint, privates.endPoint));
            root.boxReleased();
        }
    }

    Rectangle {
        visible: root.drawBorders

        x: root.box.x-1
        y: root.box.y-1
        width: root.box.width+2
        height: root.box.height+2

        color: "transparent"
        border.color: "#664CFF"
        border.width: 1

        Rectangle {
            id: selectionRectGradient

            anchors.fill: parent

            visible: root.animationEnabled

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

    QtObject {
        id: privates

        property point startPoint: Qt.point(0, 0)
        property point endPoint: Qt.point(0, 0)
    }

    function relativeToAbsoluteBox(box) {
        var p = root.mapToGlobal(box.x, box.y)
        return Qt.rect(p.x, p.y, box.width, box.height)
    }

    function rectFromPoints(p1, p2) {
        var x = Math.min(p1.x, p2.x)
        var y = Math.min(p1.y, p2.y)
        var w = Math.abs(p2.x - p1.x)
        var h = Math.abs(p2.y - p1.y)
        return Qt.rect(x, y, w, h)
    }

    function clear() {
        privates.startPoint = Qt.point(0, 0)
        privates.endPoint = Qt.point(0, 0)
        root.box = Qt.rect(0, 0, 0, 0)
    }

    function selectBox(rect) {
        root.box = rect
    }

    function _redesignRect(rect) {
        if (rect.width <= 0) {
            rect.width = 10
        }
        if (rect.height <= 0) {
            rect.height = 10
        }
        return rect
    }
}
