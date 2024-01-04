import os
import random
import textwrap
import typing as t

import streamlit as st

from lib.local import Session, Video


class Choice:
    def __init__(self, sequence: t.List[str]) -> None:
        self._sequence = sequence
        self._length = len(sequence)

    @property
    def sequence(self) -> t.List[str]:
        return self._sequence

    @property
    def playlist(self) -> t.List[str]:
        return st.session_state['playlist']

    @playlist.setter
    def playlist(self, value: t.List[str]):
        st.session_state['playlist'] = value

    @property
    def index(self) -> int:
        return st.session_state['index']

    @index.setter
    def index(self, value: int) -> None:
        st.session_state['index'] = value

    def next(self) -> None:
        self.index = (self.index + 1) % self._length

    def prev(self) -> None:
        self.index = (self.index - 1) % self._length

    def current(self) -> int:
        if 'playlist' not in st.session_state:
            sequence = self._sequence.copy()
            random.shuffle(sequence)
            self.playlist = sequence
            self.index = 0
        return self.index


# page config
st.set_page_config(page_title='bilibili-backup-app', page_icon='random', layout='wide')
# sidebar
with Session() as session:
    is_login = os.environ.get('ADMIN', 'admin') not in \
        st.experimental_get_query_params().get('user', [])
    videos = {
        f'{video.id} {video.title}': video
        for video in session
            .query(Video)
            .filter_by(public=is_login)
            .order_by(Video.id.desc())
    }
    choice = Choice(list(videos.keys()))
with st.sidebar:
    threshold = st.slider('Auto-display Threshold (MB)', min_value=1, max_value=128, value=32)
    st.form('prev').form_submit_button('Prev', on_click=choice.prev, use_container_width=True)
    st.form('next').form_submit_button('Next', on_click=choice.next, use_container_width=True)
    key = st.selectbox('Video', index=choice.current(), options=choice.playlist)
    choice.index = choice.playlist.index(key)
    video = videos[key]
    st.image(video.cover.as_posix(), caption=f'ID: {video.id}', use_column_width=True)
    st.markdown('## [{title}]({url})\n\n### {tags}\n\n{body}'.format(
        title=video.title,
        url=video.to_remote().url,
        tags=' '.join(map('`{}`'.format, filter(bool, video.tags.split('\t')))),
        body=textwrap.indent(video.description, '> '),
    ))
# main
paths: t.Dict[str, t.Tuple[str, bool]] = {
    path.stem: (
        path.as_posix(),
        path.stat().st_size > threshold * 1048576,
    ) for path in video.directory.glob('*.mp4')
}
index = None if any(value[1] for value in paths.values()) else 0
key = st.selectbox(f'Total {len(paths)} Part(s)', sorted(paths.keys()), index=index)
if key is not None:
    st.video(paths[key][0])
