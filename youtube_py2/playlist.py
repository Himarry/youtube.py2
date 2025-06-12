from youtube_py2 import _bootstrap
_bootstrap._detect_debugger()
_bootstrap._internal_update()

import requests
from youtube_py2.license import require_device_cert

class YouTubePlaylist:
    """
    プレイリスト関連APIラッパー
    - プレイリスト情報取得
    - プレイリスト内動画一覧取得
    - チャンネルの全プレイリスト取得
    """
    def __init__(self, auth):
        self.auth = auth
        self.base_url = "https://www.googleapis.com/youtube/v3"

    def get_playlist_info(self, playlist_id):
        require_device_cert()
        url = f"{self.base_url}/playlists"
        params = {
            "id": playlist_id,
            "part": "snippet,contentDetails",
            "key": self.auth.get_api_key() if self.auth.api_key else None
        }
        headers = self.auth.get_headers()
        resp = requests.get(url, params={k: v for k, v in params.items() if v}, headers=headers)
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            if items:
                return items[0]
            raise ValueError("プレイリストが見つかりません")
        raise RuntimeError(f"プレイリスト情報取得失敗: {resp.text}")

    def get_playlist_items(self, playlist_id, max_results=50, page_token=None):
        require_device_cert()
        url = f"{self.base_url}/playlistItems"
        params = {
            "playlistId": playlist_id,
            "part": "snippet,contentDetails",
            "maxResults": max_results,
            "pageToken": page_token,
            "key": self.auth.get_api_key() if self.auth.api_key else None
        }
        headers = self.auth.get_headers()
        resp = requests.get(url, params={k: v for k, v in params.items() if v}, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(f"プレイリスト動画一覧取得失敗: {resp.text}")

    def get_channel_playlists(self, channel_id, max_results=50, page_token=None):
        require_device_cert()
        url = f"{self.base_url}/playlists"
        params = {
            "channelId": channel_id,
            "part": "snippet,contentDetails",
            "maxResults": max_results,
            "pageToken": page_token,
            "key": self.auth.get_api_key() if self.auth.api_key else None
        }
        headers = self.auth.get_headers()
        resp = requests.get(url, params={k: v for k, v in params.items() if v}, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(f"チャンネルのプレイリスト取得失敗: {resp.text}")
