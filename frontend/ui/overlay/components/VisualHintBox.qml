import QtQuick
import Qt5Compat.GraphicalEffects

Item {
    id: root

    required property ImageProvider provider
    required property string text

    ShaderEffectSource {
        id: rawBoxCapture

        visible: false
        live: true

        sourceItem: provider
        sourceRect: Qt.rect(root.x, root.y, root.width, root.height)
    }

    ShaderEffect {
        id: cleanBackgroundBox

        property variant source: rawBoxCapture
        property vector2d pixelSize: Qt.vector2d(4, 4)

        visible: false

        anchors.fill: parent

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

    // Box text with background blending
    Text {
        id: textLabel

        visible: false

        anchors.fill: parent
        
        text: root.text
        fontSizeMode: Text.Fit
        font.pixelSize: height
        font.weight: 600
        minimumPixelSize: 6
        horizontalAlignment: Text.AlignLeft
        verticalAlignment: Text.AlignVCenter
        padding: 0

        color: "white"
    }

    Blend {
        anchors.fill: parent
        source: maskedBackground
        foregroundSource: textLabel
        mode: "exclusion"
    }
}