import functools as f
import pathlib as p
import shutil
import subprocess as sp
import typing as t

import httpx

from tenacity import retry, stop, wait

from .local import Author, Video as LocalVideo
from .util import get


class Favorite:
    def __init__(self, id: int) -> None:
        self._id = id

    def number(self) -> int:
        return self._page(1).json()['data']['info']['media_count']

    def videos(self) -> t.Iterator[t.Tuple[Author, LocalVideo]]:
        ith = 0
        while True:
            ith += 1
            data = self._page(ith).json()['data']
            for item in self._page_medias(ith):
                yield (Author.fromDict(item), LocalVideo.fromDict(item))
            if not data['has_more']:
                break

    @f.lru_cache(maxsize=5)
    def _page(self, ith: int) -> httpx.Response:
        url = 'https://api.bilibili.com/x/v3/fav/resource/list'
        params = {'media_id': self._id, 'pn': ith, 'ps': 20, 'order': 'mtime'}
        return get(url, params=params)

    @retry(stop=stop.stop_after_attempt(5), wait=wait.wait_fixed(1))
    def _page_medias(self, ith: int) -> t.List:
        return self._page(ith).json()['data']['medias']


class Favorites:
    def __init__(self, *ids: int) -> None:
        self._favorites = list(map(Favorite, ids))

    def number(self) -> int:
        return sum(favorite.number() for favorite in self._favorites)

    def videos(self) -> t.Iterator[t.Tuple[Author, LocalVideo]]:
        for favorite in self._favorites:
            yield from favorite.videos()


class Video:
    def __init__(self, id: int) -> None:
        self._id = id

    @property
    def bv(self) -> str:
        table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
        r = list('BV1  4 1 7  ')
        s = [11, 10, 3, 8, 4, 6]
        x = (self._id^177451812) + 8728348608
        for i in range(6):
            r[s[i]] = table[x//58**i%58]
        return ''.join(r)

    @property
    def url(self) -> str:
        return f'https://www.bilibili.com/video/{self.bv}/'

    def download(self) -> bool:
        directory = LocalVideo._directory(self._id)
        if directory.exists():
            return True
        args = [
            'you-get',
            '--playlist',
            '--output-dir', directory,
            f'https://www.bilibili.com/video/{self.bv}',
        ]
        try:
            return 0 == sp.run(args, capture_output=True).returncode
        except KeyboardInterrupt:
            shutil.rmtree(directory, ignore_errors=True)
            return False

    def ffmpeg(self) -> bool:
        ans = True
        directory = LocalVideo._directory(self._id)
        temp = directory / '_.mp4'
        for path in directory.glob('*.mp4'):
            shutil.copy(path, temp)
            try:
                ans &= 0 == self._ffmpeg(temp, path).returncode
            except KeyboardInterrupt:
                shutil.copy(temp, path)
                return False
        temp.unlink(missing_ok=True)
        return ans

    def _ffmpeg(self, src: p.Path, dst: p.Path) -> sp.CompletedProcess:
        # https://superuser.com/questions/859010/what-ffmpeg-command-line-produces-video-more-compatible-across-all-devices
        args = [
            'ffmpeg', '-y', '-i', src,
            '-c:v', 'libx264', '-crf', '23', '-profile:v', 'baseline',
            '-level', '3.0', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ac', '2',
            '-b:a', '128k', '-movflags', 'faststart', dst,
        ]
        return sp.run(args, capture_output=True)
