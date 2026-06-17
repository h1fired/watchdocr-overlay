import QtQuick
import QtQuick.Controls
import App.Backend
import "qrc:/qml/ui/overlay/components"

Item {
    id: root

    property SelectionArea area: area

    SelectionArea {
        id: area

        anchors.fill: parent

        onBoxReleased: {
            let absoluteBox = area.relativeToAbsoluteBox(area.box);
            Backend.Processor.onSelectionAreaBoxReleased(absoluteBox);
        }
    }

    Connections {
        target: Backend.Processor

        function onRecognizerStatusChanged(status) {
            area.loading = status === 1;
        }
    }

    function cleanUp() {
        area.clear();
    }
}
