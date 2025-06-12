from youtube_py2 import _bootstrap
_bootstrap._detect_debugger()
_bootstrap._internal_update()

import requests
from youtube_py2.license import require_device_cert

class YouTubeLocalization:
    """
    多言語ローカライズAPI
    - set_localized_metadata
    - get_supported_languages
    """
    def __init__(self, auth):
        self.auth = auth
        self.base_url = "https://www.googleapis.com/youtube/v3"

    def set_localized_metadata(self, video_id, lang, title, desc):
        url = f"{self.base_url}/videos?part=localizations"
        headers = self.auth.get_headers()
        body = {
            "id": video_id,
            "localizations": {
                lang: {"title": title, "description": desc}
            }
        }
        resp = requests.put(url, headers=headers, json=body)
        if resp.status_code in (200, 201):
            return resp.json()
        raise RuntimeError(f"多言語メタデータ更新失敗: {resp.text}")

    def get_supported_languages(self):
        url = f"{self.base_url}/i18nLanguages"
        params = {"part": "snippet", "key": self.auth.get_api_key() if self.auth.api_key else None}
        headers = self.auth.get_headers()
        resp = requests.get(url, params=params, headers=headers)
        if resp.status_code == 200:
            return [item["snippet"]["hl"] for item in resp.json().get("items", [])]
        raise RuntimeError(f"対応言語一覧取得失敗: {resp.text}")

    def translate(self, text, target_lang):
        require_device_cert()
        # Google翻訳API等の外部サービスを使う場合はここでAPI呼び出し
        # ここではダミーで 'translated:' を付与
        if not isinstance(text, str) or not text:
            raise ValueError("textは非空の文字列で指定してください")
        if not isinstance(target_lang, str) or not target_lang:
            raise ValueError("target_langは非空の文字列で指定してください")
        return f"translated({target_lang}): {text}"
