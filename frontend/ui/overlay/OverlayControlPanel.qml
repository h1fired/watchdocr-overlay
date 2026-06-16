import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import App.Backend
import "../common/controls"
import "components"


Rectangle {
    id: root

    property alias selectionToolActive: btnToolSelection.checked
    property alias visualHintsActive: menuVisualHints.showEnabled
    property alias visualHintsAsOverlayActive: menuVisualHints.asOverlayEnabled
    property alias screensPreviewActive: btnScreensPreview.checked
    property TranslationSelector translationSelector: translationSelector

    implicitWidth: row.implicitWidth + (row.anchors.leftMargin * 2)

    radius: 15
    color: "#1A1A1A"
    border.width: 1
    border.color: "#353535"

    onVisualHintsActiveChanged: {
        Backend.Settings.set("visual_hints_show", visualHintsActive);
    }

    onVisualHintsAsOverlayActiveChanged: {
        Backend.Settings.set("visual_hints_show_as_overlay", visualHintsAsOverlayActive);
    }

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

            visible: false

            Layout.fillHeight: true
            Layout.topMargin: 2
            Layout.bottomMargin: 2

            onCurrentModeChanged: {
                Backend.Processor.onModeChanged(currentMode);
                btnPlayPause.visible = currentMode == "live";
            }
        }

        Divider {
            visible: modeSelector.currentMode == "live";
        }

        OButton {
            id: btnPlayPause

            Layout.preferredWidth: 80
            Layout.fillHeight: true

            text: "Play"
            font.family: "Segoe UI"
            font.weight: 700
            font.pixelSize: 12

            icon.color: "#FAF9FF"
            icon.width: 12
            icon.height: 12

            background: Rectangle {
                color: parent.hovered ? "#7C3AED" : "#8B5CF6"
                radius: 6
            }

            state: Backend.Processor.active ? "pause" : "run"
            states: [
                State {
                    name: "run"
                    PropertyChanges {
                        target: btnPlayPause
                        text: "Run"
                        icon.source: "../../../resources/icons/play.svg"
                        background.color: btnPlayPause.hovered ? "#7C3AED" : "#8B5CF6"
                    }
                },
                State {
                    name: "pause"
                    PropertyChanges {
                        target: btnPlayPause
                        text: "Pause"
                        icon.source: "../../../resources/icons/pause.svg"
                        background.color: "#1E293B"
                    }
                }
            ]

            onClicked: {
                Backend.Processor.onPlayPauseButtonClick(state);
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

            icon.source: "../../../resources/icons/selection.svg"
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

        // OButton {
        //     Layout.fillHeight: true
        //     Layout.preferredWidth: height

        //     icon.source: "../../../resources/icons/settings.svg"
        //     icon.color: "#E9E9E9"
        //     icon.width: 24
        //     icon.height: 24

        //     background: Rectangle {
        //         color: parent.hovered ? "#2C2C2C" : "transparent"
        //         radius: 6
        //     }

        //     ToolTip.text: "Settings"
        //     ToolTip.visible: hovered
        //     ToolTip.delay: 1000
        // }

        // Divider {}

        VisualHintsToolButtonMenu {
            id: menuVisualHints

            Layout.fillHeight: true
            Layout.preferredWidth: height
        }

        OButton {
            id: btnScreensPreview

            Layout.fillHeight: true
            Layout.preferredWidth: height

            checkable: true

            icon.source: "../../../resources/icons/eye.svg"
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

    Connections {
        target: translationSelector

        function onSourceLanguageChanged() {
            Backend.Settings.set("source_language", translationSelector.sourceLanguage);
        }

        function onTargetLanguageChanged() {
            Backend.Settings.set("target_language", translationSelector.targetLanguage);
        }
    }

    Component.onCompleted: {
        visualHintsActive = Backend.Settings.values.visual_hints_show;
        visualHintsAsOverlayActive = Backend.Settings.values.visual_hints_show_as_overlay;
        btnScreensPreview.checked = Backend.Settings.values.screens_preview_enabled;
        translationSelector.sourceLanguage = Backend.Settings.values.source_language;
        translationSelector.targetLanguage = Backend.Settings.values.target_language;
    }
}
