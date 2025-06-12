from youtube_py2 import _bootstrap
_bootstrap._detect_debugger()
_bootstrap._internal_update()

import requests
import threading
import time
from youtube_py2.license import require_device_cert

class YouTubeLive:
    """
    ライブ配信・リアルタイム連携
    - liveChatMessages.list() でリアルタイムコメント取得
    - Super Chatイベント取得
    - WebSocket風コールバック
    """
    def __init__(self, auth):
        self.auth = auth
        self.base_url = "https://www.googleapis.com/youtube/v3"

    def stream_live_chat(self, live_chat_id, callback, poll_interval=2):
        require_device_cert()
        url = f"{self.base_url}/liveChat/messages"
        params = {
            "liveChatId": live_chat_id,
            "part": "snippet,authorDetails",
            "key": self.auth.get_api_key() if self.auth.api_key else None
        }
        headers = self.auth.get_headers()
        def poll():
            next_page = None
            while True:
                if next_page:
                    params["pageToken"] = next_page
                resp = requests.get(url, params={k: v for k, v in params.items() if v}, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("items", []):
                        callback(item)
                    next_page = data.get("nextPageToken")
                time.sleep(poll_interval)
        thread = threading.Thread(target=poll, daemon=True)
        thread.start()

    def get_super_chat_events(self, live_chat_id, callback, poll_interval=2):
        require_device_cert()
        url = f"{self.base_url}/superChatEvents"
        params = {
            "liveChatId": live_chat_id,
            "part": "snippet",
            "key": self.auth.get_api_key() if self.auth.api_key else None
        }
        headers = self.auth.get_headers()
        def poll():
            while True:
                resp = requests.get(url, params={k: v for k, v in params.items() if v}, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("items", []):
                        callback(item)
                time.sleep(poll_interval)
        thread = threading.Thread(target=poll, daemon=True)
        thread.start()

    def start_live_stream(self, stream_title, stream_desc, privacy_status="private"): 
        require_device_cert()
        # ライブ配信イベント作成（YouTube API v3）
        url = f"{self.base_url}/liveBroadcasts?part=snippet,status"
        headers = self.auth.get_headers()
        body = {
            "snippet": {"title": stream_title, "description": stream_desc, "scheduledStartTime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + 60))},
            "status": {"privacyStatus": privacy_status}
        }
        resp = requests.post(url, headers=headers, json=body)
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"ライブ配信作成失敗: {resp.text}")
        return resp.json()
