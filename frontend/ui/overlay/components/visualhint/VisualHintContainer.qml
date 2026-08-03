import QtQuick

Item {
    id: root

    property var boxes: []
    property var parts: []
    property alias filterDelegate: filterLoader.sourceComponent
    property alias textDelegate: textLoader.sourceComponent

    Loader {
        id: filterLoader
    
        anchors.fill: parent

        onLoaded: {
            item.boxes = Qt.binding(() => root.boxes);
        }
    }

    Loader {
        id: textLoader
    
        anchors.fill: parent

        onLoaded: {
            item.parts = Qt.binding(() => root.parts);
            item.boxes = Qt.binding(() => root.boxes);
        }
    }
}