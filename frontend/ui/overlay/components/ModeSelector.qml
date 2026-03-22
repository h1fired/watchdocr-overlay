import QtQuick
import QtQuick.Layouts
import "../../common/controls"


Rectangle {
    id: root

    property string     _currentMode:       "live"
    property var        _modes:             ["live", "onetime"]
    readonly property string currentMode:    _currentMode

    implicitWidth: row.implicitWidth + 8

    radius: 9

    color: "#12151E"
    border.width: 1
    border.color: "#23272F"

    RowLayout {
        id: row

        anchors.fill: parent
        anchors.margins: 4

        Repeater {
            model: root._modes

            OButton {
                Layout.fillHeight: true
                Layout.preferredWidth: 60

                checkable: true
                checked: root._currentMode === modelData

                background: Rectangle {
                    color: checked ? "#23272F" : "transparent"
                    radius: 6
                }

                text: modelData
                font.family: "Segoe UI"
                font.weight: 600
                font.pixelSize: 12
                palette.buttonText: hovered ? "#94A3B8" :"#475569"
                palette.brightText : "#94A3B8"

                onClicked: {
                    root._currentMode = text;
                }
            }
        }
    }
}