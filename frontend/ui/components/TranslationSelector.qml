import QtQuick
import QtQuick.Layouts


Rectangle {
    color: "#000000"

    RowLayout {
        anchors.fill: parent

        spacing: 8

        LanguageListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
        }

        Rectangle {
            Layout.fillHeight: true
            Layout.topMargin: 12
            Layout.bottomMargin: 12
            width: 1

            color: "#1F1F1F"
        }

        LanguageListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
    }
}