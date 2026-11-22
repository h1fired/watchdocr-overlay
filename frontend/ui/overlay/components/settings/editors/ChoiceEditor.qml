import QtQuick
import "qrc:/qml/ui/common/controls"

OComboBox {
    id: root

    property var field
    property var settingValue
    signal committed(var value)

    readonly property var choices: Object.entries(root.field?.options ?? {}).map(
        ([value, text]) => ({ value: value, text: text }))

    function settingIndex() {
        return root.choices.findIndex(c => c.value === String(root.settingValue));
    }

    model: root.choices
    textRole: "text"
    valueRole: "value"
    currentIndex: root.settingIndex()

    onActivated: {
        root.committed(root.currentValue);
        root.currentIndex = Qt.binding(() => root.settingIndex());
    }
}
