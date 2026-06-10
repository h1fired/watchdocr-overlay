import QtQuick
import App.Backend
import App.System
import "components"

Item {
    id: root

    property bool active: false

    ImageProvider {
        id: screensPreview

        visible: root.active

        anchors.fill: parent

        providerId: "preview_screens"
    }

    Connections {
        target: Backend.Preview

        function onPreviewUpdated() {
            screensPreview.update();
        }
    }

    Connections {
        target: System

        function onVisibleChanged() {
            if (root.active) {
                Backend.Preview.requestAllScreensPreview();
            }
        }
    }
}
