import QtQuick
import QtQuick.Layouts
import App.Gui
import "qrc:/qml/ui/common/controls"

Item {
    id: root

    property alias sourceLanguages: menu.sourceLanguages
    property alias targetLanguages: menu.targetLanguages
    property alias sourceLanguage: menu.sourceLanguage
    property alias targetLanguage: menu.targetLanguage
    readonly property alias sourceLanguageName: menu.sourceLanguageName
    readonly property alias targetLanguageName: menu.targetLanguageName
    readonly property alias searchQuery: menu.searchQuery

    implicitWidth: row.width

    MouseArea {
        anchors.fill: parent
    }

    Row {
        id: row

        TranslationSelectorButton {
            height: root.height

            language: menu.sourceLanguageName
            shortLanguage: menu.sourceLanguage

            onClicked: {
                Gui.showWindowPopup(menu);
            }
        }

        OButton {
            width: height
            height: root.height

            icon.source: "qrc:/qml/resources/icons/swap.svg"
            icon.color: "#E9E9E9"
            icon.width: 18
            icon.height: 18

            background: Rectangle {
                color: parent.hovered ? "#2C2C2C" : "transparent"
                radius: 6
            }

            onClicked: {
                menu.swap();
            }
        }

        TranslationSelectorButton {
            height: root.height

            language: menu.targetLanguageName
            shortLanguage: menu.targetLanguage

            onClicked: {
                Gui.showWindowPopup(menu);
            }
        }
    }

    TranslationSelectorMenu {
        id: menu

        visible: false

        x: 0
        y: 36

        width: 460
    }
}