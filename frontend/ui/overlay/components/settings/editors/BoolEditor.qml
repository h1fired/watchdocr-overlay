import QtQuick
import "qrc:/qml/ui/common/controls"

OSwitch {
    id: root

    property var field
    property var settingValue
    signal committed(var value)

    checked: Boolean(root.settingValue)

    onToggled: {
        root.committed(root.checked);
        // Toggling breaks the binding, value comes back from the backend
        root.checked = Qt.binding(() => Boolean(root.settingValue));
    }
}
