import QtQuick
import App.Backend
import App.System
import "qrc:/qml/ui/overlay/components"

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
            updatePreview(false);
        }
    }

    function updatePreview(delayed: bool) {
        root.grabbing = true;

        if (delayed) {
            timer.start();
        } else {
            Backend.Preview.requestAllScreensPreview();
            root.grabbing = false;
        }
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
