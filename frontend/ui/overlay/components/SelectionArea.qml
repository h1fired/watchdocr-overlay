import QtQuick
import QtQuick.Controls

Item {
    id: root

    readonly property alias box: objects.box
    property bool loading: false
    property bool selecting: selectionMouseArea.selecting && selectionBox.selecting
    signal boxSelected()

    Item {
        x: objects.box.x - 1
        y: objects.box.y - 1
        width: objects.box.width + 2
        height: objects.box.height + 2

        Rectangle {
            id: selectionRectGradient

            property var gradientPos: 0.0

            visible: root.loading

            anchors.fill: parent

            gradient: Gradient {
                orientation: Qt.Horizontal

                GradientStop {
                    position: selectionRectGradient.gradientPos - 1.0;
                    color: Qt.rgba(1.0, 1.0, 1.0, 0.0)
                }
                GradientStop {
                    position: selectionRectGradient.gradientPos
                    color: Qt.rgba(1.0, 1.0, 1.0, 0.3)
                }
                GradientStop {
                    position: selectionRectGradient.gradientPos + 1.0;
                    color: Qt.rgba(1.0, 1.0, 1.0, 0.0)
                }
            }

            NumberAnimation on gradientPos {
                from: -1.0
                to: 2.0
                duration: 1500
                loops: Animation.Infinite
                easing.type: Easing.InOutQuad
                running: root.loading
            }
        }
    }

    Canvas {
        id: canvas

        anchors.fill: parent

        opacity: 0.3

        onPaint: {
            let ctx = getContext("2d");
            ctx.fillStyle = "black";

            // Draw a rectangle with a transparent box
            ctx.beginPath();
            ctx.fillRect(0, 0, parent.width, parent.height);
            ctx.globalCompositeOperation = "destination-out";
            ctx.fillStyle = "black";
            ctx.fillRect(
                objects.box.x,
                objects.box.y,
                objects.box.width,
                objects.box.height,
            );
            ctx.globalCompositeOperation = "source-over";
        }
    }

    MouseArea {
        id: selectionMouseArea

        property point startPoint: Qt.point(0, 0)
        property point endPoint: Qt.point(0, 0)
        property bool selecting: false

        anchors.fill: parent

        cursorShape: Qt.CrossCursor

        onPressed: (event) => {
            startPoint = Qt.point(event.x, event.y);
            endPoint = startPoint;

            selecting = true;
        }

        onPositionChanged: (event) => {
            endPoint = Qt.point(event.x, event.y);
            objects.box = reformatRect(rectFromPoints(startPoint, endPoint));
            objects.boxUpdated();
   
            // Update selection box area
            selectionBox.updateArea(objects.box)
        }

        onReleased: (event) => {
            endPoint = Qt.point(event.x, event.y);
            root.boxSelected();

            selecting = false;
        }

        function reformatRect(rect) {
            if (rect.width <= 0)
                rect.width = 10;
            if (rect.height <= 0)
                rect.height = 10;
            return rect;
        }

        function rectFromPoints(p1, p2) {
            var x = Math.min(p1.x, p2.x);
            var y = Math.min(p1.y, p2.y);
            var w = Math.abs(p2.x - p1.x);
            var h = Math.abs(p2.y - p1.y);
            return Qt.rect(x, y, w, h);
        }
    }

    SelectionBox {
        id: selectionBox

        x: 0
        y: 0
        width: 0
        height: 0

        onBoxReleased: {
            objects.box.x = x;
            objects.box.y = y;
            objects.box.width = width;
            objects.box.height = height;

            root.boxSelected();
        }

        onBoxChanged: {
            objects.box.x = x;
            objects.box.y = y;
            objects.box.width = width;
            objects.box.height = height;

            objects.boxUpdated();
        }
    }

    QtObject {
        id: objects

        signal boxUpdated()
        property rect box: Qt.rect(0, 0, 0, 0)

        onBoxUpdated: {
            canvas.requestPaint();
        }
    }

    function relativeToAbsoluteBox(box) {
        var p = root.mapToGlobal(box.x, box.y);
        return Qt.rect(p.x, p.y, box.width, box.height);
    }

    function clear() {
        objects.box = Qt.rect(0, 0, 0, 0);
        selectionBox.updateArea(objects.box);
        canvas.requestPaint();
    }
}