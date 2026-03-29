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
            Backend.Processor.onSelectionAreaBoxReleased(box);
        }
    }
}
