import QtQuick
import App.Backend
import App.System
import "qrc:/qml/ui/overlay/components"

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
            updatePreview();
        }
    }

    Timer {
        id: windowTransparentTimer

        running: false
        interval: 50

        onTriggered: {
            System.windowTransparentForCapture = false;
        }
    }

    function updatePreview() {
        windowTransparentTimer.stop();
        System.windowTransparentForCapture = true;
        Backend.Preview.requestAllScreensPreview();
        windowTransparentTimer.start();
    }
}
