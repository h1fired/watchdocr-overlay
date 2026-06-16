import QtQuick
import App.Backend
import "overlay"
import "overlay/components"
import "common/components"

Item {
    id: root

    property bool controlsVisible: true

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

        area.enabled: controlPanel.selectionToolActive

        Connections {
            target: selectionArea.area

            function onBoxReleased() {
                controlPanel.selectionToolActive = false;
                visualHints.offset = Qt.point(selectionArea.area.box.x, selectionArea.area.box.y);
            }
        }
    }

    OverlayVisualHints {
        id: visualHints

        anchors.fill: parent
            
        boxesVisible: (
            !selectionArea.area.loading && !controlPanel.selectionToolActive &&
            (!root.controlsVisible && controlPanel.visualHintsAsOverlayActive ||
            root.controlsVisible && controlPanel.visualHintsActive)
        )
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

            visible: !controlPanel.selectionToolActive

            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 20

            translationInfo.sourceLanguage: controlPanel.translationSelector.sourceLanguageName
            translationInfo.targetLanguage: controlPanel.translationSelector.targetLanguageName
        }
    }

    function cleanUp() {
        selectionArea.cleanUp();
        controlPanel.selectionToolActive = true;
    }

    onControlsVisibleChanged: {
        if (controlsVisible) {
            cleanUp();
        }
    }

    Component.onCompleted: {
        cleanUp();
    }
}
