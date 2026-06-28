import QtQuick
import Qt5Compat.GraphicalEffects
import App.Backend
import "qrc:/qml/ui/overlay/components"

Item {
    id: root

    property bool boxesVisible: true
    property point offset: Qt.point(0, 0)
    property var _boxes: ([])
    property int _expand: 2

    ImageProvider {
        id: areaPreview

        visible: false

        x: root.offset.x
        y: root.offset.y

        providerId: "preview_area"
        layer.enabled: true
    }

    Item {
        x: areaPreview.x
        y: areaPreview.y
        width: areaPreview.width
        height: areaPreview.height

        visible: root.boxesVisible

        Repeater {
            model: root._boxes

            Item {
                id: boxItem

                x: modelData[1][0] - root._expand
                y: modelData[1][1] - root._expand
                width:  modelData[1][2] - modelData[1][0] + (root._expand * 2)
                height: modelData[1][3] - modelData[1][1] + (root._expand * 2)

                ShaderEffectSource {
                    id: rawBoxCapture

                    visible: false
                    live: true

                    sourceItem: areaPreview
                    sourceRect: Qt.rect(boxItem.x, boxItem.y, boxItem.width, boxItem.height)
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
                    anchors.fill: parent
                    source: cleanBackgroundBox
                    maskSource: boxMask
                }

                // Text
                Text {
                    id: ttext

                    visible: false

                    anchors.fill: parent
                    
                    text: modelData[0]
                    fontSizeMode: Text.Fit
                    font.pixelSize: height
                    font.weight: 600
                    minimumPixelSize: 6
                    horizontalAlignment: Text.AlignLeft
                    verticalAlignment: Text.AlignVCenter
                    color: "white"
                }

                Blend {
                    anchors.fill: parent
                    source: cleanBackgroundBox
                    foregroundSource: ttext
                    mode: "exclusion"
                }
            }

        }
    }

    function clear() {
        root._boxes = ([]);
    }

    Connections {
        target: Backend.Processor
        function onResultReceived(json) {
            let data = JSON.parse(json);
            root._boxes = data.boxes;
        }
    }

    Connections {
        target: Backend.Preview
        function onPreviewAreaUpdated() {
            areaPreview.update();
        }
    }
}