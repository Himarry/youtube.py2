from youtube_py2 import _bootstrap
_bootstrap._detect_debugger()
_bootstrap._internal_update()

import requests
from youtube_py2.license import require_device_cert
import time

class YouTubeChannel:
    """
    チャンネル関連APIラッパー
    - チャンネル情報取得
    - チャンネル動画一覧取得
    - チャンネル統計情報取得
    - 登録チャンネルリスト取得
    """
    def __init__(self, auth):
        self.auth = auth
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self._cache = {}

    def _cache_get(self, key):
        v = self._cache.get(key)
        if v and v[1] > time.time():
            return v[0]
        return None

    def _cache_set(self, key, value, ttl=60):
        self._cache[key] = (value, time.time() + ttl)

    def get_channel_info(self, channel_id=None, for_username=None, use_cache=True):
        cache_key = f"channel_info:{channel_id or for_username}"
        if use_cache:
            cached = self._cache_get(cache_key)
            if cached:
                return cached
        url = f"{self.base_url}/channels"
        params = {
            "id": channel_id,
            "forUsername": for_username,
            "part": "snippet,statistics,brandingSettings",
            "key": self.auth.get_api_key() if self.auth.api_key else None
        }
        headers = self.auth.get_headers()
        resp = requests.get(url, params={k: v for k, v in params.items() if v}, headers=headers)
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            if items:
                self._cache_set(cache_key, items[0], ttl=300)
                return items[0]
            raise ValueError("チャンネルが見つかりません")
        raise RuntimeError(f"チャンネル情報取得失敗: {resp.text}")

    def get_channel_videos(self, channel_id, max_results=50, page_token=None, exclude_shorts=False, exclude_normal=False, exclude_live=False):
        if exclude_shorts or exclude_normal or exclude_live:
            require_device_cert()
        url = f"{self.base_url}/search"
        params = {
            "channelId": channel_id,
            "part": "snippet",
            "maxResults": max_results,
            "order": "date",
            "type": "video",
            "pageToken": page_token,
            "key": self.auth.get_api_key() if self.auth.api_key else None
        }
        headers = self.auth.get_headers()
        resp = requests.get(url, params={k: v for k, v in params.items() if v}, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            if any([exclude_shorts, exclude_normal, exclude_live]):
                filtered = []
                for item in data.get("items", []):
                    desc = item["snippet"].get("description", "").lower()
                    title = item["snippet"].get("title", "").lower()
                    # Shorts判定: #shortsタグ or 60秒未満（durationはvideo APIで取得要）
                    is_shorts = ("#shorts" in desc or "#shorts" in title)
                    # ライブ判定: title/descに"ライブ"/"live"含む or liveBroadcastContent
                    is_live = ("ライブ" in title or "live" in title or item["snippet"].get("liveBroadcastContent") == "live")
                    is_normal = not is_shorts and not is_live
                    if exclude_shorts and is_shorts:
                        continue
                    if exclude_normal and is_normal:
                        continue
                    if exclude_live and is_live:
                        continue
                    filtered.append(item)
                data["items"] = filtered
            return data
        raise RuntimeError(f"チャンネル動画一覧取得失敗: {resp.text}")

    def get_channel_statistics(self, channel_id):
        info = self.get_channel_info(channel_id=channel_id)
        return info.get("statistics", {})

    def get_subscriptions(self, channel_id, max_results=50, page_token=None):
        url = f"{self.base_url}/subscriptions"
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
        raise RuntimeError(f"登録チャンネルリスト取得失敗: {resp.text}")

    def search_channels(self, query, max_results=10, page_token=None):
        """
        キーワードでチャンネルを検索
        :param query: 検索キーワード
        :param max_results: 最大取得件数
        :param page_token: ページトークン
        :return: dict (YouTube Data API v3 search type=channel のレスポンス)
        """
        url = f"{self.base_url}/search"
        params = {
            "q": query,
            "type": "channel",
            "part": "snippet",
            "maxResults": max_results,
            "pageToken": page_token,
            "key": self.auth.get_api_key() if self.auth.api_key else None
        }
        headers = self.auth.get_headers()
        resp = requests.get(url, params={k: v for k, v in params.items() if v}, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(f"チャンネル検索失敗: {resp.text}")

    def extract_channel_id(self, url_or_id):
        """
        YouTubeのURLや@ハンドル、チャンネルID表記からチャンネルIDを抽出する
        - URL例: https://www.youtube.com/channel/UCxxxx, https://www.youtube.com/@handle, https://www.youtube.com/user/xxxx
        - @から始まるハンドル: @handle
        - 直接ID: UCxxxx
        :param url_or_id: str
        :return: チャンネルID（str）またはNone
        """
        import re
        s = url_or_id.strip()
        # @ハンドル
        if s.startswith("@"):
            # APIでハンドルからID取得
            return self._get_channel_id_by_handle(s)
        # URLパターン
        m = re.search(r"youtube\.com/(channel|user|c|@)([\w\-@]+)", s)
        if m:
            kind, value = m.group(1), m.group(2)
            if kind == "channel":
                return value
            elif kind == "@":
                return self._get_channel_id_by_handle("@" + value)
            elif kind == "user":
                info = self.get_channel_info(for_username=value)
                return info["id"]
            elif kind == "c":
                # カスタムURLはAPIで取得できない場合がある
                # 一旦search_channelsで検索
                result = self.search_channels(value, max_results=1)
                items = result.get("items", [])
                if items:
                    return items[0]["snippet"]["channelId"]
                return None
        # 直接ID
        if s.startswith("UC") and len(s) >= 24:
            return s
        return None

    def _get_channel_id_by_handle(self, handle):
        # @handle からチャンネルIDを取得
        # API: search?type=channel&q=@handle で最上位を返す
        result = self.search_channels(handle, max_results=1)
        items = result.get("items", [])
        if items:
            return items[0]["snippet"]["channelId"]
        return None

    def get_thumbnail_url(self, channel_id, quality="high"):
        """
        チャンネルのサムネイル画像URLを取得
        :param channel_id: チャンネルID
        :param quality: "default"|"medium"|"high"
        :return: サムネイルURL(str)
        """
        info = self.get_channel_info(channel_id=channel_id)
        thumbs = info.get("snippet", {}).get("thumbnails", {})
        qmap = {"default": "default", "medium": "medium", "high": "high"}
        q = qmap.get(quality, "high")
        return thumbs.get(q, {}).get("url")

    def get_category(self, channel_id):
        """
        チャンネルのカテゴリ名を取得（brandingSettings.channel.カテゴリ）
        :param channel_id: チャンネルID
        :return: カテゴリ名(str)またはNone
        """
        info = self.get_channel_info(channel_id=channel_id)
        return info.get("brandingSettings", {}).get("channel", {}).get("category")

    def track_growth(self, channel_id, log_file="growth_log.csv"):
        require_device_cert()
        """
        チャンネル登録者数・再生数の成長をCSVに記録
        :param channel_id: チャンネルID
        :param log_file: ログファイルパス
        :return: 直近記録データ
        """
        import csv, os, datetime
        stats = self.get_channel_statistics(channel_id)
        now = datetime.datetime.now().isoformat()
        row = [now, stats.get("subscriberCount"), stats.get("viewCount")]
        write_header = not os.path.exists(log_file)
        with open(log_file, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if write_header:
                w.writerow(["datetime", "subscriberCount", "viewCount"])
            w.writerow(row)
        return row

    def list_channels(self, channel_ids):
        require_device_cert()
        """
        複数チャンネル情報を一括取得
        :param channel_ids: チャンネルIDリスト
        :return: 情報リスト
        """
        return [self.get_channel_info(channel_id=cid) for cid in channel_ids]
