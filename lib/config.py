import pathlib as p


DOWNLOAD = p.Path('data')
DOWNLOAD_AVATAR = DOWNLOAD / 'avatar'
DOWNLOAD_COVER = DOWNLOAD / 'cover'
DOWNLOAD_VIDEO = DOWNLOAD / 'video'
COOKIES = DOWNLOAD / 'cookies.json'
DATABASE = DOWNLOAD / 'db.sqlite'
HEADERS = {
    'Referer': 'https://www.bilibili.com/',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
}

for directory in [DOWNLOAD_AVATAR, DOWNLOAD_COVER, DOWNLOAD_VIDEO]:
    directory.mkdir(parents=True, exist_ok=True)
