import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import App.Utils


Item {
    id: root

    property rect box: privates.activeArea.box
    property bool loading: false

    signal boxReleased()
    signal pressed()

    onLoadingChanged: {
        privates.activeArea.animationEnable = root.loading;
    }

    Component.onCompleted: {
        privates.updateSelectionAreas();
    }

    Connections {
        target: ExtScreen

        function onScreensChanged() {
            privates.updateSelectionAreasDelayed();
        }

        function onPrimaryScreenChanged() {
            privates.updateSelectionAreasDelayed();
        }
    }

    Component {
        id: popupComponent

        Window {
            id: subwindow

            visible: {
                if (root.visible) {
                    subwindow.show();
                    return true;
                } else {
                    subwindow.close()
                    return false;
                }
            }
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

    Timer {
        id: updateTimer
        interval: 1000
        running: false
        repeat: false
        onTriggered: privates.updateSelectionAreas()
    }

    QtObject {
        id: privates

        property var activeArea
        property var areas: []
        property var objects: []

        function onSelectionAreaPressed(area) {
            privates.activeArea = area;
            root.clear();
            root.pressed();
        }

        function updateSelectionAreasDelayed() {
            updateTimer.start();
        }

        function updateSelectionAreas() {
            // Clear previous screens
            for (let i = 0; i < privates.objects.length; i++) {
                privates.objects[i].destroy();
            }
            privates.objects = [];
            privates.areas = [];

            // Create new screens
            for (let i = 0; i < ExtScreen.screens.length; i++) {
                let rect = ExtScreen.screens[i].geometry;

                if (ExtScreen.screens[i] == ExtScreen.primary) {
                    let area = component.createObject(root, {});
                    area.pressed.connect(() => privates.onSelectionAreaPressed(area));
                    area.released.connect(() => root.boxReleased());
                    privates.areas.push(area);
                    privates.objects.push(area);
                } else {
                    let popupArea = popupComponent.createObject(root, {
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height
                    })
                    popupArea.area.pressed.connect(() => privates.onSelectionAreaPressed(popupArea.area));
                    popupArea.area.released.connect(() => root.boxReleased());
                    privates.areas.push(popupArea.area);
                    privates.objects.push(popupArea);
                }
            }
            privates.activeArea = privates.areas[0];
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
