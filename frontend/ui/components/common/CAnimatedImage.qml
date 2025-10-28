import App.External
import Qt5Compat.GraphicalEffects


EAnimatedImage {
    id: root

    property string color: ""

    ColorOverlay {
        id: overlay

        visible: root.color != ""

        anchors.fill: root

        source: root
        color: root.color
    }
}