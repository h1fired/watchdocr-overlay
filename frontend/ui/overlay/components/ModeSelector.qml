import QtQuick
import QtQuick.Layouts
import "../../common/controls"


Rectangle {
    id: root

    property string             _currentMode:   "live"
    readonly property string    currentMode:    _currentMode

    ListModel {
        id: modesModel

        ListElement {
            name: "live"
            title: "Live"
        }

        ListElement {
            name: "onetime"
            title: "One-time"
        }
    }

    implicitWidth: row.implicitWidth + 8

    radius: 6

    color: "#12151E"
    border.width: 1
    border.color: "#23272F"

    RowLayout {
        id: row

        anchors.fill: parent
        anchors.margins: 4
        spacing: 4

        Repeater {
            model: modesModel

            OButton {
                Layout.fillHeight: true
                Layout.preferredWidth: implicitWidth + 12

                checkable: true
                checked: root._currentMode === model.name

                background: Rectangle {
                    color: checked ? "#23272F" : "transparent"
                    radius: 4
                }

                text: model.title
                font.family: "Segoe UI"
                font.weight: 600
                font.pixelSize: 12
                palette.buttonText: hovered ? "#94A3B8" :"#475569"
                palette.brightText : "#94A3B8"

                onClicked: {
                    root._currentMode = model.name;
                }
            }
        }
    }
}