import QtQuick 2.15
import QtQuick.Controls.Basic 2.15
import QtQuick.Layouts 2.15


Item {
    id: root
    property string text
    property bool maximized: false

    signal copied()

    // Logic
    function reset() {
        root.maximized = false;
        textBlock.clear();
    }

    function runCopied() {
        btnCopy.width = btnCopy.implicitWidth;
        copyTimer.start();
    }

    Timer {
        id: copyTimer
        interval: 2000
        repeat: false
        onTriggered: btnCopy.width = 36
    }

    onMaximizedChanged: {
        if (root.maximized) {
            root.width = 760
            root.height = 420
        } else {
            root.width = 560
            root.height = 120
        }
    }

    // UI
    width: 560
    height: 120

    Rectangle {
        anchors.fill: parent
        color: "#000000"
        radius: 6
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 4
            Row {
                Layout.alignment: Qt.AlignRight
                spacing: 8
                Button {
                    id: btnCopy

                    width: 36
                    height: 36

                    text: "Copied to clipboard"
                    icon.source: "../../../resources/icons/copy.svg"
                    icon.color: "#9D9D9D"
                    icon.width: 18
                    icon.height: 18
                    palette.buttonText: "#9D9D9D"

                    background: Rectangle {
                        color: btnCopy.hovered ? "#1B1B1B" : "transparent"
                        radius: 3
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor 
                        onPressed: (mouse) => {
                            mouse.accepted = false
                        }
                    }

                    Behavior on width {
                        NumberAnimation {
                            duration: 100
                            easing.type: Easing.InOutQuad
                        }
                    }

                    onClicked: {
                        root.copied();
                    }
                }
                Button {
                    id: btnResize

                    width: 36
                    height: 36

                    icon.source: root.maximized ? "../../../resources/icons/minimize.svg" : "../../../resources/icons/maximize.svg"
                    icon.color: "#9D9D9D"
                    icon.width: 18
                    icon.height: 18

                    background: Rectangle {
                        color: btnResize.hovered ? "#1B1B1B" : "transparent"
                        radius: 3
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor 
                        onPressed: (mouse) => {
                            mouse.accepted = false
                        }
                    }

                    onClicked: {
                        root.maximized = !root.maximized
                    }
                }
            }

            ScrollView {
                id: scrollView

                Layout.fillWidth: true
                Layout.fillHeight: true

                ScrollBar.horizontal: ScrollBar {
                    policy: ScrollBar.AlwaysOff
                }

                TextArea {
                    id: textBlock

                    anchors.fill: scrollView
                    textFormat: TextEdit.MarkdownText

                    color: "#FFFFFF"
                    selectionColor: "#073BA5"
                    wrapMode: Text.WordWrap
                    font.pointSize: 12
                    readOnly: true

                    text: root.text
                }
            }

        }
    }

    Behavior on width {
        NumberAnimation {
            duration: 200
            easing.type: Easing.InOutQuad
        }
    }

    Behavior on height {
        NumberAnimation {
            duration: 200
            easing.type: Easing.InOutQuad
        }
    }
}