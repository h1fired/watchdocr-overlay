import QtQuick
import QtQuick.Layouts


Rectangle {
    color: "#000000"

    property list<string> languages: ([])
    property alias originalLanguage: original.current
    property alias translationLanguage: translation.current

    RowLayout {
        anchors.fill: parent

        spacing: 8

        LanguageListView {
            id: original

            Layout.fillWidth: true
            Layout.fillHeight: true

            languages: root.languages
        }

        Rectangle {
            Layout.fillHeight: true
            Layout.topMargin: 12
            Layout.bottomMargin: 12
            width: 1

            color: "#1F1F1F"
        }

        LanguageListView {
            id: translation

            Layout.fillWidth: true
            Layout.fillHeight: true
         
            languages: root.languages
        }
    }
}