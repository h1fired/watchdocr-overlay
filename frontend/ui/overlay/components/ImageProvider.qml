import QtQuick


Item {
    id: root

    property string providerId: "" 

    Image {
        id: image
    }

    function update() {
        image.source = "image://" + root.providerId +"/current?v=" + Date.now();
    }
}
