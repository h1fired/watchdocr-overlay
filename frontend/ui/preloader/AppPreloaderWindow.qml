import QtQuick
import QtQuick.Window


Window {
    id: window

    visible: true

    flags: Qt.FramelessWindowHint
    color: "transparent"

    width: preloader.implicitWidth
    height: preloader.implicitHeight

    AppPreloader {
        id: preloader
    }
}