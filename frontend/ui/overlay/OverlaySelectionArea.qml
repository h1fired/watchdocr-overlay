import QtQuick
import QtQuick.Controls
import "components"


Item {
    id: root

    property SelectionArea area: area

    SelectionArea {
        id: area

        anchors.fill: parent
    }
}
