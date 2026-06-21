import QtQuick
import QtQuick.Controls
import App.Backend
import "qrc:/qml/ui/overlay/components"

Item {
    id: root

    property SelectionArea area: area
    property alias loading: area.loading

    SelectionArea {
        id: area

        anchors.fill: parent

        onBoxSelected: {
            let absoluteBox = area.relativeToAbsoluteBox(area.box);
            Backend.Processor.onSelectionAreaBoxReleased(absoluteBox);
        }
    }

    function cleanUp() {
        area.clear();
    }
}
