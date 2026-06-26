import QtQuick
import QtQuick.Layouts
import QtQuick.Controls.Basic
import App.Backend
import "qrc:/qml/ui/common/controls"
import "qrc:/qml/ui/common/components"

OMessageBoxFrame {
    id: root

    readonly property int titleBarHeight: 52

    implicitWidth: 340
    implicitHeight: column.implicitHeight + titleBarHeight

    title: "Settings"

    color: "#1A1A1A"
    radius: 15
    border.width: 1
    border.color: "#353535"

    ColumnLayout {
        id: column

        width: parent.width
        spacing: 0

        Repeater {
            id: fieldsRepeater

            model: Backend.Settings.fields

            delegate: ColumnLayout {
                id: fieldRow

                required property var modelData
                required property int index

                readonly property bool isFirstInGroup: {
                    if (index === 0) return true;
                    let prev = Backend.Settings.fields[index - 1];
                    return prev.group !== modelData.group;
                }

                Layout.fillWidth: true
                spacing: 0

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 0
                    visible: fieldRow.isFirstInGroup

                    // Top divider (skip for the very first group)
                    Rectangle {
                        Layout.fillWidth: true
                        height: 1
                        color: "#2C2C2C"
                        visible: fieldRow.index !== 0
                    }

                    Text {
                        Layout.fillWidth: true
                        Layout.topMargin: fieldRow.index === 0 ? 14 : 10
                        Layout.bottomMargin: 4
                        Layout.leftMargin: 16

                        text: fieldRow.modelData.group.toUpperCase()

                        font.family: "Segoe UI"
                        font.weight: 700
                        font.pixelSize: 9
                        font.letterSpacing: 1.2
                        color: "#4d4d4d"
                    }
                }

                Item {
                    Layout.fillWidth: true
                    implicitHeight: 44

                    // Hover highlight
                    Rectangle {
                        anchors.fill: parent
                        anchors.leftMargin: 8
                        anchors.rightMargin: 8
                        radius: 6
                        color: fieldHover.containsMouse ? "#222222" : "transparent"

                        Behavior on color {
                            ColorAnimation { duration: 120 }
                        }
                    }

                    MouseArea {
                        id: fieldHover
                        anchors.fill: parent
                        hoverEnabled: true

                        // Toggle booleans on row click (anywhere, not just the switch)
                        onClicked: {
                            if (fieldRow.modelData.type === "bool") {
                                let newVal = !Backend.Settings.values[fieldRow.modelData.key];
                                Backend.Settings.set(fieldRow.modelData.key, newVal);
                            }
                        }
                    }

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 16
                        anchors.rightMargin: 16

                        spacing: 12

                        // Label + description
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 2

                            Text {
                                Layout.fillWidth: true
                                text: fieldRow.modelData.label
                                font.family: "Segoe UI"
                                font.weight: 500
                                font.pixelSize: 12
                                color: "#d4d4d4"
                                elide: Text.ElideRight
                            }

                            Text {
                                Layout.fillWidth: true
                                text: fieldRow.modelData.description
                                visible: text.length > 0
                                font.family: "Segoe UI"
                                font.pixelSize: 10
                                color: "#595959"
                                elide: Text.ElideRight
                                wrapMode: Text.WordWrap
                            }
                        }

                        OSwitch {
                            visible: fieldRow.modelData.type === "bool"
                            enabled: fieldRow.modelData.type === "bool"

                            // Read current value from the live values map.
                            checked: fieldRow.modelData.type === "bool"
                                ? Boolean(Backend.Settings.values[fieldRow.modelData.key])
                                : false

                            onToggled: {
                                Backend.Settings.set(fieldRow.modelData.key, checked);
                            }
                        }

                        TextField {
                            visible: fieldRow.modelData.type !== "bool"
                            enabled: fieldRow.modelData.type !== "bool"

                            implicitWidth: 100
                            implicitHeight: 28

                            text: fieldRow.modelData.type !== "bool"
                                ? String(Backend.Settings.values[fieldRow.modelData.key] ?? "")
                                : ""

                            font.family: "Segoe UI"
                            font.pixelSize: 12
                            color: "#d4d4d4"

                            background: Rectangle {
                                color: "#242424"
                                radius: 6
                                border.width: 1
                                border.color: parent.activeFocus ? "#5a5a5a" : "#2C2C2C"

                                Behavior on border.color {
                                    ColorAnimation { duration: 120 }
                                }
                            }

                            onEditingFinished: {
                                let val = text;
                                if (fieldRow.modelData.type === "int") val = parseInt(val) || 0;
                                if (fieldRow.modelData.type === "float") val = parseFloat(val) || 0.0;
                                Backend.Settings.set(fieldRow.modelData.key, val);
                            }
                        }
                    }
                }
            }
        }

        // Bottom padding
        Item {
            Layout.fillWidth: true
            implicitHeight: 12
        }
    }
}
