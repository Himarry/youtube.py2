# This file was generated by Nuitka

# Stubs included by default
from __future__ import annotations
from typing import Any
from typing_extensions import Self
from youtube_py2 import _bootstrap
from youtube_py2.license import require_device_cert
import asyncio
import requests

class YouTubeAsync:
    def __init__(self: Self, auth: Any) -> None: ...
    def async_request(self: Self, func: Any) -> Any: ...


__name__ = ...



# Modules used internally, to allow implicit dependencies to be seen:
import youtube_py2
import youtube_py2._bootstrap
import asyncio
import requests
import youtube_py2.license
import aiohttp