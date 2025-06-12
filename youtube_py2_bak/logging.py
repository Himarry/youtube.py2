from youtube_py2 import _bootstrap
_bootstrap._detect_debugger()
_bootstrap._internal_update()

import logging
from youtube_py2.license import require_device_cert

class YouTubeLogger:
    """
    APIリクエスト/レスポンス・エラーのロギング
    """
    def __init__(self, log_file="youtube_api.log"):
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s"
        )
        self.logger = logging.getLogger("YouTubeAPI")

    def log_request(self, url, params):
        require_device_cert()
        self.logger.info(f"リクエスト: {url} params={params}")

    def log_response(self, resp):
        require_device_cert()
        self.logger.info(f"レスポンス: {resp.status_code} {resp.text}")

    def log_error(self, msg):
        require_device_cert()
        self.logger.error(msg)

    def enable_debug(self):
        require_device_cert()
        # ログレベルをDEBUGに変更し、標準出力にも出力
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        if not any(isinstance(h, logging.StreamHandler) for h in self.logger.handlers):
            self.logger.addHandler(handler)
        self.logger.debug("デバッグモード有効化")
