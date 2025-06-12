from youtube_py2 import _bootstrap
_bootstrap._detect_debugger()
_bootstrap._internal_update()

import requests
import logging
from youtube_py2.license import require_device_cert
from googletrans import Translator

class YouTubeComment:
    """
    コメント関連APIラッパー
    - 動画コメントリスト取得
    - コメント感情分析
    """
    def __init__(self, auth):
        self.auth = auth
        self.base_url = "https://www.googleapis.com/youtube/v3"

    def get_comments(self, video_id, exclude_owner=False, top_level_only=False, replies_only=False, no_replies=False, sentiment=False, max_results=100, fetch_all=True, owner_channel_id=None, ng_words=None, spam_patterns=None):
        require_device_cert()
        if any([exclude_owner, top_level_only, replies_only, no_replies, ng_words, spam_patterns]):
            require_device_cert()
        """
        動画コメント取得 + NGワード/スパム自動フィルタ
        :param video_id: 動画ID
        :param exclude_owner: チャンネル運営者以外のみ取得
        :param top_level_only: トップレベルのコメントのみ取得
        :param replies_only: 返信があるコメントのみ取得
        :param no_replies: 返信がないコメントのみ取得
        :param sentiment: 感情分析を付与
        :param max_results: 1ページあたり最大件数
        :param fetch_all: 全ページ取得
        :param owner_channel_id: 運営者のチャンネルID（自動取得しない場合は明示指定）
        :param ng_words: NGワードリスト（部分一致で除外）
        :param spam_patterns: スパム判定用正規表現リスト
        :return: list[dict]
        """
        url = f"{self.base_url}/commentThreads"
        params = {
            "videoId": video_id,
            "part": "snippet,replies",
            "maxResults": max_results,
            "textFormat": "plainText",
            "key": self.auth.get_api_key() if self.auth.api_key else None
        }
        headers = self.auth.get_headers()
        comments = []
        next_page = None
        # 運営者ID自動取得
        if exclude_owner and not owner_channel_id:
            owner_channel_id = self._get_video_owner_channel_id(video_id)
        while True:
            if next_page:
                params["pageToken"] = next_page
            resp = requests.get(url, params={k: v for k, v in params.items() if v}, headers=headers)
            if resp.status_code != 200:
                raise RuntimeError(f"コメント取得失敗: {resp.text}")
            data = resp.json()
            for item in data.get("items", []):
                snippet = item["snippet"]["topLevelComment"]["snippet"]
                author_id = snippet.get("authorChannelId", {}).get("value")
                has_replies = bool(item.get("replies"))
                # フィルタ適用
                if exclude_owner and owner_channel_id and author_id == owner_channel_id:
                    continue
                if top_level_only and has_replies:
                    continue
                if replies_only and not has_replies:
                    continue
                if no_replies and has_replies:
                    continue
                comment = {
                    "author": snippet.get("authorDisplayName"),
                    "text": snippet.get("textDisplay"),
                    "likeCount": snippet.get("likeCount"),
                    "publishedAt": snippet.get("publishedAt"),
                    "updatedAt": snippet.get("updatedAt")
                }
                # NGワード/スパムフィルタ
                if ng_words and any(w in comment["text"] for w in ng_words):
                    continue
                if spam_patterns:
                    import re
                    if any(re.search(p, comment["text"]) for p in spam_patterns):
                        continue
                if sentiment:
                    comment["sentiment"] = self.analyze_sentiment(comment["text"])
                comments.append(comment)
            next_page = data.get("nextPageToken")
            if not fetch_all or not next_page:
                break
        return comments

    def analyze_sentiment(self, text):
        require_device_cert()
        # 簡易感情分析: ポジ/ネガ単語数で判定
        pos_words = ["good", "great", "love", "excellent", "awesome", "best", "like"]
        neg_words = ["bad", "hate", "worst", "awful", "terrible", "dislike"]
        score = sum(w in text.lower() for w in pos_words) - sum(w in text.lower() for w in neg_words)
        if score > 0:
            return "positive"
        elif score < 0:
            return "negative"
        return "neutral"

    def _get_video_owner_channel_id(self, video_id):
        # 動画の運営者チャンネルIDを取得
        url = f"https://www.googleapis.com/youtube/v3/videos"
        params = {
            "id": video_id,
            "part": "snippet",
            "key": self.auth.get_api_key() if self.auth.api_key else None
        }
        headers = self.auth.get_headers()
        resp = requests.get(url, params=params, headers=headers)
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            if items:
                return items[0]["snippet"].get("channelId")
        return None

    def translate_comment(self, text, target_lang="ja"):
        require_device_cert()
        """
        コメントテキストを自動翻訳（googletransライブラリ使用）
        :param text: 翻訳元
        :param target_lang: 翻訳先言語
        :return: 翻訳後テキスト
        """
        translator = Translator()
        result = translator.translate(text, dest=target_lang)
        return result.text

    def learn_ng_words(self, comments, min_count=2):
        require_device_cert()
        """
        コメントリストから頻出NGワードを自動抽出（簡易）
        :param comments: コメントリスト
        :param min_count: 最低出現回数
        :return: NGワード候補リスト
        """
        from collections import Counter
        import re
        words = []
        for c in comments:
            words += re.findall(r"\w+", c["text"])
        freq = Counter(words)
        return [w for w, cnt in freq.items() if cnt >= min_count and len(w) > 3]
