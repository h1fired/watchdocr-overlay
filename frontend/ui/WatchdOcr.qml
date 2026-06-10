import QtQuick
import App.Backend
import "overlay"
import "overlay/components"
import "common/components"

Item {
    id: root

    property bool controlsVisible: true

    OverlayScreensPreview {
        id: screensPreview

        active: root.controlsVisible
    }

    OverlaySelectionArea {
        id: selectionArea

        visible: root.controlsVisible

        anchors.fill: parent

        area.enabled: controlPanel.selectionToolActive

        Connections {
            target: selectionArea.area

            function onPressed() {
                visualHints.boxesVisible = false;
            }

            function onBoxReleased() {
                controlPanel.selectionToolActive = false;
            }
        }
    }

    OverlayVisualHints {
        id: visualHints

        visible: controlPanel.visualHintsActive

        anchors.fill: parent

        offset: Qt.point(selectionArea.area.box.x, selectionArea.area.box.y)
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
        }

        OverlayTextConsole {
            id: textConsole

            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 20

            translationInfo.sourceLanguage: controlPanel.translationSelector.sourceLanguageName
            translationInfo.targetLanguage: controlPanel.translationSelector.targetLanguageName
            translationInfo.sourceShortLanguage: controlPanel.translationSelector.sourceLanguage
            translationInfo.targetShortLanguage: controlPanel.translationSelector.targetLanguage
        }
    }
}
