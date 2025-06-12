from youtube_py2 import _bootstrap
_bootstrap._detect_debugger()
_bootstrap._internal_update()

import requests
import pandas
from youtube_py2.license import require_device_cert

class YouTubeMembership:
    """
    チャンネルメンバーシップ連携
    - membershipsLevels.list()
    - members.list() → DataFrame化
    """
    def __init__(self, auth):
        self.auth = auth
        self.base_url = "https://www.googleapis.com/youtube/v3"

    def get_membership_levels(self, channel_id):
        require_device_cert()
        url = f"{self.base_url}/membershipsLevels"
        params = {
            "part": "snippet",
            "channelId": channel_id,
            "key": self.auth.get_api_key() if self.auth.api_key else None
        }
        headers = self.auth.get_headers()
        resp = requests.get(url, params={k: v for k, v in params.items() if v}, headers=headers)
        if resp.status_code == 200:
            return resp.json().get("items", [])
        raise RuntimeError(f"メンバーシップレベル取得失敗: {resp.text}")

    def get_channel_members(self, channel_id, to_dataframe=True):
        require_device_cert()
        url = f"{self.base_url}/members"
        params = {
            "part": "snippet",
            "channelId": channel_id,
            "key": self.auth.get_api_key() if self.auth.api_key else None
        }
        headers = self.auth.get_headers()
        resp = requests.get(url, params={k: v for k, v in params.items() if v}, headers=headers)
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            if to_dataframe:
                return pandas.DataFrame(items)
            return items
        raise RuntimeError(f"メンバーリスト取得失敗: {resp.text}")

    def get_membership_info(self, channel_id):
        require_device_cert()
        url = f"{self.base_url}/membershipsLevels"
        params = {
            "part": "snippet",
            "channelId": channel_id,
            "key": self.auth.get_api_key() if self.auth.api_key else None
        }
        headers = self.auth.get_headers()
        resp = requests.get(url, params={k: v for k, v in params.items() if v}, headers=headers)
        if resp.status_code == 200:
            return resp.json().get("items", [])
        raise RuntimeError(f"メンバーシップ情報取得失敗: {resp.text}")
