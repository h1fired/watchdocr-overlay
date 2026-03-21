import QtQuick
import QtQuick.Window
import QtQuick.Controls


Window {
    id: window

    visible: true

    width: 800
    height: 600

    title: "OCR Overlay"
    
    color: "gray"

    Loader {
        id: contentLoader
        objectName: "windowContentLoader"

        anchors.fill: parent

        source: "Component.qml"
    }
}
