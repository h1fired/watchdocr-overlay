pragma Singleton
import QtQuick

QtObject {
    id: root

    property var _windowPopup

    function setup(windowPopup) {
        root._windowPopup = windowPopup;
    }

    function showWindowPopup(component) {
        root._windowPopup.contentObject = component;
    }

    function closeWindowPopup() {
        root._windowPopup.clear();
    }
}
