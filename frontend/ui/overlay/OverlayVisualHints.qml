import QtQuick
import Qt5Compat.GraphicalEffects
import App.Backend
import "components"

Item {
    id: root

    property bool boxesVisible: false
    property var _boxes: ([])
    property point offset: Qt.point(0, 0)
    property int _expand: 0

    ImageProvider {
        id: areaPreview

        visible: false

        x: root.offset.x
        y: root.offset.y

        providerId: "preview_area"
        layer.enabled: true
    }

    ShaderEffectSource {
        // Explicit texture capture of the image
        id: previewTex

        visible: false

        sourceItem: areaPreview
        live: true
    }

    // 3. Blur the captured texture
    FastBlur {
        id: blurred

        anchors.fill: areaPreview

        source: previewTex
        radius: 24
        visible: false
        layer.enabled: true
    }

    Item {
        id: maskShape

        visible: false

        x: areaPreview.x
        y: areaPreview.y
        width: areaPreview.width
        height: areaPreview.height

        layer.enabled: true

        Repeater {
            model: root._boxes

            Rectangle {
                x: modelData[1][0] - root._expand
                y: modelData[1][1] - root._expand
                width:  modelData[1][2] - modelData[1][0] + root._expand * 2
                height: modelData[1][3] - modelData[1][1] + root._expand * 2
                color: "white"
            }
        }
    }

    OpacityMask {
        // Final composited result
        x: areaPreview.x
        y: areaPreview.y
        width: areaPreview.width
        height: areaPreview.height

        visible: root.boxesVisible

        source: blurred
        maskSource: maskShape
    }

    Item {
        x: areaPreview.x
        y: areaPreview.y
        width: areaPreview.width
        height: areaPreview.height

        visible: root.boxesVisible

        Repeater {
            model: root._boxes

            Rectangle {
                x: modelData[1][0] - root._expand
                y: modelData[1][1] - root._expand
                width:  modelData[1][2] - modelData[1][0] + root._expand * 2
                height: modelData[1][3] - modelData[1][1] + root._expand * 2

                color: Qt.rgba(0, 0, 0, 0.3)

                Text {
                    anchors.fill: parent
                    
                    text: modelData[0]
                    fontSizeMode: Text.Fit
                    font.pixelSize: height
                    font.weight: 600
                    minimumPixelSize: 6
                    horizontalAlignment: Text.AlignLeft
                    verticalAlignment: Text.AlignVCenter
                    color: "white"

                    layer.enabled: true
                    layer.effect: DropShadow {
                        radius: 5
                        samples: radius * 2
                        color: Qt.rgba(0, 0, 0, 1.0)
                        horizontalOffset: 0
                        verticalOffset: 1
                    }
                }
            }

        }
    }

    Connections {
        target: Backend.Processor
        function onResultReceived(json) {
            let data = JSON.parse(json);
            root._boxes = data.boxes;
            root.boxesVisible = true;
        }
    }

    Connections {
        target: Backend.Preview
        function onPreviewAreaUpdated() {
            areaPreview.update();
        }
    }
}