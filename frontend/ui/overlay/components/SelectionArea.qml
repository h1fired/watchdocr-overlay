import QtQuick
import QtQuick.Controls
import "qrc:/qml/ui/common/controls"

Item {
    id: root

    readonly property alias box: objects.box
    property bool loading: false
    readonly property bool selecting: selectionMouseArea.selecting || selectionBox.selecting
    property bool mouseSelectionActive: false
    readonly property bool boxValid: !isNullRect(objects.box)
    signal boxSelected()

    Item {
        x: objects.box.x - 1
        y: objects.box.y - 1
        width: objects.box.width + 2
        height: objects.box.height + 2

        Rectangle {
            id: selectionRectGradient

            property var gradientPos: 0.0

            visible: root.loading && !root.selecting

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

    SelectionMouseArea {
        id: selectionMouseArea

        onBoxChanged: {
            selectionBox.updateArea(box);
        }

        onReleased: {
            selectionBox.boxReleased();
        }
    }

    SelectionBox {
        id: selectionBox

        visible: root.boxValid

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

    OButton {
        x: selectionBox.x + selectionBox.width - width + 4
        y: selectionBox.y - height - 6

        width: 20
        height: 20

        visible: (
            selectionBox.width >= selectionBox.minWidth &&
            selectionBox.height >= selectionBox.minHeight
        )

        background: Rectangle {
            color: "transparent"
            border.width: 1
            border.color: "#FFFFFF"
        }
        icon.source: "qrc:/qml/resources/icons/close.svg"
        icon.width: 12
        icon.height: 12
        display: AbstractButton.IconOnly

        onClicked: {
            root.clear();
            root.boxSelected();
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

    function isNullRect(r) {
        return r.x === 0 &&
               r.y === 0 &&
               r.width === 0 &&
               r.height === 0;
    }

    function clear() {
        objects.box = Qt.rect(0, 0, 0, 0);
        selectionBox.updateArea(objects.box);
        canvas.requestPaint();
    }
}