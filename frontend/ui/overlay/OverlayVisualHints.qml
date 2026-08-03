import QtQuick
import Qt5Compat.GraphicalEffects
import App.Backend
import "qrc:/qml/ui/overlay/components"
import "qrc:/qml/ui/overlay/components/visualhint"

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

    VisualHints {
        id: visualHints

        x: areaPreview.x
        y: areaPreview.y
        width: areaPreview.width
        height: areaPreview.height
    }

    function clear() {
        visualHints.clear();
    }

    Connections {
        target: Backend.Processor
        function onResultReceived(json) {
            let data = JSON.parse(json);
            visualHints.boxes = data.boxes;
            visualHints.parts = data.translated_parts;
        }
    }

    Connections {
        target: Backend.Preview
        function onPreviewAreaUpdated() {
            areaPreview.update();
        }
    }
}