import QtQuick
import "qrc:/qml/ui/common/controls"

OTextField {
    id: root

    property var field
    property var settingValue
    signal committed(var value)

    function settingText() {
        return String(root.settingValue ?? "");
    }

    text: root.settingText()

    onEditingFinished: {
        if (root.text !== root.settingText())
            root.committed(root.text);
        root.text = Qt.binding(() => root.settingText());
    }
}
