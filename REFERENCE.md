# youtube_py2 APIリファレンス

## 概要

YouTube Data API v3 Pythonラッパー「youtube_py2」の全機能APIリファレンスです。  
各クラス・メソッド・パラメータ・戻り値・例外・利用条件（有料/無料）を網羅します。

---

## モジュール一覧

- analytics
- async_api
- auth
- captions
- channel
- cli
- comment
- export
- license
- live
- localization
- logging
- membership
- pagination
- playlist
- pubsub
- video

---

## 各モジュール詳細

---

### youtube_py2.analytics

#### クラス: `YouTubeAnalytics`

YouTube Analytics & Reporting API

- **`__init__(auth)`**
  - `auth`: 認証情報（YouTubeAuthインスタンス）

- **`get_analytics(channel_id, metrics, start_date, end_date)`**
  - `channel_id`: チャンネルID（str）
  - `metrics`: メトリクス名リスト（list[str]）
  - `start_date`: 開始日（YYYY-MM-DD, str）
  - `end_date`: 終了日（YYYY-MM-DD, str）
  - **戻り値**: dict（APIレスポンス）
  - **例外**: RuntimeError

- **`download_bulk_reports(channel_id, metrics, save_path)`**
  - `channel_id`: チャンネルID
  - `metrics`: メトリクス名リスト
  - `save_path`: 保存先パス
  - **戻り値**: 保存ファイルパス
  - **例外**: 失敗時RuntimeError

- **`get_analytics_report(channel_id, metrics, start_date, end_date)`**（有料機能/証明書必須）
  - `channel_id`, `metrics`, `start_date`, `end_date`: 上記同様
  - **戻り値**: pandas.DataFrame
  - **例外**: ValueError, RuntimeError

---

### youtube_py2.async_api

#### クラス: `YouTubeAsync`

非同期APIユーティリティ

- **`__init__(auth)`**
  - `auth`: 認証情報

- **`fetch(session, url, params, headers)`**
  - `session`: aiohttp.ClientSession
  - `url`: リクエストURL
  - `params`: パラメータdict
  - `headers`: ヘッダーdict
  - **戻り値**: dict

- **`fetch_many(urls_params)`**
  - `urls_params`: (url, params, headers)のリスト
  - **戻り値**: list[dict]

- **`async_request(func, *args, **kwargs)`**（有料機能/証明書必須）
  - 任意の同期関数を非同期実行
  - **戻り値**: Future

---

### youtube_py2.auth

#### クラス: `YouTubeAuth`

APIキー・OAuth2認証管理

- **`__init__(api_key=None, client_id=None, client_secret=None, refresh_token=None, token_file="token.json")`**
  - 各種認証情報

- **`load_token()`**
  - トークンファイルからアクセストークン読込

- **`save_token(token_data)`**
  - トークン情報保存

- **`get_access_token()`**
  - **戻り値**: str（アクセストークン）
  - **例外**: RuntimeError

- **`refresh_access_token()`**
  - **戻り値**: str（新アクセストークン）
  - **例外**: RuntimeError

- **`get_headers()`**
  - **戻り値**: dict（APIリクエスト用ヘッダー）

- **`log_quota(cost)`**
  - クォータ消費記録

- **`set_quota_threshold(threshold, throttle_callback)`**
  - クォータ閾値設定

- **`get_api_key()`**
  - **戻り値**: str（APIキー）
  - **例外**: RuntimeError

---

### youtube_py2.captions

#### クラス: `YouTubeCaptions`

字幕API

- **`__init__(auth)`**
- **`captions_list(video_id)`**
  - **戻り値**: 字幕リスト
- **`captions_download(caption_id, to_format="srt")`**
  - **戻り値**: 字幕テキスト
- **`captions_insert(video_id, file_path, lang)`**
  - **戻り値**: dict
- **`get_captions(video_id)`**（有料機能/証明書必須）
  - **戻り値**: 字幕＋データリスト
- **`translate_video(video_id, target_lang)`**（有料機能/証明書必須）
  - **戻り値**: 翻訳済み字幕テキスト

---

### youtube_py2.channel

#### クラス: `YouTubeChannel`

チャンネル情報API

- **`__init__(auth)`**
- **`get_channel_info(channel_id=None, for_username=None)`**
  - **戻り値**: dict（チャンネル情報）
- **`get_channel_videos(channel_id, max_results=50, page_token=None)`**
  - **戻り値**: dict（動画リスト）
- **`get_channel_statistics(channel_id)`**
  - **戻り値**: dict（統計情報）
- **`get_subscriptions(channel_id, max_results=50, page_token=None)`**
  - **戻り値**: dict（登録チャンネルリスト）

---

### youtube_py2.cli

#### クラス: `YouTubeCLI`

コマンドラインツール

- **`__init__(video_api, channel_api, license_key=None)`**
- **`run()`**
  - コマンドライン引数で動画検索・チャンネル情報取得

---

### youtube_py2.comment

#### クラス: `YouTubeComment`

コメントAPI

- **`__init__(auth)`**
- **`get_comments(video_id, exclude_owner=False, top_level_only=False, replies_only=False, no_replies=False, sentiment=False, max_results=100, fetch_all=True)`**
  - **戻り値**: コメントリスト
- **`analyze_sentiment(text)`**（有料機能/証明書必須）
  - **戻り値**: "positive"|"negative"|"neutral"

---

### youtube_py2.export

#### クラス: `YouTubeExport`

データエクスポート

- **`to_dataframe(data)`**
  - **戻り値**: pandas.DataFrame
- **`to_csv(data, file_path)`**
- **`to_json(data, file_path)`**
- **`export_to_csv(data, file_path)`**（有料機能/証明書必須）

---

### youtube_py2.license

#### クラス: `LicenseKeyGenerator`

- **`generate_key(length=32)`**
  - **戻り値**: str（新ライセンスキー）

#### クラス: `LicenseManager`

- **`check_license(license_key, api_url=...)`**
  - **戻り値**: dict（認証結果）
- **`require_license(license_key=None)`**
  - **例外**: ライセンス無効時
- **`last_result()`**
  - **戻り値**: dict（直近認証結果）

#### 関数: `require_device_cert()`
- 端末証明書がなければ例外

---

### youtube_py2.live

#### クラス: `YouTubeLive`

ライブ配信API

- **`__init__(auth)`**
- **`stream_live_chat(live_chat_id, callback, poll_interval=2)`**
- **`get_super_chat_events(live_chat_id, callback, poll_interval=2)`**
- **`start_live_stream(stream_title, stream_desc, privacy_status="private")`**（有料機能/証明書必須）

---

### youtube_py2.localization

#### クラス: `YouTubeLocalization`

多言語ローカライズAPI

- **`__init__(auth)`**
- **`set_localized_metadata(video_id, lang, title, desc)`**
- **`get_supported_languages()`**
- **`translate(text, target_lang)`**（有料機能/証明書必須）

---

### youtube_py2.logging

#### クラス: `YouTubeLogger`

APIリクエスト・レスポンス・エラーのロギング

- **`__init__(log_file="youtube_api.log")`**
- **`log_request(url, params)`**
- **`log_response(resp)`**
- **`log_error(msg)`**
- **`enable_debug()`**（有料機能/証明書必須）

---

### youtube_py2.membership

#### クラス: `YouTubeMembership`

チャンネルメンバーシップAPI

- **`__init__(auth)`**
- **`get_membership_levels(channel_id)`**
- **`get_channel_members(channel_id, to_dataframe=True)`**
- **`get_membership_info(channel_id)`**（有料機能/証明書必須）

---

### youtube_py2.pagination

#### クラス: `YouTubePagination`

ページネーションユーティリティ

- **`fetch_all(fetch_func, *args, max_total=1000, **kwargs)`**
  - **戻り値**: itemsリスト

---

### youtube_py2.playlist

#### クラス: `YouTubePlaylist`

プレイリストAPI

- **`__init__(auth)`**
- **`get_playlist_info(playlist_id)`**
- **`get_playlist_items(playlist_id, max_results=50, page_token=None)`**
- **`get_channel_playlists(channel_id, max_results=50, page_token=None)`**

---

### youtube_py2.pubsub

#### クラス: `YouTubePubSub`

Pub/Sub Push通知API

- **`__init__(auth)`**
- **`subscribe_pubsub(topic, callback_url)`**（有料機能/証明書必須）

---

### youtube_py2.video

#### クラス: `YouTubeVideo`

動画API

- **`__init__(auth)`**
- **`get_video_info(video_id)`**
- **`search_videos(query, max_results=10, page_token=None)`**
- **`get_related_videos(video_id, max_results=10)`**
- **`upload_video(file_path, title, desc, progress_callback=None)`**（有料機能/証明書必須）
- **`batch_edit_videos(video_ids, title, desc)`**（有料機能/証明書必須）

---

## 注意事項

- 「有料機能/証明書必須」：端末証明書(device_cert.pem)が必要です。  
- すべてのAPIは例外処理・バリデーションが実装されています。
- 詳細な型・例外・サンプルは各クラスのdocstringも参照してください。

---

このリファレンスは最新版コードベースに基づき自動生成されています。  
他モジュールや詳細なサンプルが必要な場合はご指示ください。

---

## 使い方サンプル

---

### youtube_py2.video

#### クラス: `YouTubeVideo` の使い方

```python
from youtube_py2 import YouTubeAuth, YouTubeVideo

auth = YouTubeAuth(api_key="YOUR_API_KEY")
video_api = YouTubeVideo(auth)

# 動画情報を取得
info = video_api.get_video_info("VIDEO_ID")
print(info)

# 動画検索
results = video_api.search_videos("猫", max_results=5)
for item in results["items"]:
    print(item["snippet"]["title"])

# 関連動画取得
related = video_api.get_related_videos("VIDEO_ID")

# 動画アップロード（有料機能/証明書必須）
# video_api.upload_video("movie.mp4", "タイトル", "説明")

# バッチ編集（有料機能/証明書必須）
# video_api.batch_edit_videos(["VIDEO_ID1", "VIDEO_ID2"], "新タイトル", "新説明")
```

---

### youtube_py2.channel

#### クラス: `YouTubeChannel` の使い方

```python
from youtube_py2 import YouTubeAuth, YouTubeChannel

auth = YouTubeAuth(api_key="YOUR_API_KEY")
channel_api = YouTubeChannel(auth)

# チャンネル情報取得
info = channel_api.get_channel_info(channel_id="CHANNEL_ID")
print(info["snippet"]["title"])

# チャンネル動画一覧
videos = channel_api.get_channel_videos("CHANNEL_ID")

# チャンネル統計情報
stats = channel_api.get_channel_statistics("CHANNEL_ID")

# 登録チャンネル一覧
subs = channel_api.get_subscriptions("CHANNEL_ID")
```

---

### youtube_py2.auth

#### クラス: `YouTubeAuth` の使い方

```python
from youtube_py2 import YouTubeAuth

auth = YouTubeAuth(api_key="YOUR_API_KEY")
headers = auth.get_headers()
api_key = auth.get_api_key()
```

---

### youtube_py2.analytics

#### クラス: `YouTubeAnalytics` の使い方

```python
from youtube_py2 import YouTubeAuth, YouTubeAnalytics

auth = YouTubeAuth(api_key="YOUR_API_KEY")
analytics = YouTubeAnalytics(auth)

# アナリティクス取得
result = analytics.get_analytics("CHANNEL_ID", ["views", "likes"], "2024-01-01", "2024-01-31")

# レポートCSV保存
analytics.download_bulk_reports("CHANNEL_ID", ["views"], "report.csv")

# DataFrameで取得（有料機能/証明書必須）
df = analytics.get_analytics_report("CHANNEL_ID", ["views"], "2024-01-01", "2024-01-31")
```

---

### youtube_py2.captions

#### クラス: `YouTubeCaptions` の使い方

```python
from youtube_py2 import YouTubeAuth, YouTubeCaptions

auth = YouTubeAuth(api_key="YOUR_API_KEY")
captions = YouTubeCaptions(auth)

# 字幕リスト取得
items = captions.captions_list("VIDEO_ID")

# 字幕ダウンロード
srt = captions.captions_download("CAPTION_ID")

# 字幕アップロード
# captions.captions_insert("VIDEO_ID", "file.srt", "ja")

# 字幕＋データ取得（有料機能/証明書必須）
# captions.get_captions("VIDEO_ID")

# 翻訳（有料機能/証明書必須）
# captions.translate_video("VIDEO_ID", "en")
```

---

### youtube_py2.comment

#### クラス: `YouTubeComment` の使い方

```python
from youtube_py2 import YouTubeAuth, YouTubeComment

auth = YouTubeAuth(api_key="YOUR_API_KEY")
comment_api = YouTubeComment(auth)

# コメント取得
comments = comment_api.get_comments("VIDEO_ID", max_results=10)
for c in comments:
    print(c["author"], c["text"])

# 簡易感情分析（有料機能/証明書必須）
# sentiment = comment_api.analyze_sentiment("I love this video!")
```

---

### youtube_py2.playlist

#### クラス: `YouTubePlaylist` の使い方

```python
from youtube_py2 import YouTubeAuth, YouTubePlaylist

auth = YouTubeAuth(api_key="YOUR_API_KEY")
playlist_api = YouTubePlaylist(auth)

# プレイリスト情報取得
info = playlist_api.get_playlist_info("PLAYLIST_ID")

# プレイリスト内動画一覧
items = playlist_api.get_playlist_items("PLAYLIST_ID")

# チャンネルの全プレイリスト
lists = playlist_api.get_channel_playlists("CHANNEL_ID")
```

---

### youtube_py2.export

#### クラス: `YouTubeExport` の使い方

```python
from youtube_py2 import YouTubeExport

exporter = YouTubeExport()
data = [{"id": 1, "name": "test"}]

# DataFrame化
import pandas as pd
df = exporter.to_dataframe(data)

# CSV出力
exporter.to_csv(data, "out.csv")

# JSON出力
exporter.to_json(data, "out.json")

# 有料機能/証明書必須
# exporter.export_to_csv(data, "out.csv")
```

---

### youtube_py2.async_api

#### クラス: `YouTubeAsync` の使い方

```python
from youtube_py2 import YouTubeAuth, YouTubeAsync
import asyncio

auth = YouTubeAuth(api_key="YOUR_API_KEY")
async_api = YouTubeAsync(auth)

# 非同期で複数リクエスト
async def main():
    urls_params = [
        ("https://www.googleapis.com/youtube/v3/videos", {"id": "VIDEO_ID", "part": "snippet"}, auth.get_headers())
    ]
    results = await async_api.fetch_many(urls_params)
    print(results)

# asyncio.run(main())
```

---

### youtube_py2.cli

#### クラス: `YouTubeCLI` の使い方

```sh
python -m youtube_py2.cli search "猫"
python -m youtube_py2.cli --channel CHANNEL_ID
```

---

### youtube_py2.logging

#### クラス: `YouTubeLogger` の使い方

```python
from youtube_py2 import YouTubeLogger

logger = YouTubeLogger()
logger.log_request("https://api.example.com", {"q": "test"})
logger.log_error("エラー内容")
logger.enable_debug()  # 有料機能/証明書必須
```

---

### youtube_py2.live

#### クラス: `YouTubeLive` の使い方

```python
from youtube_py2 import YouTubeAuth, YouTubeLive

auth = YouTubeAuth(api_key="YOUR_API_KEY")
live_api = YouTubeLive(auth)

def on_chat(item):
    print(item)

# ライブチャット取得（スレッドで自動実行）
live_api.stream_live_chat("LIVE_CHAT_ID", on_chat)

# SuperChatイベント取得
def on_superchat(item):
    print(item)
live_api.get_super_chat_events("LIVE_CHAT_ID", on_superchat)

# ライブ配信開始（有料機能/証明書必須）
# live_api.start_live_stream("タイトル", "説明")
```

---

### youtube_py2.membership

#### クラス: `YouTubeMembership` の使い方

```python
from youtube_py2 import YouTubeAuth, YouTubeMembership

auth = YouTubeAuth(api_key="YOUR_API_KEY")
membership_api = YouTubeMembership(auth)

# メンバーシップレベル取得
levels = membership_api.get_membership_levels("CHANNEL_ID")

# メンバー一覧
members = membership_api.get_channel_members("CHANNEL_ID")

# メンバーシップ情報（有料機能/証明書必須）
# info = membership_api.get_membership_info("CHANNEL_ID")
```

---

### youtube_py2.pubsub

#### クラス: `YouTubePubSub` の使い方

```python
from youtube_py2 import YouTubeAuth, YouTubePubSub

auth = YouTubeAuth(api_key="YOUR_API_KEY")
pubsub = YouTubePubSub(auth)

# PubSub登録（有料機能/証明書必須）
# pubsub.subscribe_pubsub("https://www.youtube.com/xml/feeds/videos.xml?channel_id=CHANNEL_ID", "https://your.server/callback")
```

---

### youtube_py2.localization

#### クラス: `YouTubeLocalization` の使い方

```python
from youtube_py2 import YouTubeAuth, YouTubeLocalization

auth = YouTubeAuth(api_key="YOUR_API_KEY")
localization = YouTubeLocalization(auth)

# 多言語メタデータ設定
localization.set_localized_metadata("VIDEO_ID", "en", "English Title", "English Desc")

# 対応言語一覧
langs = localization.get_supported_languages()

# 翻訳（有料機能/証明書必須）
# localization.translate("こんにちは", "en")
```

---

### youtube_py2.pagination

#### クラス: `YouTubePagination` の使い方

```python
from youtube_py2 import YouTubePagination

pagination = YouTubePagination()
# 例: チャンネル動画を最大200件まとめて取得
# all_videos = pagination.fetch_all(channel_api.get_channel_videos, "CHANNEL_ID", max_total=200)
```

---

### youtube_py2.license

#### クラス: `LicenseKeyGenerator` / `LicenseManager` の使い方

```python
from youtube_py2 import LicenseKeyGenerator, LicenseManager

# ライセンスキー生成
key = LicenseKeyGenerator.generate_key()

# ライセンス認証
result = LicenseManager.check_license(key)

# 有料機能利用時
# LicenseManager.require_license(key)
```

---

## 無料機能・有料機能一覧

| モジュール         | クラス/メソッド名                       | 無料/有料 | 備考・証明書要否 |
|-------------------|------------------------------------------|-----------|-----------------|
| video             | get_video_info, search_videos, get_related_videos | 無料      |                 |
| video             | upload_video, batch_edit_videos           | 有料      | device_cert.pem 必須 |
| channel           | 全メソッド                               | 無料      |                 |
| auth              | 全メソッド                               | 無料      |                 |
| analytics         | get_analytics, download_bulk_reports      | 無料      |                 |
| analytics         | get_analytics_report                      | 有料      | device_cert.pem 必須 |
| captions          | captions_list, captions_download, captions_insert | 無料      |                 |
| captions          | get_captions, translate_video             | 有料      | device_cert.pem 必須 |
| comment           | get_comments                             | 無料      |                 |
| comment           | analyze_sentiment                         | 有料      | device_cert.pem 必須 |
| playlist          | 全メソッド                               | 無料      |                 |
| export            | to_dataframe, to_csv, to_json             | 無料      |                 |
| export            | export_to_csv                             | 有料      | device_cert.pem 必須 |
| async_api         | fetch, fetch_many                         | 無料      |                 |
| async_api         | async_request                             | 有料      | device_cert.pem 必須 |
| cli               | 全機能                                   | 無料      |                 |
| logging           | log_request, log_response, log_error       | 無料      |                 |
| logging           | enable_debug                              | 有料      | device_cert.pem 必須 |
| live              | stream_live_chat, get_super_chat_events    | 無料      |                 |
| live              | start_live_stream                         | 有料      | device_cert.pem 必須 |
| membership        | get_membership_levels, get_channel_members | 無料      |                 |
| membership        | get_membership_info                       | 有料      | device_cert.pem 必須 |
| pubsub            | subscribe_pubsub                          | 有料      | device_cert.pem 必須 |
| localization      | set_localized_metadata, get_supported_languages | 無料      |                 |
| localization      | translate                                 | 有料      | device_cert.pem 必須 |
| pagination        | fetch_all                                 | 無料      |                 |
| license           | 全メソッド                                | 無料      |                 |

- 「有料」機能は device_cert.pem（端末証明書）が必要です。
- 無料機能はAPIキーのみで利用可能です。
