import QtQuick
import QtQuick.Layouts
import App.Backend
import "../common/controls"
import "components"


Rectangle {
    id: root

    property alias selectionToolActive: btnToolSelection.checked
    property alias visualHintsActive: btnVisualHints.checked
    property alias screensPreviewActive: btnScreensPreview.checked
    property TranslationSelector translationSelector: translationSelector

    implicitWidth: row.implicitWidth + (row.anchors.leftMargin * 2)

    radius: 12
    color: "#070B14"
    border.width: 1
    border.color: "#21242D"

    component Divider: Rectangle {
        width: 2

        Layout.fillHeight: true
        Layout.topMargin: 8
        Layout.bottomMargin: 8

        color: "#1A1C26"
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
            icon.color: hovered || checked ? "#94A3B8" : "#475569"
            icon.width: 22
            icon.height: 22

            background: Rectangle {
                color: parent.hovered || parent.checked ? "#1B1E28" : "transparent"
                radius: 6
            }

            onClicked: {
                checked = !checked;
            }
        }

        Divider {}

        OButton {
            Layout.fillHeight: true
            Layout.preferredWidth: height

            icon.source: "../../../resources/icons/settings.svg"
            icon.color: hovered ? "#94A3B8" : "#475569"
            icon.width: 22
            icon.height: 22

            background: Rectangle {
                color: parent.hovered ? "#1B1E28" : "transparent"
                radius: 6
            }
        }

        Divider {}

        OButton {
            id: btnVisualHints

            Layout.fillHeight: true
            Layout.preferredWidth: height

            checkable: true

            icon.source: "../../../resources/icons/selection.svg"
            icon.color: hovered || checked ? "#94A3B8" : "#475569"
            icon.width: 22
            icon.height: 22

            background: Rectangle {
                color: parent.hovered || parent.checked ? "#1B1E28" : "transparent"
                radius: 6
            }

            onClicked: {
                checked = !checked;
            }
        }

        OButton {
            id: btnScreensPreview

            Layout.fillHeight: true
            Layout.preferredWidth: height

            checkable: true

            icon.source: "../../../resources/icons/selection.svg"
            icon.color: hovered || checked ? "#94A3B8" : "#475569"
            icon.width: 22
            icon.height: 22

            background: Rectangle {
                color: parent.hovered || parent.checked ? "#1B1E28" : "transparent"
                radius: 6
            }

            onClicked: {
                checked = !checked;
            }
        }

        Item {
            Layout.fillWidth: true
        }
    }
}
