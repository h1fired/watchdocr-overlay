import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts


Item {
    id: root

    width: parent.width - 2
    height: maximized ? parent.height - 2 : btnTranslate.height + 6

    anchors.margins: 1

    clip: true

    property bool maximized: false
    property alias sourceLanguage: translationSelector.sourceLanguage
    property alias targetLanguage: translationSelector.targetLanguage
    property list<string> sourceLanguages: ([])
    property list<string> targetLanguages: ([])

    Button {
        id: btnTranslate

        y: 3

        height: 28

        anchors.horizontalCenter: parent.horizontalCenter

        text: root.sourceLanguage + " -> " + root.targetLanguage
        font.weight: 600
        font.pixelSize: 12
        palette.buttonText: "#FFFFFF"
        background: Rectangle {
            color: btnTranslate.hovered || root.maximized ? "#1B1B1B" : "transparent"
            radius: height / 2
        }

        onClicked: {
            root.maximized = !root.maximized;
        }
    }

    TranslationSelector {
        id: translationSelector

        y: 36

        width: parent.width - 20
        height: parent.height - 36

        anchors.horizontalCenter: parent.horizontalCenter

        sourceLanguages: root.sourceLanguages
        targetLanguages: root.targetLanguages
    }
}