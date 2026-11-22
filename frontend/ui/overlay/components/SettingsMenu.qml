import QtQuick
import QtQuick.Layouts
import App.Backend
import "qrc:/qml/ui/common/components"
import "qrc:/qml/ui/overlay/components/settings"

OMessageBoxFrame {
    id: root

    readonly property int titleBarHeight: 52

    readonly property var sections: Backend.Settings.sections
    property string currentSectionId: ""
    readonly property var currentSection: {
        let found = root.sections.find(s => s.id === root.currentSectionId);
        return found ?? (root.sections.length ? root.sections[0] : null);
    }

    implicitWidth: 560
    implicitHeight: content.implicitHeight + titleBarHeight + 1

    title: "Settings"

    color: "#1A1A1A"
    radius: 15
    border.width: 1
    border.color: "#353535"

    onVisibleChanged: {
        Backend.General.blockOverlayToggleHotkey(visible);
    }

    // Layout computes its own implicit size, so fixed height is set on a wrapper
    Item {
        id: content

        width: parent.width
        height: implicitHeight
        implicitHeight: 400

        RowLayout {
            anchors.fill: parent

            spacing: 0

            SettingsNavigation {
                Layout.preferredWidth: 170
                Layout.fillHeight: true

                model: root.sections
                currentSectionId: root.currentSection?.id ?? ""

                onSectionSelected: (sectionId) => root.currentSectionId = sectionId
            }

            Rectangle {
                Layout.preferredWidth: 1
                Layout.fillHeight: true
                Layout.bottomMargin: 12
                color: "#2C2C2C"
            }

            SettingsSectionPage {
                Layout.fillWidth: true
                Layout.fillHeight: true

                section: root.currentSection
            }
        }
    }
}
