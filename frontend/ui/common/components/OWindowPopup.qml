import QtQuick
import QtQuick.Controls.Basic


Popup {
    id: root

    property var contentObject
    property var _closeSignalHandler

    padding: 0

    background: Rectangle {
        color: "transparent"
    }

    MouseArea {
        anchors.fill: parent

        onClicked: (e) => {
            if (!root.contentObject)
                return;
            let localPoint = contentObject.mapFromItem(contentRect, Qt.point(e.x, e.y));
            if (!contentObject.contains(localPoint)) {
                root._close();
            }
        }
    }

    Rectangle {
        id: contentRect

        anchors.fill: parent

        color: Qt.rgba(0.0, 0.0, 0.0, 0.4)
    }

    onContentObjectChanged: {
        if (!root.contentObject)
            return;
        root.contentObject.parent = contentRect;
        root.contentObject.anchors.centerIn = Qt.binding(() => contentRect);
        root.contentObject.closed.connect(root._close);
        root.contentObject.visible = true;
        root.visible = true;
    }

    function _close() {
        root.contentObject.closed.disconnect(root._close);
        root.visible = false;
        root.contentObject.visible = false;
        root.contentObject = undefined;
    }
}
