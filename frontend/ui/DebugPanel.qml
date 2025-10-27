import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import App.Backend


Rectangle {
    id: root

    implicitHeight: grid.implicitHeight + 24

    color: "black"

    MouseArea {
        anchors.fill: parent
    }

    GridLayout {
        id: grid

        width: parent.width - 24
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter

        columns: 2

        // OCR backend
        Text {
            Layout.fillWidth: true

            text: "OCR Backend"
            color: "white"
            font.pixelSize: 14
            font.weight: 600
        }

        ComboBox {
            Layout.fillWidth: true

            model: Backend.Ocr.backends
            currentIndex: find(Backend.Ocr.currentBackend)

            onCurrentTextChanged: {
                Backend.Ocr.currentBackend = currentText;
            }
        }

        // Translation backend
        Text {
            Layout.fillWidth: true

            text: "Translation Backend"
            color: "white"
            font.pixelSize: 14
            font.weight: 600
        }

        ComboBox {
            Layout.fillWidth: true
        }
    }
}