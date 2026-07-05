import QtQuick
import QtQuick.Window


Window {
    id: window

    width: preloader.implicitWidth
    height: preloader.implicitHeight

    AppPreloader {
        id: preloader
    }
}