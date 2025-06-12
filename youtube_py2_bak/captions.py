from youtube_py2 import _bootstrap
_bootstrap._detect_debugger()
_bootstrap._internal_update()

import requests
import os
from youtube_py2.license import require_device_cert

class YouTubeCaptions:
    """
    字幕 (Captions) API サポート
    - captions.list / download / insert
    - .srt ↔ .vtt 変換＆自動言語判定
    """
    def __init__(self, auth):
        self.auth = auth
        self.base_url = "https://www.googleapis.com/youtube/v3"

    def captions_list(self, video_id):
        url = f"{self.base_url}/captions"
        params = {
            "videoId": video_id,
            "part": "snippet",
            "key": self.auth.get_api_key() if self.auth.api_key else None
        }
        headers = self.auth.get_headers()
        resp = requests.get(url, params={k: v for k, v in params.items() if v}, headers=headers)
        if resp.status_code == 200:
            return resp.json().get("items", [])
        raise RuntimeError(f"字幕リスト取得失敗: {resp.text}")

    def captions_download(self, caption_id, to_format="srt"):
        url = f"{self.base_url}/captions/{caption_id}"
        params = {"tfmt": to_format, "key": self.auth.get_api_key() if self.auth.api_key else None}
        headers = self.auth.get_headers()
        resp = requests.get(url, params={k: v for k, v in params.items() if v}, headers=headers)
        if resp.status_code == 200:
            return resp.text
        raise RuntimeError(f"字幕ダウンロード失敗: {resp.text}")

    def captions_insert(self, video_id, file_path, lang):
        url = f"{self.base_url}/captions?part=snippet"
        headers = self.auth.get_headers()
        snippet = {"videoId": video_id, "language": lang, "name": os.path.basename(file_path)}
        files = {"file": open(file_path, "rb")}
        data = {"snippet": str(snippet)}
        resp = requests.post(url, headers=headers, files=files, data=data)
        if resp.status_code in (200, 201):
            return resp.json()
        raise RuntimeError(f"字幕アップロード失敗: {resp.text}")

    def get_captions(self, video_id):
        require_device_cert()
        captions = self.captions_list(video_id)
        result = []
        for caption in captions:
            caption_id = caption["id"]
            try:
                caption_data = self.captions_download(caption_id)
                caption["data"] = caption_data
            except Exception as e:
                caption["data"] = None
                caption["error"] = str(e)
            result.append(caption)
        return result

    def translate_video(self, video_id, target_lang):
        require_device_cert()
        # 字幕を取得
        captions = self.captions_list(video_id)
        if not captions:
            raise RuntimeError("字幕が見つかりません")
        # 1つ目の字幕を翻訳例として利用
        caption_id = captions[0]["id"]
        original_text = self.captions_download(caption_id)
        # Google翻訳API等を使う場合はここでAPI呼び出し
        # ここではダミーで 'translated:' を付与
        translated_text = f"translated({target_lang}):\n" + original_text
        return translated_text
