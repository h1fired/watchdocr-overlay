import QtQuick
import Qt5Compat.GraphicalEffects
import "qrc:/qml/ui/overlay/components"

Delegate {
    id: root

    required property ImageProvider provider

    rectMargin: 2

    // Background inpaint shader
    ShaderEffectSource {
        id: frameCapture

        visible: false
        live: true
        recursive: false
        sourceItem: root.provider
        textureSize: Qt.size(root.provider.width, root.provider.height)
    }

    Repeater {

        model: parent.visible ? root.boxes : 0

        MatrixDelegateBox {
            id: box

            required property var modelData

            coordinates: root.expandQuad(modelData.coordinates, root.rectMargin)

            readonly property real ringRadius: Math.max(8, box.height * 0.25)

            ShaderEffect {
                id: cleanBackgroundBox

                anchors.fill: parent

                property variant source: frameCapture

                property vector2d q0: Qt.vector2d(box.coordinates[0] / root.width,
                                                  box.coordinates[1] / root.height)
                property vector2d q1: Qt.vector2d(box.coordinates[2] / root.width,
                                                  box.coordinates[3] / root.height)
                property vector2d q2: Qt.vector2d(box.coordinates[4] / root.width,
                                                  box.coordinates[5] / root.height)
                property vector2d q3: Qt.vector2d(box.coordinates[6] / root.width,
                                                  box.coordinates[7] / root.height)

                property real tolerance: 0.06
                property real seam: 0.0
                property real gradient: 0.0

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
