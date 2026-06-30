import QtQuick
import App.Utils

Item {
    id: root

    property int monitor: 0

    onMonitorChanged: {
        privates.updateUtilsScreens();
    }

    Component.onCompleted: {
        privates.updateUtilsScreens();
    }

    QtObject {
        id: privates

        function updateUtilsScreens() {
            let screen = UtilsScreen.screens[root.monitor];
            let geometry = screen.geometry;
            let pos = Qt.point(
                geometry.x - UtilsScreen.globalX,
                geometry.y - UtilsScreen.globalY
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
