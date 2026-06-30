import QtQuick
import QtQuick.Controls.Basic

FocusScope {
    id: root

    property string value: ""
    signal sequenceCaptured(string sequence)

    readonly property bool capturing: activeFocus
    property var pressedKeys: []

    implicitWidth: 140
    implicitHeight: 28

    Rectangle {
        anchors.fill: parent
        radius: 6
        color: "#242424"
        border.width: 1
        border.color: root.capturing ? "#75A0FF" : (mouseArea.containsMouse ? "#5a5a5a" : "#2C2C2C")

        Behavior on border.color {
            ColorAnimation { duration: 120 }
        }

        Text {
            anchors.centerIn: parent
            text: root.capturing ? "Press keys…" : (root.value.length > 0 ? root.value : "Unset")
            font.family: "Segoe UI"
            font.pixelSize: 12
            color: root.capturing ? "#75A0FF" : "#d4d4d4"
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true

        onClicked: {
            // root.capturing = true;
            root.pressedKeys = [];
            root.forceActiveFocus();
        }
    }

    Keys.onPressed: function(event) {
        if (!root.capturing) return;
        event.accepted = true;

        // Escape cancels capture without changing the value
        if (event.key === Qt.Key_Escape) {
            root.focus = false;
            return;
        }

        let parts = [];
        if (event.modifiers & Qt.ControlModifier) parts.push("Ctrl");
        if (event.modifiers & Qt.ShiftModifier) parts.push("Shift");
        if (event.modifiers & Qt.AltModifier) parts.push("Alt");
        if (event.modifiers & Qt.MetaModifier) parts.push("Meta");

        // Ignore bare modifier presses — wait for a real key
        const modifierKeys = [Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta];
        if (modifierKeys.indexOf(event.key) !== -1) {
            return;
        }

        const keyName = keyToString(event.key);
        if (!keyName)
            return;

        parts.push(keyName);
        const sequence = parts.join("+");

        root.value = sequence;
        root.focus = false;
        root.sequenceCaptured(sequence);
    }

    function keyToString(key) {
        if (key >= Qt.Key_A && key <= Qt.Key_Z)
            return String.fromCharCode(key);

        if (key >= Qt.Key_0 && key <= Qt.Key_9)
            return String.fromCharCode(key);

        switch (key) {
        case Qt.Key_F1: return "F1";
        case Qt.Key_F2: return "F2";
        case Qt.Key_F3: return "F3";
        case Qt.Key_F4: return "F4";
        case Qt.Key_F5: return "F5";
        case Qt.Key_F6: return "F6";
        case Qt.Key_F7: return "F7";
        case Qt.Key_F8: return "F8";
        case Qt.Key_F9: return "F9";
        case Qt.Key_F10: return "F10";
        case Qt.Key_F11: return "F11";
        case Qt.Key_F12: return "F12";
        case Qt.Key_Space: return "Space";
        case Qt.Key_Tab: return "Tab";
        case Qt.Key_Return:
        case Qt.Key_Enter: return "Enter";
        case Qt.Key_Backspace: return "Backspace";
        case Qt.Key_Delete: return "Delete";
        default:
            return "";
        }
    }
}
