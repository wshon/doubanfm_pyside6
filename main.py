import logging
import sys
from pathlib import Path

from PySide6.QtCore import QObject, Slot, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement
from PySide6.QtQuickControls2 import QQuickStyle

from douban_fm import DoubanFM, Action, Song
from system_media import SystemMediaInterface


class Music(Song):
    position = 0
    duration = 1

    def __init__(self, song: Song):
        self._song = song

    def __getattr__(self, item):
        return Song.__getattribute__(self._song, item)


QML_IMPORT_NAME = "MusicUtil"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class MusicTool(QObject):
    music: Music

    def __init__(self):
        QObject.__init__(self)
        self.db = DoubanFM()
        self.smi = SystemMediaInterface()
        self.smi.on_play_event = self.on_play_event
        self.smi.on_pause_event = self.on_pause_event
        self.smi.on_next_event = self.on_next_event
        self.load_music()

    def load_music(self, action=None):
        song = self.db.get_next_song(action)
        self.music = Music(song)

    sendCommand = Signal(str)

    def on_play_event(self):
        # noinspection PyUnresolvedReferences
        self.sendCommand.emit('play')

    def on_pause_event(self):
        # noinspection PyUnresolvedReferences
        self.sendCommand.emit('pause')

    def on_next_event(self):
        # noinspection PyUnresolvedReferences
        self.sendCommand.emit('next')

    # noinspection PyTypeChecker
    @Slot(int, result=str)
    def get_time(self, t):
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

    # noinspection PyTypeChecker
    @Slot(result=str)
    def get_music_title(self):
        title = self.music.title if self.music else '未播放'
        self.smi.set_title(title)
        return title

    # noinspection PyTypeChecker
    @Slot(result=str)
    def get_music_artist(self):
        artist = self.music.artist if self.music else '跌名'
        self.smi.set_artist(artist)
        return artist

    # noinspection PyTypeChecker
    @Slot(result=str)
    def get_music_url(self):
        return self.music.url if self.music else ''

    # noinspection PyTypeChecker
    @Slot(result=str)
    def get_music_pic(self):
        return self.music.picture if self.music else ''

    @Slot()
    def next_music(self):
        self.load_music()

    @Slot()
    def skip_music(self):
        self.load_music(Action.Skip)

    @Slot()
    def on_music_play(self):
        self.smi.set_status_playing()

    @Slot()
    def on_music_paused(self):
        self.smi.set_status_paused()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.NOTSET,
        stream=sys.stdout
    )

    app = QGuiApplication(sys.argv)
    QQuickStyle.setStyle("Material")

    engine = QQmlApplicationEngine()

    qml_file = Path(__file__).parent / 'main.qml'
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
