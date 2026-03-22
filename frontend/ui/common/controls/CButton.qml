import QtQuick
import QtQuick.Controls.Basic
import App.Gui
import App.Visual.Colors
import App.Visual.Fonts
import "qrc:/qml/common"


Button {
    id: root

    implicitHeight: Gui.dp(32)

    font.family: Fonts.primary
    font.weight: 500
    font.pixelSize: Gui.dp(14)

    icon.width: 0
    icon.height: 0
    
    clip: true

    background: Rectangle {
        color: (
            !root.enabled ? Colors.btnBackgroundDisabled :
            root.down ? Colors.btnBackgroundDown :
            root.hovered ? Colors.btnBackgroundHovered : Colors.btnBackground
        )
        radius: Gui.dp(9)
    }

    contentItem: Item {
        implicitWidth: row.implicitWidth
        implicitHeight: row.implicitHeight
        anchors.centerIn: parent

        Row {
            id: row

            anchors.centerIn: parent

            spacing: root.spacing

            CImage {
                width: root.icon.width
                height: root.icon.height

                anchors.verticalCenter: parent.verticalCenter

                source: root.icon.source
                fillMode: Image.PreserveAspectFit
                color: root.propagateTextColorToIcon ? textItem.color : icon.color
                rotation: root.iconRotation
            }

            CText {
                id: textItem

                anchors.verticalCenter: parent.verticalCenter

                text: root.text
                font: root.font
                color: (
                    !root.textColor.valid
                    ? root.enabled ? Colors.text : Colors.textDisabled
                    : root.textColor
                )
            }
        }
    }

    property real iconRotation: 0
    property bool propagateTextColorToIcon: false
    property int mouseMargin: 0
    property color textColor
}
