import QtQuick
import "qrc:/qml/ui/common/controls"

OText {
    id: root

    padding: 0

    fontSizeMode: Text.Fit
    font.pixelSize: height
    font.weight: 600

    minimumPixelSize: height / 1.5

    horizontalAlignment: Text.AlignLeft
    verticalAlignment: Text.AlignVCenter

    renderType: Text.QtRendering
    antialiasing: true

    color: "white"

    transform: Scale {
        xScale: {
            if (root.width >= root.paintedWidth)
                return 1.0
            return root.width / (root.paintedWidth + 8)
        }
    }
}