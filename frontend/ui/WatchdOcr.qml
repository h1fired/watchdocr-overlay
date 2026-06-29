import QtQuick
import App.Backend
import "qrc:/qml/ui/overlay"
import "qrc:/qml/ui/overlay/components"
import "qrc:/qml/ui/common/components"

Item {
    id: root

    property bool controlsVisible: true
    readonly property string mode: controlPanel.mode

    MouseArea {
        anchors.fill: parent
    }

    OverlayScreensPreview {
        id: screensPreview

        active: root.controlsVisible && controlPanel.screensPreviewActive
    }

    OverlaySelectionArea {
        id: selectionArea

        visible: root.controlsVisible && !screensPreview.grabbing

        anchors.fill: parent

        area.mouseSelectionActive: controlPanel.selectionToolActive

        Connections {
            target: selectionArea.area

            function onBoxSelected() {
                visualHints.offset = Qt.point(
                    selectionArea.area.box.x,
                    selectionArea.area.box.y
                );
                visualHints.clear();

                controlPanel.selectionToolActive = false;
            }
        }
    }

    OverlayVisualHints {
        id: visualHints

        anchors.fill: parent
    }

    ScreenArea {
        id: screenArea

        visible: root.controlsVisible

        monitor: 0

        OverlayControlPanel {
            id: controlPanel

            y: 20

            anchors.horizontalCenter: parent.horizontalCenter

            height: 44

            onScreensPreviewActiveChanged: {
                if (screensPreviewActive) {
                    screensPreview.updatePreview(true);
                }
            }
        }

        OverlayTextConsole {
            id: textConsole

            opacity: controlPanel.selectionToolActive ? 0.5 : 1.0

            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 20

            translationInfo.sourceLanguage: controlPanel.translationSelector.sourceLanguageName
            translationInfo.targetLanguage: controlPanel.translationSelector.targetLanguageName
        }
    }

    onControlsVisibleChanged: {
        if (controlsVisible) {
            modeController.cleanUp();
        }
    }

    Item {
        id: modeController

        state: "onetime"
        states: [
            State {
                name: "onetime"
                when: root.mode === "onetime"

                PropertyChanges {
                    target: visualHints
                    boxesVisible: (
                        !selectionArea.area.loading && !selectionArea.area.selecting &&
                        (!root.controlsVisible && Backend.Settings.values.visual_hints_show_as_overlay ||
                        root.controlsVisible && Backend.Settings.values.visual_hints_show)
                    )
                }

                PropertyChanges {
                    target: selectionArea
                    loading: Backend.Processor.recognizerStatus === 1
                }

                PropertyChanges {
                    target: textConsole
                    visible: !selectionArea.selecting
                    enableSizeAdaptivity: true
                    enableProcessingStageLoader: true
                }
            },
            State {
                name: "live"
                when: root.mode === "live"

                PropertyChanges {
                    target: visualHints
                    boxesVisible: (
                        !selectionArea.area.selecting &&
                        (!root.controlsVisible && Backend.Settings.values.visual_hints_show_as_overlay ||
                        root.controlsVisible && Backend.Settings.values.visual_hints_show)
                    )
                }

                PropertyChanges {
                    target: selectionArea
                    loading: true
                }

                PropertyChanges {
                    target: textConsole
                    visible: !selectionArea.selecting
                    enableSizeAdaptivity: false
                    enableProcessingStageLoader: false
                }
            },
        ]

        function cleanUp() {
            if (state == "onetime") {
                selectionArea.cleanUp();
                controlPanel.selectionToolActive = true;
                visualHints.clear();
            }
        }
    }

    Connections {
        target: Backend.Settings

        property string previousHotkey: ""

        function onSettingsChanged() {
            let hotkey = Backend.Settings.values.overlay_toggle_hotkey;
            if (hotkey !== previousHotkey) {
                Backend.General.changeOverlayToggleHotkey(hotkey);
                previousHotkey = hotkey;
            }
        }
    }

    Component.onCompleted: {
        modeController.cleanUp();
    }
}
