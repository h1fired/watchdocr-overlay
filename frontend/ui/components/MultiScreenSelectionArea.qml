import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window


Item {
    id: root

    property var screensGeometries: []
    property rect box: privates.activeArea.box
    property bool animationEnable: false

    signal boxReleased()

    onAnimationEnableChanged: {
        privates.activeArea.animationEnable = root.animationEnable;
    }

    Component.onCompleted: {
        for (let i = 0; i < root.screensGeometries.length; i++) {
            let rect = root.screensGeometries[i];
            if (i == 0) {
                let area = component.createObject(root, {});
                area.pressed.connect(() => privates.onSelectionAreaPressed(area));
                area.released.connect(() => root.boxReleased());
                privates.areas.push(area);
            } else {
                let popup = popupComponent.createObject(root, {
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height
                })
                popup.area.pressed.connect(() => privates.onSelectionAreaPressed(popup.area));
                popup.area.released.connect(() => root.boxReleased());
                privates.areas.push(popup.area);
            }
        }
        privates.activeArea = privates.areas[0];
    }

    Component {
        id: popupComponent

        Window {
            visible: true
            color: "transparent"
            flags: Qt.FramelessWindowHint

            property alias area: selectionArea

            SelectionArea {
                id: selectionArea

                anchors.fill: parent
            }
        }
    }

    Component {
        id: component

        SelectionArea {
            id: selectionArea

            anchors.fill: parent
        }
    }

    QtObject {
        id: privates

        property var areas: []
        property var activeArea

        function onSelectionAreaPressed(area) {
            privates.activeArea = area;
            root.clear();
        }
    }

    function clear() {
        for (let i = 0; i < privates.areas.length; i++) {
            privates.areas[i].clear();
        }
    }

    function relativeToAbsoluteBox(box) {
        return privates.activeArea.relativeToAbsoluteBox(box);
    }

    function selectPrimaryScreenBox() {
        root.clear();
        let area = privates.areas[0];
        privates.activeArea = area;
        area.box = Qt.rect(
            area.x,
            area.y,
            area.width,
            area.height
        );
    }
}
