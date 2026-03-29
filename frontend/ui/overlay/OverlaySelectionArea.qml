import QtQuick
import QtQuick.Controls
import App.Backend
import "components"


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
}
