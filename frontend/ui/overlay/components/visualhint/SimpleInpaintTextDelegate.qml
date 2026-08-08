import QtQuick
import App.ImageText
import "qrc:/qml/ui/overlay/components"

Delegate {
    id: root

    required property ImageProvider provider
    rectMargin: 2

    TextColorDetector {
        id: detector

        coordinates: root.boxes
        image: provider.providerId
    }

    Repeater {
        model: parent.visible ? root.boxes : 0

        MatrixDelegateBox {
            id: box

            required property int index
            required property var modelData

            coordinates: root.expandQuad(modelData.coordinates, root.rectMargin)

            VisualHintText {
                id: textLabel

                anchors.fill: parent

                leftPadding: root.rectMargin * 2
                
                text: root.parts[index] ?? ""
                color: detector.colorsOutput[index]
                    ? detector.colorsOutput[index].text
                    : "#FFFFFF"
                style: detector.colorsOutput[index]
                    && detector.colorsOutput[index].has_border
                    ? Text.Outline
                    : Text.Normal
                styleColor: detector.colorsOutput[index]
                    && detector.colorsOutput[index].has_border
                    ? detector.colorsOutput[index].border
                    : "#000000"
            }
        }
    }
}
