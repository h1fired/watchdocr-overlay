import QtQuick
import "qrc:/qml/ui/common/controls"

OText {
    id: root

    padding: 0

    fontSizeMode: Text.Fit
    font.pixelSize: height
    font.weight: 600
    minimumPixelSize: 2

    horizontalAlignment: Text.AlignLeft
    verticalAlignment: Text.AlignVCenter

    renderType: Text.QtRendering
    antialiasing: true

    color: "white"
}