import QtQuick
import QtQuick.Layouts
import "qrc:/qml/ui/common/controls"

Rectangle {
    id: root

    property string             _currentMode:   "onetime"
    readonly property string    currentMode:    _currentMode

    ListModel {
        id: modesModel

        ListElement {
            name: "onetime"
            title: "One-time"
        }

        ListElement {
            name: "live"
            title: "Live"
        }
    }

    implicitWidth: row.implicitWidth + 8

    radius: 6

    color: "#2C2C2C"

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
                    color: checked ? "#414141" : "transparent"
                    radius: 4
                }

                text: model.title
                font.family: "Segoe UI"
                font.weight: 600
                font.pixelSize: 12
                palette.buttonText: hovered ? "#E7E7E7" : "#ADADAD"
                palette.brightText : "#E7E7E7"

                onClicked: {
                    root._currentMode = model.name;
                }
            }
        }
    }
}