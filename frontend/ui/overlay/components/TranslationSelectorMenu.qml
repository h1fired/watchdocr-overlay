import QtQuick
import QtQuick.Layouts
import QtQuick.Controls.Basic


Rectangle {
    id: root

    color: "#070B14"
    radius: 12
    border.width: 1
    border.color: "#21242D"

    property list<string> sourceLanguages: ([])
    property list<string> targetLanguages: ([])
    property alias sourceLanguage: source.current
    property alias targetLanguage: target.current

    ColumnLayout {
        anchors.fill: parent

        TextField {
            id: searchTextField

            Layout.fillWidth: true
            Layout.preferredHeight: 32
            Layout.margins: 12

            background: Rectangle {
                color: "#12151E"
                radius: 6

                border.width: 1
                border.color: "#23272F"
            }

            placeholderText: "Search languages"
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.leftMargin: 12
            Layout.rightMargin: 12

            spacing: 8

            LanguageListView {
                id: source

                Layout.fillWidth: true
                Layout.fillHeight: true

                languages: root.sourceLanguages
            }

            Rectangle {
                Layout.fillHeight: true
                Layout.topMargin: 12
                Layout.bottomMargin: 12
                width: 1

                color: "#1A1C26"
            }

            LanguageListView {
                id: target

                Layout.fillWidth: true
                Layout.fillHeight: true
            
                languages: root.targetLanguages
            }
        }

    }

}
