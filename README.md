# youtube.py2

youtube.py3を廃止し、youtube.py2に以降しました。
※youtube.py3は公開自体はされていますが機能はしないようにしています※

## インストール

```sh
pip install youtube_py2
```

## クイックスタート

```python
import youtube_py2

yt = youtube_py2.YouTube(api_key="YOUR_API_KEY")
# 動画情報取得
info = yt.videos.get_video("動画ID")
```

## バイナリ配布・型スタブのみ公開について

本リポジトリでは `.pyi`（型スタブ）ファイルのみを公開し、実際の `.py`（Pythonソース）や `.pyd`（バイナリ本体）は公開していません。

- `.pyi` ファイルは型情報や関数シグネチャのみを記述したダミーファイルです。
- `.pyi` だけではライブラリ本体の機能は一切動作しません。
- ソースコードをダウンロードしても、**本体のAPIや機能は利用できません**。
- 実際のAPIを利用するには、PyPI等で配布される `.pyd` バイナリ本体が必要です。

> **この方式により、ソース流出や不正利用を防止しています。**

---

## 開発者専用機能・一般機能について（2025年6月11日現在）

- 開発者専用機能の利用には device_cert.pem（端末証明書）が必須です。
- ※pypiからダウンロードして使おうとしても動きません※
- 一般機能はAPIキーのみで利用可能です。
- CLI（コマンドラインツール）も開発者専用機能です。

### 一般機能一覧
- channel（チャンネル情報API）: get_channel_info, get_channel_videos, get_channel_statistics, get_subscriptions, search_channels など
- auth（認証API）: 全メソッド
- analytics: get_analytics, download_bulk_reports
- pagination: fetch_all
- localization: set_localized_metadata, get_supported_languages
- license: 全メソッド

### 開発者専用機能一覧（device_cert.pem必須）
- video: get_video_info, search_videos, get_related_videos, upload_video, batch_edit_videos など
- playlist: get_playlist_info, get_playlist_items, get_channel_playlists
- comment: get_comments, analyze_sentiment
- captions: captions_list, captions_download, captions_insert, get_captions, translate_video
- export: to_dataframe, to_csv, to_json, export_to_csv
- async_api: fetch, fetch_many, async_request
- logging: log_request, log_response, log_error, enable_debug
- live: stream_live_chat, get_super_chat_events, start_live_stream
- membership: get_membership_levels, get_channel_members, get_membership_info
- pubsub: subscribe_webhook
- CLI: 全サブコマンド（search, channel, dates, auto-playlist, rating, comment-like, embed, share など）

---

- 開発者専用機能は device_cert.pem（端末証明書）が必要です。
- 
  ※これらの機能のライセンス配布は行っておりません。
  これらの機能はまだベータ版であり、動作確認が十分にできていないため、一般公開・サポートは行っていません。
  利用を希望する場合は、自身で解析をしてご対応ください。
- 一般機能はAPIキーのみで利用可能です。

---


