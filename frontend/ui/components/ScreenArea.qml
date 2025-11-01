import QtQuick
import App.Utils


Item {
    id: root

    property int monitor: 0

    onMonitorChanged: {
        privates.updateScreens();
    }

    Component.onCompleted: {
        privates.updateScreens();
    }

    QtObject {
        id: privates

        function updateScreens() {
            let screen = EScreen.screens[root.monitor];
            let geometry = screen.geometry;
            let pos = Qt.point(
                geometry.x - EScreen.globalX,
                geometry.y - EScreen.globalY
            );
            Object.assign(root, {
                x: pos.x,
                y: pos.y,
                width: geometry.width,
                height: geometry.height
            });
        }
    }
}