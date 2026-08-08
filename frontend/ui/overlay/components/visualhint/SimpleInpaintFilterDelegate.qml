import QtQuick
import Qt5Compat.GraphicalEffects
import "qrc:/qml/ui/overlay/components"

Delegate {
    id: root

    required property ImageProvider provider

    Repeater {

        model: parent.visible ? root.boxes : 0

        MatrixDelegateBox {
            id: box

            required property var modelData

            coordinates: root.expandQuad(modelData.coordinates, root.rectMargin)

            // Background inpaint shader
            ShaderEffectSource {
                id: rawBoxCapture

                visible: false

                live: true
                sourceItem: root.provider
                sourceRect: Qt.rect(
                    box.x,
                    box.y,
                    box.width,
                    box.height
                )
            }

            ShaderEffect {
                id: cleanBackgroundBox

                property variant source: rawBoxCapture
                property vector2d pixelSize: Qt.vector2d(4, 4)

                anchors.fill: parent

                layer.enabled: true
                opacity: 0

                fragmentShader: "qrc:/qml/ui/shaders/average.frag.qsb" 
            }

            Rectangle {
                id: boxMask

                visible: false

                anchors.fill: parent

                radius: 6
                color: "black"
            }

            OpacityMask {
                id: maskedBackground

                anchors.fill: parent

                source: cleanBackgroundBox
                maskSource: boxMask
            }
        }
    }
}
