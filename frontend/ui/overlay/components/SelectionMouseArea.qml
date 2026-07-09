import QtQuick


MouseArea {
    id: root

    readonly property alias selecting: objects.selecting
    readonly property alias box: objects.box

    anchors.fill: parent

    cursorShape: Qt.CrossCursor

    onPressed: (event) => {
        objects.startPoint = Qt.point(event.x, event.y);
        objects.endPoint = objects.startPoint;

        objects.selecting = true;
    }

    onPositionChanged: (event) => {
        objects.endPoint = Qt.point(event.x, event.y);
        objects.box = rectFromPoints(objects.startPoint, objects.endPoint);
    }

    onReleased: (event) => {
        objects.endPoint = Qt.point(event.x, event.y);
        let box = rectFromPoints(objects.startPoint, objects.endPoint);

        // Normalize box to minimal recognizable size
        if (box.width < selectionBox.minWidth)
            box.width = selectionBox.minWidth;
        if (box.height < selectionBox.minHeight)
            box.height = selectionBox.minHeight;

        objects.box = box
        objects.selecting = false;
    }

    function rectFromPoints(p1, p2) {
        var x = Math.min(p1.x, p2.x);
        var y = Math.min(p1.y, p2.y);
        var w = Math.abs(p2.x - p1.x);
        var h = Math.abs(p2.y - p1.y);
        return Qt.rect(x, y, w, h);
    }

    QtObject {
        id: objects

        property point startPoint: Qt.point(0, 0)
        property point endPoint: Qt.point(0, 0)
        property bool selecting: false
        property rect box: Qt.rect(0, 0, 0, 0)
    }
}
