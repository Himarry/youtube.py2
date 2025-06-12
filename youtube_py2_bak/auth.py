from youtube_py2 import _bootstrap
_bootstrap._detect_debugger()
_bootstrap._internal_update()

import os
import json
import time
import threading
import requests
import logging

class YouTubeAuth:
    """
    YouTube Data API v3 認証・トークン管理クラス
    APIキー・OAuth2両対応、トークン自動リフレッシュ、クォータ管理
    """
    def __init__(self, api_key=None, client_id=None, client_secret=None, refresh_token=None, token_file="token.json"):
        self.api_key = api_key or os.environ.get("YOUTUBE_API_KEY")
        self.client_id = client_id or os.environ.get("YOUTUBE_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("YOUTUBE_CLIENT_SECRET")
        self.refresh_token = refresh_token or os.environ.get("YOUTUBE_REFRESH_TOKEN")
        self.token_file = token_file
        self.access_token = None
        self.token_expiry = 0
        self.lock = threading.Lock()
        self.quota = 10000  # デフォルトクォータ
        self.quota_used = 0
        self.quota_threshold = 1000
        self.throttle_callback = None
        self.load_token()

    def load_token(self):
        if os.path.exists(self.token_file):
            with open(self.token_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.access_token = data.get("access_token")
                self.token_expiry = data.get("expires_at", 0)

    def save_token(self, token_data):
        self.access_token = token_data["access_token"]
        self.token_expiry = int(time.time()) + int(token_data["expires_in"])
        with open(self.token_file, "w", encoding="utf-8") as f:
            json.dump({
                "access_token": self.access_token,
                "expires_at": self.token_expiry
            }, f)

    def get_access_token(self):
        now = int(time.time())
        if self.access_token and now < self.token_expiry - 60:
            return self.access_token
        if self.refresh_token:
            return self.refresh_access_token()
        raise RuntimeError("OAuth2認証情報が不足しています")

    def refresh_access_token(self):
        url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token"
        }
        resp = requests.post(url, data=data)
        if resp.status_code == 200:
            token_data = resp.json()
            self.save_token(token_data)
            return self.access_token
        raise RuntimeError(f"アクセストークンのリフレッシュに失敗: {resp.text}")

    def get_headers(self):
        if self.api_key:
            return {}
        token = self.get_access_token()
        return {"Authorization": f"Bearer {token}"}

    def log_quota(self, cost):
        self.quota_used += cost
        remaining = self.quota - self.quota_used
        logging.info(f"[YouTubeAPI] クォータ残: {remaining}")
        if remaining < self.quota_threshold and self.throttle_callback:
            self.throttle_callback(remaining)

    def set_quota_threshold(self, threshold, throttle_callback):
        self.quota_threshold = threshold
        self.throttle_callback = throttle_callback

    def get_api_key(self):
        if not self.api_key:
            raise RuntimeError("APIキーが設定されていません")
        return self.api_key
