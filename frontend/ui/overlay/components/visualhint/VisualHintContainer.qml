import QtQuick

Item {
    id: root

    property var boxes: []
    property var parts: []
    property alias filterDelegate: loader.sourceComponent
    property alias textDelegate: textRepeater.delegate

    Loader {
        id: loader
    
        anchors.fill: parent
    }

    Repeater {
        id: textRepeater

        model: root.visible ? root.parts : 0

        onItemAdded: (index, item) => {
            if (root.boxes[index]) {
                item.x = root.boxes[index].boundings[0];
                item.y = root.boxes[index].boundings[1];
                item.width = root.boxes[index].boundings[2] - root.boxes[index].boundings[0];
                item.height = root.boxes[index].boundings[3] - root.boxes[index].boundings[1];
            }
        }
    }

    function clear() {
        root.boxes = ([]);
        root.parts = ([]);
    }
}