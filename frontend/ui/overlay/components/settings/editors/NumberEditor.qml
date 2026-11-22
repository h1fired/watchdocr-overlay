import QtQuick
import "qrc:/qml/ui/common/controls"

OTextField {
    id: root

    property var field
    property var settingValue
    signal committed(var value)

    readonly property bool integer: Boolean(root.field?.integer)
    readonly property int decimals: {
        if (root.integer || !root.field)
            return 0;
        let parts = String(root.field.step).split(".");
        return parts.length > 1 ? parts[1].length : 0;
    }

    function format(value) {
        let number = Number(value);
        if (value === null || value === undefined || isNaN(number))
            return "";
        return String(parseFloat(number.toFixed(root.decimals)));
    }

    function parse(text) {
        return root.integer ? parseInt(text) : parseFloat(text.replace(",", "."));
    }

    function restore() {
        root.text = Qt.binding(() => root.format(root.settingValue));
    }

    function submit(value) {
        // Range is validated by the backend, error is shown under the field
        root.committed(value);
        root.restore();
    }

    function stepBy(direction) {
        let current = root.parse(root.text);
        if (isNaN(current))
            current = Number(root.settingValue) || 0;

        let next = current + direction * root.field.step;
        if (root.field.min != null)
            next = Math.max(next, root.field.min);
        if (root.field.max != null)
            next = Math.min(next, root.field.max);

        root.submit(Number(next.toFixed(root.decimals)));
    }

    implicitWidth: 100

    text: root.format(root.settingValue)

    validator: RegularExpressionValidator {
        regularExpression: root.integer ? /-?\d*/ : /-?\d*[.,]?\d*/
    }

    onEditingFinished: {
        let value = root.parse(root.text);
        if (isNaN(value) || value === Number(root.settingValue)) {
            root.restore();
            return;
        }
        root.submit(value);
    }

    Keys.onUpPressed: root.stepBy(1)
    Keys.onDownPressed: root.stepBy(-1)

    WheelHandler {
        enabled: root.activeFocus
        onWheel: (event) => root.stepBy(event.angleDelta.y > 0 ? 1 : -1)
    }
}
