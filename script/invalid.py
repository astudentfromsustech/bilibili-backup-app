__root__ = __import__('pathlib').Path(__file__).parents[1]
__import__('sys').path.append(__root__.as_posix())


import time

import httpx
import tqdm

from lib.config import HEADERS
from lib.local import Session, Video


url = 'https://api.bilibili.com/x/web-interface/wbi/view/detail'
with Session() as session:
    total = session.query(Video).count()
    for video in tqdm.tqdm(session.query(Video), total=total):
        time.sleep(1.0)
        params = {'aid': video.id}
        data = httpx.get(url, params=params, headers=HEADERS).json()
        if data['code'] != 0:
            print(
                data['code'], video.author.name,
                video.title, video.to_remote().url,
                sep='\t',
            )
