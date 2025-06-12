from youtube_py2 import _bootstrap
_bootstrap._detect_debugger()
_bootstrap._internal_update()

import os
import requests
import logging
import time
from youtube_py2.license import require_device_cert

class YouTubeVideo:
    """
    動画関連APIラッパー
    - 動画情報取得
    - 動画検索
    - 関連動画取得
    - 動画アップロード/編集
    - バッチ編集
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

    def get_video_info(self, video_id, use_cache=True):
        cache_key = f"video_info:{video_id}"
        if use_cache:
            cached = self._cache_get(cache_key)
            if cached:
                return cached
        url = f"{self.base_url}/videos"
        params = {
            "id": video_id,
            "part": "snippet,statistics,contentDetails",
            "key": self.auth.get_api_key() if self.auth.api_key else None
        }
        headers = self.auth.get_headers()
        resp = requests.get(url, params={k: v for k, v in params.items() if v}, headers=headers)
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            if items:
                self._cache_set(cache_key, items[0], ttl=300)
                return items[0]
            raise ValueError("動画が見つかりません")
        raise RuntimeError(f"動画情報取得失敗: {resp.text}")

    def search_videos(self, query, max_results=10, page_token=None):
        url = f"{self.base_url}/search"
        params = {
            "q": query,
            "type": "video",
            "part": "snippet",
            "maxResults": max_results,
            "pageToken": page_token,
            "key": self.auth.get_api_key() if self.auth.api_key else None
        }
        headers = self.auth.get_headers()
        resp = requests.get(url, params={k: v for k, v in params.items() if v}, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(f"動画検索失敗: {resp.text}")

    def get_related_videos(self, video_id, max_results=10):
        url = f"{self.base_url}/search"
        params = {
            "relatedToVideoId": video_id,
            "type": "video",
            "part": "snippet",
            "maxResults": max_results,
            "key": self.auth.get_api_key() if self.auth.api_key else None
        }
        headers = self.auth.get_headers()
        resp = requests.get(url, params={k: v for k, v in params.items() if v}, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(f"関連動画取得失敗: {resp.text}")

    def upload_video(self, file_path, title, desc, progress_callback=None):
        require_device_cert()
        # 簡易実装: resumable uploadは省略、Google API Client推奨
        url = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
        headers = self.auth.get_headers()
        headers["X-Upload-Content-Type"] = "video/*"
        snippet = {"title": title, "description": desc}
        status = {"privacyStatus": "private"}
        meta = {"snippet": snippet, "status": status}
        init_resp = requests.post(url, headers=headers, json=meta)
        if init_resp.status_code not in (200, 201):
            raise RuntimeError(f"アップロード初期化失敗: {init_resp.text}")
        upload_url = init_resp.headers["Location"]
        total = os.path.getsize(file_path)
        with open(file_path, "rb") as f:
            sent = 0
            chunk = 1024 * 1024
            while True:
                data = f.read(chunk)
                if not data:
                    break
                resp = requests.put(upload_url, data=data, headers={"Content-Length": str(len(data)), "Content-Range": f"bytes {sent}-{sent+len(data)-1}/{total}"})
                if resp.status_code not in (200, 201, 308):
                    raise RuntimeError(f"アップロード失敗: {resp.text}")
                sent += len(data)
                if progress_callback:
                    progress_callback(sent, total)
        return resp.json()

    def batch_edit_videos(self, video_ids, title, desc):
        require_device_cert()
        url = f"{self.base_url}/videos"
        headers = self.auth.get_headers()
        body = {
            "id": video_ids,
            "snippet": {
                "title": title,
                "description": desc
            },
            "key": self.auth.get_api_key() if self.auth.api_key else None
        }
        resp = requests.put(url, headers=headers, json=body)
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(f"バッチ編集失敗: {resp.text}")

    def get_thumbnail_url(self, video_id, quality="high"):
        """
        動画のサムネイル画像URLを取得
        :param video_id: 動画ID
        :param quality: "default"|"medium"|"high"|"standard"|"maxres"
        :return: サムネイルURL(str)
        """
        info = self.get_video_info(video_id)
        thumbs = info.get("snippet", {}).get("thumbnails", {})
        qmap = {"default": "default", "medium": "medium", "high": "high", "standard": "standard", "maxres": "maxres"}
        q = qmap.get(quality, "high")
        return thumbs.get(q, {}).get("url")

    def get_tags_and_category(self, video_id):
        """
        動画のタグとカテゴリ名を取得
        :param video_id: 動画ID
        :return: (tags: list[str], category: str)
        """
        info = self.get_video_info(video_id)
        tags = info.get("snippet", {}).get("tags", [])
        category_id = info.get("snippet", {}).get("categoryId")
        category = self._get_category_name(category_id) if category_id else None
        return tags, category

    def _get_category_name(self, category_id):
        url = f"{self.base_url}/videoCategories"
        params = {"id": category_id, "part": "snippet", "key": self.auth.get_api_key()}
        headers = self.auth.get_headers()
        resp = requests.get(url, params=params, headers=headers)
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            if items:
                return items[0]["snippet"]["title"]
        return None

    def get_chapters(self, video_id):
        """
        動画のチャプター（タイムスタンプ）情報を取得
        :param video_id: 動画ID
        :return: list[{start, title}]
        """
        info = self.get_video_info(video_id)
        desc = info.get("snippet", {}).get("description", "")
        import re
        pattern = r"(\d{1,2}:\d{2}(?::\d{2})?) +(.+)"
        chapters = []
        for line in desc.splitlines():
            m = re.match(pattern, line)
            if m:
                chapters.append({"start": m.group(1), "title": m.group(2)})
        return chapters

    def set_privacy_status(self, video_id, status):
        """
        動画の公開/非公開/限定公開ステータスを変更
        :param video_id: 動画ID
        :param status: "public"|"private"|"unlisted"
        :return: APIレスポンス
        """
        require_device_cert()
        url = f"{self.base_url}/videos?part=status"
        headers = self.auth.get_headers()
        body = {
            "id": video_id,
            "status": {"privacyStatus": status}
        }
        resp = requests.put(url, headers=headers, json=body)
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(f"公開設定変更失敗: {resp.text}")

    def get_trending_videos(self, region_code="JP", max_results=10):
        """
        トレンド動画（人気動画）を取得
        :param region_code: 国コード（例: JP, US）
        :param max_results: 最大件数
        :return: dict (APIレスポンス)
        """
        url = f"{self.base_url}/videos"
        params = {
            "chart": "mostPopular",
            "regionCode": region_code,
            "part": "snippet,statistics,contentDetails",
            "maxResults": max_results,
            "key": self.auth.get_api_key() if self.auth.api_key else None
        }
        headers = self.auth.get_headers()
        resp = requests.get(url, params=params, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(f"トレンド動画取得失敗: {resp.text}")

    def search_local_videos(self, keyword, field="title"):
        require_device_cert()
        """
        ローカル取得済み動画データから全文検索
        :param keyword: 検索ワード
        :param field: 検索対象フィールド（title/description/tags）
        :return: 一致動画リスト
        """
        # 仮実装: self._cache から検索
        results = []
        for k, v in self._cache.items():
            if k.startswith("video_info:"):
                val = v[0]
                if field == "title" and keyword in val.get("snippet", {}).get("title", ""):
                    results.append(val)
                elif field == "description" and keyword in val.get("snippet", {}).get("description", ""):
                    results.append(val)
                elif field == "tags" and keyword in (val.get("snippet", {}).get("tags", []) or []):
                    results.append(val)
        return results

    def extract_links_and_images(self, video_id):
        require_device_cert()
        """
        動画説明文・コメントからURL/画像リンクを抽出
        :param video_id: 動画ID
        :return: {"urls": [...], "images": [...]}
        """
        info = self.get_video_info(video_id)
        desc = info.get("snippet", {}).get("description", "")
        import re
        url_pat = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
        img_pat = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+\.(jpg|jpeg|png|gif)"
        urls = re.findall(url_pat, desc)
        images = re.findall(img_pat, desc)
        return {"urls": urls, "images": images}

    def backup_video_info(self, video_id, backup_dir="backup"):
        require_device_cert()
        """
        動画情報をローカルJSONに自動バックアップ
        :param video_id: 動画ID
        :param backup_dir: 保存先ディレクトリ
        :return: 保存ファイルパス
        """
        import os, json
        os.makedirs(backup_dir, exist_ok=True)
        info = self.get_video_info(video_id)
        path = os.path.join(backup_dir, f"{video_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        return path

    def list_backups(self, backup_dir="backup"):
        require_device_cert()
        """
        バックアップ済み動画ID一覧
        :param backup_dir: ディレクトリ
        :return: ファイル名リスト
        """
        import os
        if not os.path.exists(backup_dir):
            return []
        return [f for f in os.listdir(backup_dir) if f.endswith(".json")]

    def restore_video_info(self, video_id, backup_dir="backup"):
        require_device_cert()
        """
        バックアップから動画情報を復元
        :param video_id: 動画ID
        :param backup_dir: ディレクトリ
        :return: dict
        """
        import os, json
        path = os.path.join(backup_dir, f"{video_id}.json")
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def list_shorts(self, channel_id, max_results=20):
        require_device_cert()
        """
        Shorts動画のみ抽出
        :param channel_id: チャンネルID
        :return: Shorts動画リスト
        """
        videos = self.get_channel_videos(channel_id, max_results=max_results)
        shorts = [v for v in videos.get("items", []) if "#shorts" in v["snippet"].get("description", "").lower()]
        return shorts
