import QtQuick


Item {
    id: root

    implicitWidth: row.implicitWidth 
    implicitHeight: row.implicitHeight 

    Row {
        id: row

        spacing: 3

        Repeater {
            model: [0, 150, 300]
            Rectangle {
                width: 4
                height: 4
                radius: width / 2
                transformOrigin: Item.Center

                SequentialAnimation on scale {
                    loops: Animation.Infinite
                    PauseAnimation { duration: modelData }
                    NumberAnimation { to: 1; duration: 300 }
                    NumberAnimation { to: 0; duration: 300 }
                    PauseAnimation { duration: 600 - modelData }
                }
            }
        }
    }
}