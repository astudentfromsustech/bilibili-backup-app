import typing as t

import click


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument('ids', nargs=-1)
@click.option('--fast', '-f', is_flag=True, default=False)
def sync(ids: t.Tuple[int, ...], fast: bool) -> None:
    from tqdm import tqdm

    from .local import Session
    from .remote import Favorite, Favorites

    with Session() as session:
        for id in ids:
            favorite = Favorite(id)
            for author, video in tqdm(favorite.videos(), desc=id, total=favorite.number()):
                if not session.exists(video, 'id') and video.to_remote().download():
                    assert session.add_if_not_exists(author.full(), 'id')
                    assert session.add(video.full())
                elif fast:
                    break


@cli.command()
def ffmpeg():
    from tqdm import tqdm

    from .local import Session, Video

    with Session() as session:
        total = session.query(Video).count()
        for video in tqdm(session.query(Video), total=total):
            path = video.directory / 'ffmpeg.done'
            if not path.exists():
                assert video.to_remote().ffmpeg()
                path.touch(exist_ok=True)


@cli.command()
@click.option('--driver', '-d', default='Firefox')
def login(driver: t.Literal['Chrome', 'Edge', 'Firefox', 'Safari']) -> None:
    import json

    from selenium import webdriver

    from .config import COOKIES

    browser: webdriver.Remote = getattr(webdriver, driver)()
    browser.get('https://passport.bilibili.com/login')
    input('Please login in >>> ')
    cookies = {item['name']: item['value'] for item in browser.get_cookies()}
    COOKIES.write_text(json.dumps(cookies))


@cli.command()
def clean() -> None:
    import shutil

    from .config import COOKIES, DATABASE, DOWNLOAD_AVATAR, DOWNLOAD_COVER, DOWNLOAD_VIDEO

    for directory in [DOWNLOAD_AVATAR, DOWNLOAD_COVER, DOWNLOAD_VIDEO]:
        shutil.rmtree(directory, ignore_errors=True)
    for path in [COOKIES, DATABASE]:
        path.unlink(missing_ok=True)


cli.main()
