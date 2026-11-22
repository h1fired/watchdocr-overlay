import QtQuick
import "qrc:/qml/ui/overlay/components"

KeySequenceField {
    id: root

    property var field
    property var settingValue
    signal committed(var value)

    value: String(root.settingValue ?? "")

    onSequenceCaptured: (sequence) => {
        root.committed(sequence);
        // Capturing overwrites the value, it comes back from the backend
        root.value = Qt.binding(() => String(root.settingValue ?? ""));
    }
}
