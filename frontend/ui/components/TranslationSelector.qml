import QtQuick
import QtQuick.Layouts


Rectangle {
    color: "#000000"

    property list<string> sourceLanguages: ([])
    property list<string> targetLanguages: ([])
    property alias sourceLanguage: source.current
    property alias targetLanguage: target.current

    RowLayout {
        anchors.fill: parent

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

            color: "#1F1F1F"
        }

        LanguageListView {
            id: target

            Layout.fillWidth: true
            Layout.fillHeight: true
         
            languages: root.targetLanguages
        }
    }
}