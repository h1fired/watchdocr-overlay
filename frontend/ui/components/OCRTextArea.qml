import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "common"


Item {
    id: root

    implicitWidth: root.maximized ? maximizedWidth : minimizedWidth
    implicitHeight: root.maximized ? maximizedHeight : minimizedHeight

    property string text
    property bool loading: false
    property bool maximized: false
    property int minimizedWidth: 560
    property int minimizedHeight: 120
    property int maximizedWidth: 760
    property int maximizedHeight: 420

    signal copied()

    states: [
        State { name: "result" },
        State { name: "status" }
    ]
    state: "result"

    MouseArea {
        anchors.fill: parent
    }

    Rectangle {
        anchors.fill: parent

        color: "#000000"
        radius: 6
        border {
            width: 1
            color: "#1F1F1F"
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 4

            Row {
                Layout.alignment: Qt.AlignRight
                spacing: 0

                Button {
                    id: btnCopy

                    width: 32
                    height: 32

                    enabled: root.state == "result"

                    text: "Copied to clipboard"
                    icon {
                        source: "../../../resources/icons/copy.svg"
                        color: btnCopy.enabled ? "#9D9D9D" : "#646464"
                        width: 18
                        height: 18
                    }
                    palette.buttonText: "#9D9D9D"
                    background: Rectangle {
                        color: btnCopy.hovered && btnCopy.enabled ? "#1B1B1B" : "transparent"
                        radius: 3
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor

                        onPressed: (mouse) => {
                            mouse.accepted = false;
                        }
                    }

                    Behavior on width {
                        NumberAnimation {
                            duration: 100
                            easing.type: Easing.InOutQuad
                        }
                    }
                }

                Button {
                    id: btnResize

                    width: 32
                    height: 32

                    icon {
                        source: root.maximized ? "../../../resources/icons/minimize.svg" : "../../../resources/icons/maximize.svg"
                        color: "#9D9D9D"
                        width: 18
                        height: 18
                    }
                    background: Rectangle {
                        color: btnResize.hovered ? "#1B1B1B" : "transparent"
                        radius: 3
                    }

                    onClicked: {
                        root.maximized = !root.maximized
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor

                        onPressed: (mouse) => {
                            mouse.accepted = false;
                        }
                    }

                }
            }

            Flickable {
                id: flickable

                Layout.fillWidth: true
                Layout.fillHeight: true
                contentHeight: Math.max(textBlock.implicitHeight, height)
                clip: true
                boundsBehavior: Flickable.StopAtBounds

                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                }

                TextArea {
                    id: textBlock

                    anchors.fill: parent
                    topPadding: 6
                    bottomPadding: 6
                    leftPadding: root.maximized
                        ? root.loading ? 50 : 20
                        : root.loading ? 40 : 10
                    rightPadding: root.maximized ? 20 : 10

                    text: root.text
                    selectionColor: "#073BA5"
                    wrapMode: Text.WordWrap
                    textFormat: root.state === "status" ? TextEdit.MarkdownText : TextEdit.AutoText
                    font.pointSize: 12
                    color: "#FFFFFF"
                    readOnly: true

                    Behavior on leftPadding {
                        NumberAnimation {
                            duration: 200
                            easing.type: Easing.InOutQuad
                        }
                    }

                    Behavior on rightPadding {
                        NumberAnimation {
                            duration: 200
                            easing.type: Easing.InOutQuad
                        }
                    }
                }

                CAnimatedImage {
                    x: root.maximized ? 20 : 10
                    y: 9

                    width: 16
                    height: 16

                    visible: root.state == "status" && root.loading
                    running: root.state == "status" && root.loading

                    source: "resources/icons/a_loading.svg"
                    color: "#C3C3C3"

                    Behavior on x {
                        NumberAnimation {
                            duration: 200
                            easing.type: Easing.InOutQuad
                        }
                    }
                }
            }
        }
    }

    Behavior on implicitWidth {
        NumberAnimation {
            duration: 200
            easing.type: Easing.InOutQuad
        }
    }

    Behavior on implicitHeight {
        NumberAnimation {
            duration: 200
            easing.type: Easing.InOutQuad
        }
    }

    Timer {
        id: copyTimer

        interval: 2000
        repeat: false

        onTriggered: btnCopy.width = 36
    }

    Connections {
        target: btnCopy

        function onClicked() {
            root.copied();
        }
    }

    function reset() {
        root.maximized = false;
        textBlock.clear();
    }

    function runCopied() {
        btnCopy.width = btnCopy.implicitWidth;
        copyTimer.start();
    }
}
