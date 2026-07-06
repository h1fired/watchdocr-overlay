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
            root.pressedKeys = [];
            root.forceActiveFocus();
        }
    }

    Keys.onPressed: function(event) {
        if (!root.capturing)
            return;
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

        const keyName = objects.keyToString(event);
        if (!keyName)
            return;

        parts.push(keyName);
        const sequence = parts.join("+");

        root.value = sequence;
        root.focus = false;
        root.sequenceCaptured(sequence);
    }

    QtObject {
        id: objects

        readonly property var winScanCodes: ({
            2: "1", 3: "2", 4: "3", 5: "4", 6: "5", 7: "6", 8: "7", 9: "8", 10: "9", 11: "0",
            12: "-", 13: "=",
            16: "Q", 17: "W", 18: "E", 19: "R", 20: "T", 21: "Y", 22: "U", 23: "I", 24: "O", 25: "P",
            26: "[", 27: "]",
            30: "A", 31: "S", 32: "D", 33: "F", 34: "G", 35: "H", 36: "J", 37: "K", 38: "L",
            39: ";", 40: "'", 41: "`", 43: "\\",
            44: "Z", 45: "X", 46: "C", 47: "V", 48:"B", 49: "N", 50: "M",
            51: ",", 52: ".", 53: "/"
        })

        function keyToString(event) {
            let table = winScanCodes;

            let code = event.nativeScanCode;
            if (table && table[code] !== undefined)
                return table[code];

            switch (event.key) {
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
                case Qt.Key_Insert: return "Insert";
                case Qt.Key_Home: return "Home";
                case Qt.Key_End: return "End";
                case Qt.Key_PageUp: return "PageUp";
                case Qt.Key_PageDown: return "PageDown";
                case Qt.Key_Left: return "Left";
                case Qt.Key_Right: return "Right";
                case Qt.Key_Up: return "Up";
                case Qt.Key_Down: return "Down";
            }
            return "";
        }
    }
}
