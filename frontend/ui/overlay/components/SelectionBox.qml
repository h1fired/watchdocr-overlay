import QtQuick

Item {
    id: root

    width: 0
    height: 0

    property int minWidth: 0
    property int minHeight: 0

    property color borderColor: "#80FFFFFF"
    property int borderWidth: 1
    property color cornerColor: "#FFFFFF"
    property int cornerThickness: 3
    property int cornerLength: 15
    property int handleSize: 24

    readonly property alias selecting: objects.selecting

    signal boxReleased()
    signal boxChanged()

    Rectangle {
        id: borderRect
        anchors.fill: parent
        color: "transparent"
        border.color: root.borderColor
        border.width: root.borderWidth
    }

    component ResizeHandle: Item {
        id: handle
        width: root.handleSize
        height: root.handleSize

        property int cursor: Qt.ArrowCursor
        property string direction // "tl", "t", "tr", "r", "br", "b", "bl", "l"
        property bool isCorner: false

        // L-shaped corner brackets
        Rectangle {
            // Horizontal line
            visible: handle.isCorner
            color: root.cornerColor
            height: root.cornerThickness
            width: root.cornerLength

            x: {
                if (handle.direction === "tl" || handle.direction === "bl") return 12;
                if (handle.direction === "tr" || handle.direction === "br") return 12 - root.cornerLength + root.cornerThickness;
                return 0;
            }
            y: {
                if (handle.direction === "tl" || handle.direction === "tr") return 12;
                if (handle.direction === "bl" || handle.direction === "br") return 12 - root.cornerThickness;
                return 0;
            }
        }

        Rectangle {
            // Vertical line
            visible: handle.isCorner
            color: root.cornerColor
            width: root.cornerThickness
            height: root.cornerLength

            x: {
                if (handle.direction === "tl" || handle.direction === "bl") return 12;
                if (handle.direction === "tr" || handle.direction === "br") return 12;
                return 0;
            }
            y: {
                if (handle.direction === "tl" || handle.direction === "tr") return 12;
                if (handle.direction === "bl" || handle.direction === "br") return 12 - root.cornerLength + root.cornerThickness;
                return 0;
            }
        }

        // Horizontal line for top/bottom edge handles
        Rectangle {
            visible: !handle.isCorner && (handle.direction === "t" || handle.direction === "b")
            color: root.cornerColor
            height: root.cornerThickness
            width: root.cornerLength
            x: 12 - root.cornerLength / 2
            y: 12 - root.cornerThickness / 2
        }

        // Vertical line for left/right edge handles
        Rectangle {
            visible: !handle.isCorner && (handle.direction === "l" || handle.direction === "r")
            color: root.cornerColor
            width: root.cornerThickness
            height: root.cornerLength
            x: 12 - root.cornerThickness / 2
            y: 12 - root.cornerLength / 2
        }

        // MouseArea for handle dragging
        MouseArea {
            anchors.fill: parent
            cursorShape: handle.cursor

            property point clickPos

            onPressed: (mouse) => {
                clickPos = mapToItem(root.parent, mouse.x, mouse.y)

                objects.selecting = true;
            }

            onPositionChanged: (mouse) => {
                if (pressed) {
                    let currentPos = mapToItem(root.parent, mouse.x, mouse.y)
                    let dx = currentPos.x - clickPos.x
                    let dy = currentPos.y - clickPos.y

                    let newX = root.x
                    let newY = root.y
                    let newW = root.width
                    let newH = root.height

                    if (handle.direction.indexOf("l") !== -1) {
                        if (newW - dx >= root.minWidth) {
                            newX += dx
                            newW -= dx
                        }
                    }
                    if (handle.direction.indexOf("r") !== -1) {
                        if (newW + dx >= root.minWidth) {
                            newW += dx
                        }
                    }
                    if (handle.direction.indexOf("t") !== -1) {
                        if (newH - dy >= root.minHeight) {
                            newY += dy
                            newH -= dy
                        }
                    }
                    if (handle.direction.indexOf("b") !== -1) {
                        if (newH + dy >= root.minHeight) {
                            newH += dy
                        }
                    }

                    root.x = newX
                    root.y = newY
                    root.width = newW
                    root.height = newH

                    clickPos = currentPos

                    root.boxChanged();
                }
            }

            onReleased: {
                root.boxReleased()

                objects.selecting = false;
            }
        }
    }

    // Top-Left corner handle
    ResizeHandle {
        x: -12
        y: -12
        cursor: Qt.SizeFDiagCursor
        direction: "tl"
        isCorner: true
    }

    // Top edge handle
    ResizeHandle {
        x: (root.width - width) / 2
        y: -12
        cursor: Qt.SizeVerCursor
        direction: "t"
    }

    // Top-Right corner handle
    ResizeHandle {
        x: root.width - 12
        y: -12
        cursor: Qt.SizeBDiagCursor
        direction: "tr"
        isCorner: true
    }

    // Right edge handle
    ResizeHandle {
        x: root.width - 12
        y: (root.height - height) / 2
        cursor: Qt.SizeHorCursor
        direction: "r"
    }

    // Bottom-Right corner handle
    ResizeHandle {
        x: root.width - 12
        y: root.height - 12
        cursor: Qt.SizeFDiagCursor
        direction: "br"
        isCorner: true
    }

    // Bottom edge handle
    ResizeHandle {
        x: (root.width - width) / 2
        y: root.height - 12
        cursor: Qt.SizeVerCursor
        direction: "b"
    }

    // Bottom-Left corner handle
    ResizeHandle {
        x: -12
        y: root.height - 12
        cursor: Qt.SizeBDiagCursor
        direction: "bl"
        isCorner: true
    }

    // Left edge handle
    ResizeHandle {
        x: -12
        y: (root.height - height) / 2
        cursor: Qt.SizeHorCursor
        direction: "l"
    }

    QtObject {
        id: objects

        property bool selecting: false
    }
}
