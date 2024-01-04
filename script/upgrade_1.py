__root__ = __import__('pathlib').Path(__file__).parents[1]
__import__('sys').path.append(__root__.as_posix())


from sqlalchemy.engine import create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Boolean, Integer, String


Base = declarative_base()
engine = create_engine(f'sqlite:///db.sqlite')
session = sessionmaker(bind=engine)()


class Author(Base):
    __tablename__ = 'author'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    sex = Column(String(4), default='保密')
    sign = Column(String(128), default='')


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


Base.metadata.create_all(engine, checkfirst=True)


if __name__ == '__main__':
    from lib.local import Session, Author as AuthorSrc, Video as VideoSrc

    session_dst = session
    with Session() as session_src:
        session_dst.add_all(
            Author(
                id=author.id, name=author.name,
                sex=author.sex, sign=author.sign,
            ) for author in session_src.query(AuthorSrc)
        )
        session_dst.add_all(
            Video(
                id=video.id, title=video.title,
                timestamp=video.timestamp, tags=video.tags,
                description=video.description, public=True,
                author_id=video.author_id,
            ) for video in session_src.query(VideoSrc)
        )
    session_dst.commit()
