import logging
import sys

from PySide6.QtCore import QUrl, QObject, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType

from douban_fm import DoubanFM, Action, Song


def get_time(t):
    t = t // 1000
    h = []
    while t > 0:
        p = int(t % 60)
        h.insert(0, f'{p:02d}')
        t = t // 60
    while len(h) < 2:
        h.insert(0, '00')
    s = ':'.join(h)
    return s


class MusicTool(QObject):

    def __init__(self):
        QObject.__init__(self)
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.durationChanged.connect(self.durationChanged)
        self.player.positionChanged.connect(self.positionChanged)
        self.player.mediaStatusChanged.connect(self.mediaStatusChanged)
        self.audio_output.setVolume(10)
        # self.process_timer = QTimer()
        # self.process_timer.setInterval(1000)
        # self.process_timer.timeout.connect(self.showTime)
        self.db = DoubanFM()

    setMusicTitle = Signal(str)
    setMusicArtist = Signal(str)
    setMusicUrl = Signal(str)
    setMusicPic = Signal(str)
    setDuration = Signal(int)
    setPosition = Signal(int)
    setDurationText = Signal(str)
    setPositionText = Signal(str)

    def _switch_music(self, music: Song):
        self.player.setSource(music.url)

        self.setPosition.emit(0)
        self.setDuration.emit(1)
        self.setMusicTitle.emit(music.title)
        self.setMusicArtist.emit(music.artist)
        self.setMusicUrl.emit(music.url)
        self.setMusicPic.emit(music.picture)

    @Slot()
    def nextMusic(self):
        music = self.db.get_next_song()
        self._switch_music(music)
        self.player.play()

    @Slot()
    def skipMusic(self):
        music = self.db.get_next_song(Action.Skip)
        self._switch_music(music)
        self.player.play()

    @Slot()
    def playMusic(self):
        self.player.play()

    @Slot()
    def pauseMusic(self):
        self.player.pause()

    @Slot()
    def skip10s(self):
        self.player.setPosition(self.player.position() + 10 * 1000)

    @Slot()
    def durationChanged(self, duration):
        print('duration: ', duration)
        self.setDuration.emit(duration)
        t = get_time(duration)
        self.setDurationText.emit(t)
        pass

    @Slot()
    def positionChanged(self, position):
        print('position: ', position)
        self.setPosition.emit(position)
        t = get_time(position)
        self.setPositionText.emit(t)
        pass

    @Slot()
    def mediaStatusChanged(self, status):
        print('status: ', status)
        if status == QMediaPlayer.EndOfMedia:
            self.nextMusic()

        pass


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.NOTSET,
        stream=sys.stdout
    )

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    qmlRegisterType(MusicTool, 'MusicUtil', 1, 0, 'MusicTool')

    engine.load(QUrl("main.qml"))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
