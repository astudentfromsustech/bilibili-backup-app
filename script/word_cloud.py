__root__ = __import__('pathlib').Path(__file__).parents[1]
__import__('sys').path.append(__root__.as_posix())


import collections as c
import functools as f
import pathlib as p
import random
import typing as t
import xml.dom.minidom

import jieba
import tqdm

from wordcloud import WordCloud

from lib.config import DOWNLOAD, DOWNLOAD_VIDEO


class XML:
    def __init__(self, path: p.Path) -> None:
        self._path = path

    def tokens(self) -> t.Iterator[str]:
        dom = xml.dom.minidom.parse(self._path.as_posix())
        for element in dom.getElementsByTagName('d'):
            yield from jieba.cut(element.firstChild.data)

    def tokens_without(self, token_set: t.Set[str]) -> t.Iterator[str]:
        for token in self.tokens():
            if token not in token_set:
                yield token


root: p.Path = __root__
path_video = root / DOWNLOAD_VIDEO
path_font = next((root/DOWNLOAD/'font').iterdir())
path_stop = root / DOWNLOAD / 'stopwords'
path_target = root / DOWNLOAD / 'wordcloud.png'
width, height = 1024, 1024
seed = 4_293370385763834
words = {'哔哩哔哩', '火钳刘明'}

list(map(jieba.add_word, words))
stopwords = f.reduce(
    lambda x, y: x.union(y), (
        set(path.read_text().splitlines())
        for path in path_stop.rglob('*.txt')
    ), {'SimHei'},
)
paths = list(path_video.rglob('*.xml'))
tokens = sum(
    (
        c.Counter(XML(path).tokens_without(stopwords))
        for path in tqdm.tqdm(paths)
    ), start=c.Counter(),
)
tokens['哈哈哈'] += tokens.pop('哈哈哈哈', 0)
WordCloud(
    font_path=path_font.as_posix(),
    width=width, height=height, colormap='Dark2',
    max_words=1024, random_state=random.Random(seed),
) \
    .generate_from_frequencies(tokens) \
    .to_file(path_target)
