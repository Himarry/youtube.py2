# This file was generated by Nuitka

# Stubs included by default
from __future__ import annotations
from typing import Any
from typing_extensions import Self
from youtube_py2 import _bootstrap
from youtube_py2.license import require_device_cert
import pandas
import requests

class YouTubeMembership:
    def __init__(self: Self, auth: Any) -> None: ...
    def get_membership_levels(self: Self, channel_id: Any) -> Any: ...
    def get_channel_members(self: Self, channel_id: Any, to_dataframe: Any) -> Any: ...
    def get_membership_info(self: Self, channel_id: Any) -> Any: ...


__name__ = ...



# Modules used internally, to allow implicit dependencies to be seen:
import youtube_py2
import youtube_py2._bootstrap
import requests
import pandas
import youtube_py2.license