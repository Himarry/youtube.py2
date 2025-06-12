# youtube_py2 パッケージ初期化ファイル
__version__ = "1.0.23"

import os
import sys

if os.environ.get("YOUTUBE_PY2_DEBUG", "") == "1":
    try:
        from . import _bootstrap
        print(f"[DEBUG] _bootstrap: {_bootstrap}")
        if hasattr(_bootstrap, '_detect_debugger') and _bootstrap._detect_debugger is not None:
            _bootstrap._detect_debugger()
            _bootstrap._internal_update()
        else:
            print("[アンチデバッグ] _detect_debugger が None です。スキップします。", file=sys.stderr)
    except Exception as e:
        print(f"[アンチデバッグ] {e}", file=sys.stderr)
        # os._exit(1)  # PyPI公開物では強制終了は基本入れない


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
