import QtQuick
import Qt5Compat.GraphicalEffects


Image {
    id: root

    property alias color: overlay.color

    ColorOverlay {
        id: overlay
        anchors.fill: root
        source: root
    }
}
