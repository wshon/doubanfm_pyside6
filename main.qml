import QtQuick
import QtQuick.Controls
import QtMultimedia
import Qt5Compat.GraphicalEffects

import MusicUtil

ApplicationWindow {
    id: root

    width: 640
    height: 240
    visible: true
    title: "Proxy Tool"
    flags: WindowType.WindowMinMaxButtonsHint

    function show_music() {
        musicTitle.text = musicTool.get_music_title()
        musicArtist.text = musicTool.get_music_artist()
        musicPlayer.source = musicTool.get_music_url()
        musicImage.source = musicTool.get_music_pic()
        musicPlayer.play()
    }

    Component.onCompleted: {
        show_music()
    }

    MusicTool {
        id: musicTool
    }

    MediaPlayer {
        id: musicPlayer
        audioOutput: AudioOutput {
            volume: 10
        }
        onDurationChanged: {
            musicProcess.to = duration
            musicDuration.text = musicTool.get_time(duration)
        }
        onPositionChanged: {
            if (!musicProcess.pressed) {
                musicProcess.value = position
                musicPosition.text = musicTool.get_time(position)
            }
        }
        onMediaStatusChanged: {
            if (status === MediaPlayer.EndOfMedia) {
                musicTool.nextMusic()
                show_music()
            }
        }
    }

    Row {
        anchors.fill: parent
        anchors.margins: 10
        Rectangle {
            width: parent.height; height: width
            radius: width / 2
            border.width: width / 2
            border.color: "#80000000"
            color: "#00000000"
            Image {
                id: musicImage
                anchors.fill: parent
                anchors.margins: 8
                cache: false
                fillMode: Image.PreserveAspectFit
                visible: false
            }
            Image {
                id: musicImageDefault
                anchors.fill: parent
                anchors.margins: 8
                source: "https://img2.doubanio.com/f/music/cc57bd208b5048ff760ca338c30ec9370a96f5ba/pics/music/songlist/cover_default_v1.png"
                fillMode: Image.PreserveAspectFit
                visible: false
            }
            Rectangle {
                id: musicImageMask
                anchors.fill: parent
                radius: width / 2
                visible: false
            }
            OpacityMask {
                id: musicImageShow
                anchors.fill: parent
                source: musicImage.status == Image.Ready ? musicImage : musicImageDefault
                maskSource: musicImageMask
            }
            RotationAnimator {
                id: musicImageRotation
                target: musicImageShow;
                from: 0;
                to: 360;
                duration: 10000
                loops : Animation.Infinite
                running: musicPlayer.playbackState === MediaPlayer.PlayingState
            }
        }
        Rectangle {
            color: "#00000000"
            width: parent.width - parent.height; height: parent.height
            Column {
                anchors.fill: parent
                anchors.margins: 8
                Label {
                    id: musicTitle
                    width: parent.width
                    font.pixelSize: 25
                }
                Label {
                    id: musicArtist
                    width: parent.width
                    font.pixelSize: 15
                }

                Row {
                    width: parent.width
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
                    onMoved: {
                        musicPosition.text = musicTool.get_time(value)
                        musicPlayer.position = value
                    }
                }
                Row {
                    width: parent.width
                    spacing: 6
                    Button {
                        text: musicPlayer.playbackState === MediaPlayer.PlayingState ? "Pause" : "Play"
                        onClicked: musicPlayer.playbackState === MediaPlayer.PlayingState ? musicPlayer.pause() : musicPlayer.play()
                    }
                    Button {
                        text: "Next"
                        onClicked: {
                            musicTool.nextMusic()
                            show_music()
                        }
                    }
                    Button {
                        text: "Skip"
                        onClicked: {
                            musicTool.skipMusic()
                            show_music()
                        }
                    }
                    Button {
                        text: "+10S"
                        onClicked: musicPlayer.position = musicPlayer.position + 10 * 1000
                    }
                }
            }
        }
    }
}
