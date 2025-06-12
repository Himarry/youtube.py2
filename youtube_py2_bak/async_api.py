from youtube_py2 import _bootstrap
_bootstrap._detect_debugger()
_bootstrap._internal_update()

import asyncio
import requests
from youtube_py2.license import require_device_cert

class YouTubeAsync:
    """
    非同期APIユーティリティ
    - asyncio対応
    - 複数リクエスト同時処理
    """
    def __init__(self, auth):
        self.auth = auth
        self.base_url = "https://www.googleapis.com/youtube/v3"

    async def fetch(self, session, url, params, headers):
        loop = asyncio.get_event_loop()
        resp = await loop.run_in_executor(None, lambda: requests.get(url, params=params, headers=headers))
        return resp.json()

    async def fetch_many(self, urls_params):
        import aiohttp
        results = []
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url, params, headers in urls_params:
                tasks.append(self.fetch(session, url, params, headers))
            results = await asyncio.gather(*tasks)
        return results

    def async_request(self, func, *args, **kwargs):
        require_device_cert()
        # 任意の同期関数を非同期で実行
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(None, lambda: func(*args, **kwargs))
