import QtQuick
import App.Backend
import App.System
import "components"

Item {
    id: root

    property bool active: false
    property bool grabbing: false

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
            updatePreview();
        }
    }

    function updatePreview() {
        root.grabbing = true;
        timer.start();
    }

    Timer {
        id: timer

        interval: 5

        onTriggered: {
            Backend.Preview.requestAllScreensPreview();
            root.grabbing = false;
        }
    }
}
