import QtQuick

Item {
    id: root

    property var boxes: []
    property var parts: []
    property bool usePerspective: false
    property int rectMargin: 4

    function expandQuad(c, margin) {
        if (margin === 0)
            return c

        return [
            c[0] - margin, c[1] - margin,
            c[2] + margin, c[3] - margin,
            c[4] + margin, c[5] + margin,
            c[6] - margin, c[7] + margin
        ]
    }
}