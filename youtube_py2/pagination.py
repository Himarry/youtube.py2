from youtube_py2 import _bootstrap
_bootstrap._detect_debugger()
_bootstrap._internal_update()

import logging

class YouTubePagination:
    """
    ページネーション対応ユーティリティ
    - nextPageTokenによる自動ページ送り
    - 指定件数分まとめて取得
    """
    def fetch_all(self, fetch_func, *args, max_total=1000, **kwargs):
        results = []
        page_token = None
        while len(results) < max_total:
            kwargs["page_token"] = page_token
            resp = fetch_func(*args, **kwargs)
            items = resp.get("items", [])
            results.extend(items)
            page_token = resp.get("nextPageToken")
            if not page_token or len(results) >= max_total:
                break
        return results[:max_total]
