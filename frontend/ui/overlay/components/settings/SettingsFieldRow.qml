import QtQuick
import QtQuick.Layouts
import App.Backend
import "qrc:/qml/ui/common/controls"

// One Setting: label, description, messages and the editor picked by type.
// Editor contract: `field`, `settingValue` properties and `committed(value)` signal
Item {
    id: root

    required property var field
    required property string owner

    property string error: ""

    readonly property var editors: ({
        "bool": "BoolEditor.qml",
        "choice": "ChoiceEditor.qml",
        "number": "NumberEditor.qml",
        "text": "TextEditor.qml",
        "secret": "SecretEditor.qml",
        "hotkey": "HotkeyEditor.qml",
    })

    readonly property var values: Backend.Settings.ownerValues[root.owner] ?? ({})
    readonly property var value: root.values[root.field.key]
    readonly property bool fieldEnabled: !root.field.enabled_if
        || Boolean(root.values[root.field.enabled_if])
    readonly property bool restartPending: Backend.Settings.restartPending.indexOf(
        root.owner + "/" + root.field.key) !== -1

    function commit(newValue) {
        root.error = Backend.Settings.setValue(root.owner, root.field.key, newValue);
    }

    implicitHeight: Math.max(44, content.implicitHeight + 14)
    opacity: root.fieldEnabled ? 1.0 : 0.4

    onValueChanged: root.error = ""

    // Hover highlight
    Rectangle {
        anchors.fill: parent
        anchors.leftMargin: 8
        anchors.rightMargin: 8
        radius: 6
        color: rowHover.containsMouse && root.fieldEnabled ? "#222222" : "transparent"
    }

    MouseArea {
        id: rowHover

        anchors.fill: parent
        hoverEnabled: true

        // Toggle booleans on row click (anywhere, not just the switch)
        onClicked: {
            if (root.fieldEnabled && root.field.type === "bool")
                root.commit(!Boolean(root.value));
        }
    }

    RowLayout {
        id: content

        anchors.left: parent.left
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        anchors.leftMargin: 16
        anchors.rightMargin: 16

        spacing: 12

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2

            OText {
                Layout.fillWidth: true
                text: root.field.label
                font.weight: 500
                font.pixelSize: 12
                color: "#d4d4d4"
                elide: Text.ElideRight
            }

            OText {
                Layout.fillWidth: true
                text: root.field.description
                visible: text.length > 0
                font.pixelSize: 10
                color: "#595959"
                wrapMode: Text.WordWrap
            }

            OText {
                Layout.fillWidth: true
                text: "Applies after restart"
                visible: root.restartPending
                font.pixelSize: 10
                color: "#C9A44C"
            }

            OText {
                Layout.fillWidth: true
                text: root.error
                visible: text.length > 0
                font.pixelSize: 10
                color: "#E06C6C"
                wrapMode: Text.WordWrap
            }
        }

        Loader {
            id: editorLoader

            Layout.alignment: Qt.AlignVCenter
            enabled: root.fieldEnabled

            source: Qt.resolvedUrl(
                "editors/" + (root.editors[root.field.type] ?? "TextEditor.qml"))

            onLoaded: {
                item.field = Qt.binding(() => root.field);
                item.settingValue = Qt.binding(() => root.value);
            }
        }
    }

    Connections {
        target: editorLoader.item
        ignoreUnknownSignals: true

        function onCommitted(value) {
            root.commit(value);
        }
    }
}
