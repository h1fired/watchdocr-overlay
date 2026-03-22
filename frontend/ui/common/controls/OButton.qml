import QtQuick
import QtQuick.Controls.Basic


Button {
    id: root

    padding: 0

    MouseArea {
        anchors.fill: parent
        
        cursorShape: Qt.PointingHandCursor

        onClicked: {
            root.clicked();
        }
    }
}
