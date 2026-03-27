import QtQuick
import "../../common/controls"

OButton {
    id: root

    signal copied()

    implicitWidth: 28
    implicitHeight: 32

    leftPadding: 6
    rightPadding: 6

    text: "Copied to clipboard"
    palette.buttonText: "#475569"

    icon.source: "../../../../resources/icons/copy.svg"
    icon.color: hovered ? "#94A3B8" : "#475569"
    icon.width: 16
    icon.height: 16

    background: Rectangle {
        color: parent.hovered ? "#1B1E28" : "transparent"
        radius: 6
    }

    onClicked: {
        root.copied();
        root.implicitWidth = 144;
        timer.start();
    }

    Timer {
        id: timer

        interval: 2000
        repeat: false

        onTriggered: root.implicitWidth = 28
    }

    Behavior on implicitWidth {
        NumberAnimation {
            duration: 100
            easing.type: Easing.InOutQuad
        }
    }
}