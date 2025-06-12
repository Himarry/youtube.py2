# youtube_py2 パッケージ初期化ファイル
__version__ = "1.0.26"

import os
import sys


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
