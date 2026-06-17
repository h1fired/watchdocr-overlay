import QtQuick

Item {
    id: root

    property string providerId: ""
    readonly property Image image: image

    width: image.sourceSize.width
    height: image.sourceSize.height

    Image {
        id: image
    }

    function update() {
        image.source = "image://" + root.providerId +"/current?v=" + Date.now();
    }
}
