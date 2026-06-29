import QtQuick
import Qt5Compat.GraphicalEffects
import App.Backend
import "qrc:/qml/ui/overlay/components"

Item {
    id: root

    property point offset: Qt.point(0, 0)

    ImageProvider {
        id: areaPreview

        visible: false

        x: root.offset.x
        y: root.offset.y

        providerId: "preview_area"
        layer.enabled: true
    }

    VisualHintContainer {
        id: container

        anchors.fill: parent

        provider: areaPreview
    }

    function clear() {
        container.clear();
    }

    Connections {
        target: Backend.Processor
        function onResultReceived(json) {
            let data = JSON.parse(json);
            container.boxes = data.boxes;
        }
    }

    Connections {
        target: Backend.Preview
        function onPreviewAreaUpdated() {
            areaPreview.update();
        }
    }
}