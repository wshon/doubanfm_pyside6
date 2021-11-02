import logging
import platform
import sys
from pathlib import Path

from PySide6.QtCore import QObject, Slot, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement
from PySide6.QtQuickControls2 import QQuickStyle

from douban_fm import DoubanFM, Action, Song

system = None
if platform.system() == 'Windows':
    try:
        from winrt.windows.media.playback import MediaPlayer
        from winrt.windows.media import (
            SystemMediaTransportControls, SystemMediaTransportControlsButtonPressedEventArgs,
            SystemMediaTransportControlsButton, MediaPlaybackStatus, SystemMediaTransportControlsDisplayUpdater,
            MediaPlaybackType
        )

        system = 'Windows'
    except Exception as _e:
        logging.exception(_e)
    pass


class SystemMediaInterface:
    def __init__(self):
        if system == 'Windows':
            self._mp: MediaPlayer = MediaPlayer()
            self._smtc: SystemMediaTransportControls = self._mp.system_media_transport_controls
            self._smtc.is_play_enabled = True
            self._smtc.is_pause_enabled = True
            self._smtc.is_next_enabled = True
            self._smtc.add_button_pressed(self._on_button_pressed)
            self._du: SystemMediaTransportControlsDisplayUpdater = self._smtc.display_updater
            self._du.type = MediaPlaybackType.MUSIC
            self._du.update()

    if system == 'Windows':
        def _on_button_pressed(
                self,
                sender: SystemMediaTransportControls,
                args: SystemMediaTransportControlsButtonPressedEventArgs
        ):
            if args.button == SystemMediaTransportControlsButton.PLAY:
                if self.on_play_event():
                    sender.playback_status = MediaPlaybackStatus.PLAYING
            elif args.button == SystemMediaTransportControlsButton.PAUSE:
                if self.on_pause_event():
                    sender.playback_status = MediaPlaybackStatus.PAUSED
            elif args.button == SystemMediaTransportControlsButton.NEXT:
                if self.on_next_event():
                    sender.playback_status = MediaPlaybackStatus.PLAYING
            pass

    def on_play_event(self) -> bool:
        raise NotImplementedError

    def on_pause_event(self) -> bool:
        raise NotImplementedError

    def on_next_event(self) -> bool:
        raise NotImplementedError

    def set_status_playing(self):
        try:
            if system == 'Windows':
                self._smtc.playback_status = MediaPlaybackStatus.PLAYING
        except Exception as e:
            logging.exception(e)
        pass

    def set_status_paused(self):
        try:
            if system == 'Windows':
                self._smtc.playback_status = MediaPlaybackStatus.PAUSED
        except Exception as e:
            logging.exception(e)
        pass

    def set_title(self, title):
        try:
            if system == 'Windows':
                self._du.music_properties.title = title
                self._du.update()
        except Exception as e:
            logging.exception(e)
        pass

    def set_artist(self, artist):
        try:
            if system == 'Windows':
                self._du.music_properties.artist = artist
                self._du.update()
        except Exception as e:
            logging.exception(e)
        pass

    def set_album_artist(self, album_artist):
        try:
            if system == 'Windows':
                self._du.music_properties.album_artist = album_artist
                self._du.update()
        except Exception as e:
            logging.exception(e)
        pass


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
