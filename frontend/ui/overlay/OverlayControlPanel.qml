import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import App.Backend
import App.Gui
import "qrc:/qml/ui/common/controls"
import "qrc:/qml/ui/overlay/components"

Rectangle {
    id: root

    property alias selectionToolActive: btnToolSelection.checked
    property alias screensPreviewActive: btnScreensPreview.checked
    property TranslationSelector translationSelector: translationSelector
    readonly property string mode: modeSelector.currentMode

    implicitWidth: row.implicitWidth + (row.anchors.leftMargin * 2)

    radius: 15
    color: "#1A1A1A"
    border.width: 1
    border.color: "#353535"



    component Divider: Rectangle {
        width: 2

        Layout.fillHeight: true
        Layout.topMargin: 8
        Layout.bottomMargin: 8

        color: "#2F2F2F"
    }

    MouseArea {
        anchors.fill: parent
    }

    RowLayout {
        id: row

        anchors.fill: parent
        anchors.margins: 6
        anchors.leftMargin: 12
        anchors.rightMargin: 12

        spacing: 8

        ActivityBar {
            id: activityBar

            state: Backend.Processor.active ? "live" : "idle"

            Layout.fillHeight: true
            Layout.topMargin: 4
            Layout.bottomMargin: 4
        }

        Divider {}

        TranslationSelector {
            id: translationSelector

            Layout.fillHeight: true
            Layout.topMargin: 4
            Layout.bottomMargin: 4

            sourceLanguages: Backend.Translation.sourceLanguages
            targetLanguages: Backend.Translation.targetLanguages

            onSourceLanguageChanged: {
                Backend.Translation.setSourceLanguage(sourceLanguage);
            }

            onTargetLanguageChanged: {
                Backend.Translation.setTargetLanguage(targetLanguage);
            }

            onSearchQueryChanged: {
                Backend.Translation.setLanguageSearchQuery(searchQuery);
            }
        }

        Divider {}

        ModeSelector {
            id: modeSelector

            Layout.fillHeight: true

            onCurrentModeChanged: {
                Backend.Processor.onModeChanged(currentMode);
            }
        }

        Divider {
            visible: false
        }

        OButton {
            id: btnToolSelection

            Layout.fillHeight: true
            Layout.preferredWidth: height

            checkable: true

            icon.source: "qrc:/qml/resources/icons/selection.svg"
            icon.color: "#E9E9E9"
            icon.width: 22
            icon.height: 22

            background: Rectangle {
                color: parent.hovered || parent.checked ? "#2C2C2C" : "transparent"
                radius: 6
            }

            ToolTip.text: "Selection tool"
            ToolTip.visible: hovered
            ToolTip.delay: 1000


            onClicked: {
                checked = !checked;
            }
        }

        Divider {}

        OButton {
            id: btnSettings

            Layout.fillHeight: true
            Layout.preferredWidth: height

            icon.source: "qrc:/qml/resources/icons/settings.svg"
            icon.color: "#E9E9E9"
            icon.width: 24
            icon.height: 24

            background: Rectangle {
                color: parent.hovered || parent.checked ? "#2C2C2C" : "transparent"
                radius: 6
            }

            ToolTip.text: "Settings"
            ToolTip.visible: hovered
            ToolTip.delay: 1000

            onClicked: {
                Gui.showWindowPopup(settingsMenu);
            }
        }



        OButton {
            id: btnScreensPreview

            Layout.fillHeight: true
            Layout.preferredWidth: height

            checkable: true

            icon.source: "qrc:/qml/resources/icons/eye.svg"
            icon.color: "#E9E9E9"
            icon.width: 20
            icon.height: 20

            background: Rectangle {
                color: parent.hovered || parent.checked ? "#2C2C2C" : "transparent"
                radius: 6
            }

            ToolTip.text: "Toggle preview"
            ToolTip.visible: hovered
            ToolTip.delay: 1000

            onClicked: {
                checked = !checked;
            }

            onCheckedChanged: {
                Backend.Settings.set("screens_preview_enabled", checked);
            }
        }

        Item {
            Layout.fillWidth: true
        }
    }

    SettingsMenu {
        id: settingsMenu

        visible: false
    }

    Connections {
        target: translationSelector

        function onSourceLanguageChanged() {
            Backend.Settings.set("source_language", translationSelector.sourceLanguage);
        }

        function onTargetLanguageChanged() {
            Backend.Settings.set("target_language", translationSelector.targetLanguage);
        }
    }

    // Sync screensPreview button from settings when changed externally (e.g. SettingsMenu).
    Connections {
        target: Backend.Settings

        function onSettingsChanged() {
            btnScreensPreview.checked = Backend.Settings.values.screens_preview_enabled;
        }
    }

    Component.onCompleted: {
        btnScreensPreview.checked = Backend.Settings.values.screens_preview_enabled;
        translationSelector.sourceLanguage = Backend.Settings.values.source_language;
        translationSelector.targetLanguage = Backend.Settings.values.target_language;
    }
}
