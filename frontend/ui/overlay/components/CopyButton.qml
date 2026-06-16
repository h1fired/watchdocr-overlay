import QtQuick
import "../../common/controls"

OButton {
    id: root

    signal copied()

    implicitWidth: 32
    implicitHeight: 32

    leftPadding: 6
    rightPadding: 6

    text: "Copied to clipboard"
    palette.buttonText: "#D2D2D2"

    icon.source: "../../../../resources/icons/copy.svg"
    icon.color: "#D2D2D2"
    icon.width: 18
    icon.height: 18

    background: Rectangle {
        color: parent.hovered ? "#292929" : "transparent"
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

        onTriggered: root.implicitWidth = 32
    }

    Behavior on implicitWidth {
        NumberAnimation {
            duration: 100
            easing.type: Easing.InOutQuad
        }
    }
}