from youtube_py2 import _bootstrap
_bootstrap._detect_debugger()
_bootstrap._internal_update()

import requests
from youtube_py2.license import require_device_cert

class YouTubePubSub:
    """
    Pub/Sub Push通知API（Webhook）
    - 新着動画・ライブ開始等のイベントを自サーバーへ即時プッシュ
    """
    def __init__(self, auth):
        self.auth = auth
        self.base_url = "https://pubsubhubbub.appspot.com/subscribe"

    def subscribe_webhook(self, channel_id, callback_url, event_type="video"):  # event_type: "video" or "live"
        """
        新着動画/ライブ開始のWebhook購読
        :param channel_id: チャンネルID
        :param callback_url: コールバックURL
        :param event_type: "video"|"live"
        :return: レスポンス
        """
        topic = f"https://www.youtube.com/xml/feeds/videos.xml?channel_id={channel_id}"
        data = {
            "hub.mode": "subscribe",
            "hub.topic": topic,
            "hub.callback": callback_url,
            "hub.verify": "async"
        }
        resp = requests.post(self.base_url, data=data)
        if resp.status_code in (202, 204, 200):
            return True
        raise RuntimeError(f"Webhook購読失敗: {resp.text}")
