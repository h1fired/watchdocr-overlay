import QtQuick
import App.Utils

Item {
    id: root

    property int monitor: 0
    property int mouseTrackedMonitor: -1
    property bool enableMonitorMouseTracking: false

    onMonitorChanged: {
        privates.updateUtilsScreens();
    }

    onEnableMonitorMouseTrackingChanged: {
        UtilsMouseTracker.enabled = enableMonitorMouseTracking;
    }

    Component.onCompleted: {
        privates.updateUtilsScreens();
    }

    QtObject {
        id: privates

        function updateUtilsScreens() {
            if (root.monitor === -1) {
                Object.assign(root, {
                    x: 0,
                    y: 0,
                    width: 0,
                    height: 0
                });
                return;
            }

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

    Connections {
        target: UtilsMouseTracker
        enabled: root.enableMonitorMouseTracking

        function onPositionChanged() {
            let monitor_index = -1;
            let pos = UtilsMouseTracker.position;

            for (let i = 0; i < UtilsScreen.screens.length; i++) {
                let screen = UtilsScreen.screens[i];
                let geometry = screen.geometry;

                if (contains(geometry, pos)) {
                    monitor_index = i;
                }
            }

            root.mouseTrackedMonitor = monitor_index;
        }

        function contains(rect, point) {
            return point.x >= rect.x &&
                point.x < rect.x + rect.width &&
                point.y >= rect.y &&
                point.y < rect.y + rect.height
        }
    }
}
