import QtQuick
import QtQuick.Controls
import QtMultimedia
import Qt5Compat.GraphicalEffects

import MusicUtil

Window {
    id: root

    width: 640; maximumWidth: width; minimumWidth: width
    height: 240; maximumHeight: height; minimumHeight: height
    visible: true
    title: "DoubanFM by 𝚆𝚂𝚑𝚘𝚗"
    flags: Qt.Window | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint

    function show_music() {
        musicTitle.text = musicTool.get_music_title()
        musicArtist.text = musicTool.get_music_artist()
        musicPlayer.source = musicTool.get_music_url()
        musicImage.source = musicTool.get_music_pic()
        musicPlayer.play()
        musicImageRotation.to = 0
        musicImageRotationTimer.restart()
    }

    Component.onCompleted: {
        show_music()
    }

    MusicTool {
        id: musicTool
    }
    Connections {
        target: musicTool
        function onSendCommand(state) {
            if (state === "play") {
                musicPlayer.play()
            } else if (state === "pause") {
                musicPlayer.pause()
            } else if (state === "next") {
                musicTool.next_music()
                show_music()
            }
            return musicPlayer.playbackState
        }
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
                musicTool.next_music()
                show_music()
            }
        }
        onPlaybackStateChanged: {
            if (playbackState === MediaPlayer.PlayingState) {
                musicTool.on_music_play()
            } else if (playbackState === MediaPlayer.PausedState) {
                musicTool.on_music_paused()
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
            Timer {
                id: musicImageRotationTimer
                interval: 200
                repeat: true
                running: musicPlayer.playbackState === MediaPlayer.PlayingState
                triggeredOnStart: true
                onTriggered: {
                    musicImageRotation.stop()
                    musicImageRotation.from = musicImageRotation.to
                    musicImageRotation.to = musicImageRotation.from + 6
                    musicImageRotation.start()
                }
            }
            RotationAnimator {
                id: musicImageRotation
                target: musicImageShow;
                duration: musicImageRotationTimer.interval - 1
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
                    spacing: 2
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
                        text: musicPlayer.playbackState === MediaPlayer.PlayingState ? "暂停" : "播放"
                        onClicked: musicPlayer.playbackState === MediaPlayer.PlayingState ? musicPlayer.pause() : musicPlayer.play()
                    }
                    Button {
                        text: "Next"
                        onClicked: {
                            musicTool.next_music()
                            show_music()
                        }
                    }
                    Button {
                        text: "Skip"
                        onClicked: {
                            musicTool.skip_music()
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
