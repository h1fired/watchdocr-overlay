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

        area.enabled: controlPanel.selectionToolActive

        Connections {
            target: selectionArea.area

            function onBoxReleased() {
                visualHints.offset = Qt.point(selectionArea.area.box.x, selectionArea.area.box.y);
                visualHints.clear()
            }
        }
    }

    OverlayVisualHints {
        id: visualHints

        anchors.fill: parent

        boxesVisible: (
            !selectionArea.area.loading && !selectionArea.area.selecting &&
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

            visible: !selectionArea.area.selecting

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
