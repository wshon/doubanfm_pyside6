import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

import MusicUtil

ApplicationWindow {
    id: root

    width: 640
    height: 240
    visible: true
    title: "Proxy Tool"

    Row {
        anchors.fill: parent
        spacing: 6
        Item {
            width: 120; height: 120
            Image {
                id: musicImage
                width: 120; height: 120
                anchors.margins: 10
                source: ""
                asynchronous: true
                cache: false
                fillMode: Image.PreserveAspectFit
            }
        }
        Item {
            width: 620; height: 120
            Column {

                Text {
                    id: musicTitle
                    font.pixelSize: 25
                }
                Text {
                    id: musicArtist
                    font.pixelSize: 15
                }

                Row {
                    Label {
                        id: musicPosition
                        text: "00:00"
                    }
                    Label { text: "/" }
                    Label {
                        id: musicDuration
                        text: "00:00"
                    }
                }
                Slider {
                    id: musicProcess
                    width: parent.width
                }
                Row {
                    Button {
                        text: "Pause"
                        onClicked: musicTool.pauseMusic()
                    }
                    Button {
                        text: "Play"
                        onClicked: musicTool.playMusic()
                    }
                    Button {
                        text: "Next Music"
                        onClicked: musicTool.nextMusic()
                    }
                    Button {
                        text: "+10S"
                        onClicked: musicTool.skip10s()
                    }
                }
                Label {
                    id: musicUrl
                    text: "url"
                }
                Label {
                    id: musicPic
                    text: "pic"
                }
            }
        }

    }

//        Rectangle {
//            color: "red";
//            width: 50; height: 50
//        }
//
//        TextField  {
//            id: input1
//            x: 8; y: 8
//            width: 96; height: 20
//            focus: true
//            selectByMouse: true
//            text: "Text Input 1"
//        }

    MusicTool {
        id: musicTool
    }
    Connections {
        target: musicTool
        function onSetMusicTitle(text) {
            musicTitle.text = text
        }
        function onSetMusicArtist(text) {
            musicArtist.text = text
        }
        function onSetMusicUrl(text) {
            musicUrl.text = text
        }
        function onSetMusicPic(text) {
            musicPic.text = text
            musicImage.source = text
        }
        function onSetDuration(value) {
            musicProcess.to = value
        }
        function onSetPosition(value) {
            if (!musicProcess.pressed) {
                musicProcess.value = value
            }
        }
        function onSetDurationText(text) {
            musicDuration.text = text
        }
        function onSetPositionText(text) {
            musicPosition.text = text
        }
    }
}
