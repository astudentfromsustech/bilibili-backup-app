__root__ = __import__('pathlib').Path(__file__).parents[1]
__import__('sys').path.append(__root__.as_posix())


import typing as t

from lib.local import Session, Video


def get_int(prompt: str) -> t.Optional[int]:
    try:
        return int(input(prompt))
    except Exception:
        return None


with Session() as session:
    while True:
        title = input('Video title part: ')
        if not title:
            break
        videos = session.query(Video).filter(Video.title.like(f'%{title}%')).all()
        if not videos:
            break
        for ith, video in enumerate(videos):
            print('', ith, video.public, video.title, sep='\t')
        number = get_int('Video number: ')
        if number is None or number not in range(len(videos)):
            break
        video = videos[number]
        print('', video.id, video.title, sep='\t')
        print('', f'Public: {video.public} -> {not video.public}', sep='\t')
        video.public = not video.public
        session.add(video)
        print()
