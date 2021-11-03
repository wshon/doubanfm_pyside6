import logging
import platform

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
