import json

import httpx

from tenacity import retry, stop, wait

from .config import COOKIES as PATH, HEADERS


COOKIES = json.loads(PATH.read_text()) if PATH.exists() else {}


@retry(stop=stop.stop_after_attempt(5), wait=wait.wait_fixed(1))
def get(*args, **kwargs) -> httpx.Response:
    kwargs['cookies'] = COOKIES | (kwargs.pop('cookies', None) or {})
    kwargs['headers'] = HEADERS | (kwargs.pop('headers', None) or {})
    return httpx.get(*args, **kwargs)
