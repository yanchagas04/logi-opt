import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Window {
    visible: true
    width: 640
    height: 480
    title: "Hello world"

    readonly property string text: "Hello world!"

    function setNumber() {
        text.text = Math.round(Math.random() * 100)
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 24

        Text {
            id: text
            text: "This is a QML example"
            Layout.alignment: Qt.AlignHCenter
        }
        Button {
            text: "Click me!"
            Layout.alignment: Qt.AlignHCenter
            onClicked: setNumber()
        }
    }
}