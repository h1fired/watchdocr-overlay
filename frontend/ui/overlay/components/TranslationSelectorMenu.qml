import QtQuick
import QtQuick.Layouts
import QtQuick.Controls.Basic
import "qrc:/qml/ui/common/controls"
import "qrc:/qml/ui/common/components"

OMessageBoxFrame {
    id: root

    title: "Language pair"

    color: "#1A1A1A"
    radius: 15
    border.width: 1
    border.color: "#353535"

    property var sourceLanguages: []
    property var targetLanguages: []
    property alias sourceLanguage: source.current
    property alias targetLanguage: target.current
    readonly property string sourceLanguageName: source.currentName
    readonly property string targetLanguageName: target.currentName
    readonly property string searchQuery: searchTextField.text

    ColumnLayout {
        anchors.fill: parent

        spacing: 0

        clip: true

        TextField {
            id: searchTextField

            Layout.fillWidth: true
            Layout.preferredHeight: 32
            Layout.topMargin: 12
            Layout.bottomMargin: 12
            Layout.leftMargin: 16
            Layout.rightMargin: 16

            background: Rectangle {
                color: "#1A1A1A"
                radius: 6

                border.width: 1
                border.color: "#2C2C2C"
            }

            placeholderText: "Search languages"
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 1

            color: "#2C2C2C"
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 160

            spacing: 0

            LanguageListView {
                id: source

                Layout.fillWidth: true
                Layout.fillHeight: true

                languages: root.sourceLanguages
            }

            Rectangle {
                Layout.fillHeight: true
                width: 1

                color: "#2C2C2C"
            }

            LanguageListView {
                id: target

                Layout.fillWidth: true
                Layout.fillHeight: true
            
                languages: root.targetLanguages
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 52

            Rectangle {
                width: parent.width
                height: 1

                color: "#2C2C2C"
            }

            Row {
                anchors.verticalCenter: parent.verticalCenter
                padding: 20

                spacing: 8

                Text {
                    anchors.verticalCenter: parent.verticalCenter

                    text: source.current

                    font.family: "Segoe UI"
                    font.weight: 500
                    font.pixelSize: 10
                    color: "#676767"
                }

                Text {
                    anchors.verticalCenter: parent.verticalCenter

                    text: source.currentName

                    font.family: "Segoe UI"
                    font.weight: 600
                    font.pixelSize: 12
                    color: "#999999"
                }

                Text {
                    anchors.verticalCenter: parent.verticalCenter

                    text: "→"

                    font.family: "Segoe UI"
                    font.pixelSize: 12
                    color: "#f1f1f1"
                }

                Text {
                    anchors.verticalCenter: parent.verticalCenter

                    text: target.current

                    font.family: "Segoe UI"
                    font.weight: 500
                    font.pixelSize: 10
                    color: "#676767"
                }

                Text {
                    anchors.verticalCenter: parent.verticalCenter

                    text: target.currentName

                    font.family: "Segoe UI"
                    font.weight: 600
                    font.pixelSize: 12
                    color: "#999999"
                }
            }

            OButton {
                width: 72
                height: 28

                anchors.right: parent.right
                anchors.rightMargin: 16
                anchors.verticalCenter: parent.verticalCenter

                text: "Swap"

                font.family: "Segoe UI"
                font.weight: 600

                icon.source: "qrc:/qml/resources/icons/swap.svg"
                icon.width: 14
                icon.height: 14

                palette.buttonText: hovered ? "#f3f3f3" :"#c5c5c5"
                background: Rectangle {
                    radius: 6

                    color: parent.hovered ? "#4d4d4d" : "#313131"
                    border.width: 1
                    border.color: parent.hovered ? "#929292" : "#616161"
                }

                onClicked: root.swap()
            }
        }
    }

    function swap() {
        let sCode = source.current;
        let tCode = target.current;

        if (source.languages.codeExists(tCode))
            source.current = tCode;
        else
            source.current = source.languages.get(0).code;
        
        if (target.languages.codeExists(sCode))
            target.current = sCode;
        else
            target.current = target.languages.get(0).code;
    }
}
