import base64
import json
import logging
import os.path
import sys
from dataclasses import dataclass
from typing import List, Optional
from urllib.request import urlopen, Request


@dataclass
class Creator:
    id: int
    name: str
    url: str
    pass


@dataclass
class Channel:
    id: int
    name: str = None
    creator: 'Creator' = None
    intro: str = None
    rec_reason: str = None
    banner: str = None
    cover: str = None
    song_to_start: str = None
    song_num: int = None
    collected: bool = None
    hot_songs: str = None
    #
    shareable: bool = None
    artist_id: int = None
    related_artists: List['RelatedArtists'] = None

    def get_playlist(self):
        pass

    pass


@dataclass
class RelatedArtists:
    id: int
    name: str
    cover: str
    pass


@dataclass
class Singer:
    style: list
    name: str
    region: List[str]
    name_usual: str
    genre: List[str]
    avatar: str
    related_site_id: int
    is_site_artist: bool
    id: str
    pass


@dataclass
class Release:
    ssid: str
    title: str
    cover: str
    link: str
    singers: List['Singer']
    id: str
    pass


@dataclass
class Song:
    all_play_sources: list
    albumtitle: str
    url: str
    file_ext: str
    album: str
    ssid: str
    title: str
    sid: str
    color_scheme: dict
    sha256: str
    status: int
    picture: str
    update_time: int
    alert_msg: str
    is_douban_playable: bool
    public_time: str
    partner_sources: list
    singers: List['Singer']
    like: int
    artist: str
    is_royal: bool
    subtype: str
    length: int
    release: 'Release'
    aid: str
    kbps: str
    available_formats: dict

    def get_picture(self):
        pass

    pass


class Action:
    New = 'n'
    Play = 'p'
    End = 'e'
    Like = 'r'
    Unlike = 'u'
    Ban = 'b'
    Skip = 's'
    pass


class DoubanFMApi:
    _api_host = 'https://fm.douban.com/j/v2'
    _api_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0'
    }
    _cookie = None

    def __init__(self, option):
        self.option = option
        self.load_cookie()

        class _Req:
            _api = self

            def __init__(self, path, **kwargs):
                if path.startswith('/'):
                    path = path.split('/', 1)[-1]
                    pass
                url = f'{self._api._api_host}/{path}'
                if kwargs:
                    url += '?' + '&'.join((f'{k}={v}' for k, v in kwargs.items()))
                    pass
                self._url = url

            def __enter__(self):
                logging.debug(f'REQ: {self._url}')
                req = Request(self._url, headers=self._api._api_header or {})
                if self._api._cookie:
                    req.add_header("Cookie", self._api._cookie)
                    pass
                rsp = urlopen(req)
                assert rsp.getcode() == 200, f'Request Fail: {rsp.getcode()}-{rsp.read()}'
                cookie = rsp.getheader('set-cookie')
                if cookie:
                    self._api.save_cookie(cookie.split(';', 1)[0])
                    pass
                rsp_data = json.load(rsp)
                logging.debug(f'RSP: {rsp_data}')
                return rsp_data

                pass

            def __exit__(self, exc_type, exc_value, traceback):
                return True

            pass

        self._req = _Req
        pass

    def load_cookie(self):
        cookie = None
        try:
            if os.path.exists('.cookie'):
                with open('.user_data', 'rb') as fp:
                    cookie = base64.b64decode(fp.read()).decode()
        except Exception as e:
            logging.exception(e)
        self._cookie = cookie

    def save_cookie(self, cookie: str):
        self._cookie = cookie
        try:
            with open('.user_data', 'wb') as fp:
                fp.write(base64.b64encode(cookie.encode()))
        except Exception as e:
            logging.exception(e)
        pass

    def get_channels(self):
        with self._req('rec_channels', specific='all') as rsp:
            if rsp['status'] is not True:
                return
            rsp_channels = rsp['data']['channels']
        ret_channels = {}
        for channel_type, channel_list in rsp_channels.items():
            if channel_type not in ret_channels:
                ret_channels[channel_type] = []
                pass
            for res_channel in channel_list:
                if 'related_artists' in res_channel:
                    res_channel['related_artists'] = [RelatedArtists(**x) for x in res_channel['related_artists']]
                res_channel['creator'] = Creator(**res_channel['creator'])
                res_channel['collected'] = res_channel['collected'] == 'true'
                channel = Channel(**res_channel)
                channel.get_playlist = lambda: self.get_playlist(channel)
                ret_channels[channel_type].append(channel)
                pass
            pass
        return ret_channels

    def get_playlist(self, channel: Channel = None, play_type=Action.New, **kwargs):
        '''
        
        type: 新频道时 n 使用列表内歌曲时 e 列表空了 p 
        sid: 正在播放时可增加当前播放歌曲的 sid 
        pt: 正在播放时可增加当前播放歌曲的 position
        pb: 正在播放时可增加当前播放歌曲的 kbps
        '''
        params = {
            'channel': channel.id if channel is not None else -10,
            **self.option,
            'type': play_type,
        }
        params.update(kwargs)
        ret_playlist = []
        with self._req('playlist', **params) as rsp:
            if rsp['r'] != 0:
                return
            rsp_playlist = rsp.get('song', [])
            rsp_song: dict
            for rsp_song in rsp_playlist:
                rsp_song['singers'] = [Singer(**s) for s in rsp_song['singers']]
                rsp_song['release'] = Release(**rsp_song['release'])
                song = Song(**rsp_song)
                song.get_picture = lambda: self.get_picture(song)
                ret_playlist.append(song)
                pass
        return ret_playlist

    def get_picture(self, song: Song):
        if not song.picture:
            return

        pass


class DoubanFM:
    api_key = ''
    _channels = {}
    _channel_fixed_maps = {
        0: Channel(0, name='我的私人'),
        -3: Channel(-3, name='红心'),
        -10: Channel(-10, name='豆瓣精选', intro='豆瓣好评音乐精选', shareable=True)
    }
    _channel_maps = {}
    current_channel: 'Channel' = None
    current_song: Optional['Song'] = None
    models = None

    def __init__(self):
        self._api = DoubanFMApi(
            option={
                'kbps': 128,
                'client': 's:mainsite|y:3.0',
                'app_name': 'radio_website',
                'version': 100,
                'apikey': self.api_key,
            }
        )
        self.current_channel = Channel(-10)
        self.reload_channel()

    def reload_channel(self):
        self._channel_maps = {k: v for k, v in self._channel_fixed_maps.items()}
        self._channels = self._api.get_channels()
        for channels in self._channels.values():
            for channel in channels:
                self._channel_maps[channel.id] = channel
        pass

    def get_channel(self, cid, default=None):
        return self._channel_maps.get(cid, default)

    def get_channels(self, group=None):
        if group:
            return self._channels.get(group)
        else:
            return self._channels
        pass

    def get_channel_groups(self, group=None):
        return self._channels.keys()

    def set_channel(self, cid):
        self.current_channel = self.get_channel(cid, self.current_channel)
        self.current_song = None

    def _playlist(self, play_type=None, **kwargs):
        if self.current_song:
            kwargs.update({
                'sid': self.current_song.sid,
                'pt': '',
                'pb': self.current_song.kbps,
                'apikey': self.api_key
            })
            play_type = play_type or Action.Play
        else:
            play_type = play_type or Action.New
        playlist = self._api.get_playlist(self.current_channel, play_type, **kwargs)
        if play_type != Action.End:
            assert playlist
        if play_type in [Action.Skip, Action.Like, Action.Unlike, Action.Ban, Action.New]:
            self.models = playlist
        elif play_type == Action.Play:
            self.models.extend(playlist)
        pass

    def get_next_song(self, action=None):
        if not self.models:
            self._playlist(action)
        elif self.current_song and self.current_song.sid:
            if action not in [Action.Skip, Action.Ban]:
                self._playlist(
                    Action.End,
                    sid=self.current_song.sid,
                    pt='',
                    pb=self.current_song.kbps
                )
        if self.models:
            self.current_song = self.models.pop(0)
        return self.current_song

    pass


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.NOTSET,
        stream=sys.stdout
    )
    db_fm = DoubanFM()
    song1 = db_fm.get_next_song()
    song2 = db_fm.get_next_song()
    song3 = db_fm.get_next_song()
    song4 = db_fm.get_next_song()
    song5 = db_fm.get_next_song()
    # a = channels['scenario'][0].get_playlist()
