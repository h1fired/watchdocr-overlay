import QtQuick
import Qt5Compat.GraphicalEffects

Item {
    id: root

    required property ImageProvider provider
    required property string text
    property int internalPadding: 0
    signal linkActivated()

    ShaderEffectSource {
        id: rawBoxCapture

        visible: false
        live: true

        sourceItem: provider
        sourceRect: Qt.rect(
            root.x + root.internalPadding,
            root.y + root.internalPadding,
            root.width - (root.internalPadding * 2),
            root.height - (root.internalPadding * 2)
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

    // Box text with background blending
    Text {
        id: textLabel

        visible: true
        opacity: 0

        anchors.fill: parent

        leftPadding: root.internalPadding * 2

        text: root.linkify(root.text)
        fontSizeMode: Text.Fit
        font.pixelSize: height
        font.weight: 600
        minimumPixelSize: 8
        horizontalAlignment: Text.AlignLeft
        verticalAlignment: Text.AlignVCenter
        padding: 0

        renderType: Text.QtRendering
        antialiasing: true

        color: "white"

        textFormat: Text.StyledText

        onLinkActivated: (link) => {
            Qt.openUrlExternally(link);
            root.linkActivated();
        }

        MouseArea {
            anchors.fill: parent

            acceptedButtons: Qt.NoButton
            cursorShape: textLabel.hoveredLink ? Qt.PointingHandCursor : Qt.ArrowCursor
        }
    }

    ShaderEffectSource {
        id: textMaskSource

        visible: false

        sourceItem: textLabel
        live: true
        smooth: true
        samples: 4
    }

    ShaderEffect {
        anchors.fill: parent

        property variant background: cleanBackgroundBox
        property variant textMask: textMaskSource

        fragmentShader: "qrc:/qml/ui/shaders/text_difference.frag.qsb"

        smooth: true
    }

    function escapeHtml(str) {
        return str.replace(/&/g, "&amp;")
                  .replace(/</g, "&lt;")
                  .replace(/>/g, "&gt;");
    }

    function linkify(str) {
        var text = escapeHtml(str);
        var urlRegex = /(https?:\/\/[^\s]+|www\.[^\s]+)/g;
        return text.replace(urlRegex, function(url) {
            var href = url.startsWith('www.') ? 'https://' + url : url;
            return `<a href="${href}">${url}</a>`;
        });
    }
}