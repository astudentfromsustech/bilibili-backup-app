import pathlib as p
import typing as t

import typing_extensions as te

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Boolean, Integer, String

from .config import DATABASE, DOWNLOAD_AVATAR, DOWNLOAD_COVER, DOWNLOAD_VIDEO
from .util import get

if t.TYPE_CHECKING:
    from .remote import Video as RemoteVideo


Base = declarative_base()
engine = create_engine(f'sqlite:///{DATABASE}')


class Session:
    def __init__(self) -> None:
        self.session = sessionmaker(bind=engine)()
        self.query = self.session.query

    def __enter__(self) -> te.Self:
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self.session.__exit__(*args, **kwargs)

    def exists(self, instance: Base, *keys: str) -> bool:
        Type = type(instance)
        criterions = (getattr(Type, key)==getattr(instance, key) for key in keys)
        return self.query(
            self.query(Type).filter(*criterions).exists()
        ).scalar()

    def add(self, instance: Base) -> bool:
        try:
            self.session.add(instance)
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False

    def add_if_not_exists(self, instance: Base, *keys: str) -> bool:
        return True if self.exists(instance, *keys) else self.add(instance)

    def add_all(self, *instances: Base) -> bool:
        try:
            self.session.add_all(instances)
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False



class Author(Base):
    __tablename__ = 'author'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    sex = Column(String(4), default='保密')
    sign = Column(String(128), default='')

    @classmethod
    def fromDict(cls, data: t.Dict) -> te.Self:
        return cls(
            id=data['upper']['mid'],
            name=data['upper']['name'],
        )

    @property
    def avatar(self) -> p.Path:
        return self._avatar(self.id)

    def full(self) -> te.Self:
        try:
            kwargs = self._others(self.id)
        except Exception:
            return self
        else:
            return self.__class__(id=self.id, name=self.name, **kwargs)

    @classmethod
    def _others(cls, id: int) -> t.Dict[str, t.Any]:
        url = 'https://api.bilibili.com/x/space/wbi/acc/info'
        params = {'mid': id}
        data = get(url, params=params).json()['data']
        cls._avatar(id).write_bytes(get(data['face']).content)
        return {'sex': data['sex'], 'sign': data['sign']}

    @staticmethod
    def _avatar(id: int) -> p.Path:
        return DOWNLOAD_AVATAR / f'{id}.jpg'


class Video(Base):
    __tablename__ = 'video'

    id = Column(Integer, primary_key=True)
    title = Column(String(128), nullable=False)
    timestamp = Column(Integer, nullable=False)
    tags = Column(String(256), default='')
    description = Column(String(512), default='')
    public = Column(Boolean, default=True)
    author_id = Column(Integer, ForeignKey('author.id'))

    author = relationship('Author', backref='videos')

    @classmethod
    def fromDict(cls, data: t.Dict) -> te.Self:
        id = data['id']
        return cls(
            id=id, title=data['title'],
            timestamp=data['pubtime'],
            author_id=data['upper']['mid'],
        )

    @property
    def cover(self) -> p.Path:
        return self._cover(self.id)

    @property
    def directory(self) -> p.Path:
        return self._directory(self.id)

    def full(self) -> te.Self:
        try:
            kwargs = self._others(self.id)
        except Exception:  # code: -400
            assert self.cover.exists()
            return self
        else:
            return self.__class__(
                id=self.id, title=self.title,
                timestamp=self.timestamp, author_id=self.author_id,
                **kwargs,
            )

    def to_remote(self) -> 'RemoteVideo':
        from .remote import Video

        return Video(self.id)

    @classmethod
    def _others(cls, id: int) -> t.Dict[str, t.Any]:
        url = 'https://api.bilibili.com/x/web-interface/wbi/view/detail'
        params = {'aid': id}
        data = get(url, params=params).json()['data']
        cls._cover(id).write_bytes(get(data['View']['pic']).content)
        return {
            'tags': '\t'.join(tag['tag_name'] for tag in data['Tags']),
            'description': data['View']['desc'],
        }

    @staticmethod
    def _cover(id: int) -> p.Path:
        return DOWNLOAD_COVER / f'{id}.jpg'

    @staticmethod
    def _directory(id: int) -> p.Path:
        return DOWNLOAD_VIDEO / str(id)


Base.metadata.create_all(engine, checkfirst=True)
