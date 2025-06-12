# youtube_py2 パッケージ初期化ファイル
__version__ = "1.0.24"

import os
import sys

def _run_security_checks():
    try:
        from youtube_py2 import _bootstrap
        print(f"[DEBUG] _bootstrap: {_bootstrap}")
        if not hasattr(_bootstrap, '_detect_debugger') or _bootstrap._detect_debugger is None:
            print("[アンチデバッグ] _detect_debugger が None です。スキップします。", file=sys.stderr)
            return
        _bootstrap._detect_debugger()
        _bootstrap._internal_update()
    except Exception as e:
        print(f"[アンチデバッグ] {e}", file=sys.stderr)
        os._exit(1)

_run_security_checks()

# 主要APIクラスをトップレベルで再エクスポート
from .video import YouTubeVideo
from .channel import YouTubeChannel
from .comment import YouTubeComment
from .playlist import YouTubePlaylist
from .captions import YouTubeCaptions
from .auth import YouTubeAuth
from .analytics import YouTubeAnalytics
from .export import YouTubeExport
from .async_api import YouTubeAsync
from .cli import YouTubeCLI
from .logging import YouTubeLogger
from .live import YouTubeLive
from .membership import YouTubeMembership
from .pagination import YouTubePagination
from .pubsub import YouTubePubSub
from .localization import YouTubeLocalization
from .license import require_device_cert

__all__ = [
    "YouTubeVideo", "YouTubeChannel", "YouTubeComment", "YouTubePlaylist", "YouTubeCaptions",
    "YouTubeAuth", "YouTubeAnalytics", "YouTubeExport", "YouTubeAsync", "YouTubeCLI", "YouTubeLogger",
    "YouTubeLive", "YouTubeMembership", "YouTubePagination", "YouTubePubSub", "YouTubeLocalization",
    "require_device_cert"
]
