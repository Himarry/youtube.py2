from youtube_py2 import _bootstrap
_bootstrap._detect_debugger()
_bootstrap._internal_update()

import argparse
import sys
import logging
from youtube_py2.license import require_device_cert

class YouTubeCLI:
    """
    コマンドラインツール（開発者専用機能）
    - 動画検索やチャンネル情報取得などをCLIで実行
    - 利用にはdevice_cert.pemが必須
    """
    def __init__(self, video_api, channel_api, license_key=None):
        self.video_api = video_api
        self.channel_api = channel_api
        self.license_key = license_key

    def run(self):
        require_device_cert()
        parser = argparse.ArgumentParser(description="YouTube Data API v3 CLI")
        subparsers = parser.add_subparsers(dest="command")

        # 動画検索
        parser_search = subparsers.add_parser("search", help="動画検索")
        parser_search.add_argument("query", help="検索キーワード")

        # チャンネル情報取得
        parser_channel = subparsers.add_parser("channel", help="チャンネル情報取得")
        parser_channel.add_argument("channel_id", help="チャンネルID")

        # 動画・チャンネルの登録日・最終更新日取得
        parser_dates = subparsers.add_parser("dates", help="動画・チャンネルの登録日・最終更新日取得")
        parser_dates.add_argument("type", choices=["video", "channel"], help="video or channel")
        parser_dates.add_argument("id", help="ID")

        # 動画の再生リスト自動生成（条件指定）
        parser_auto_playlist = subparsers.add_parser("auto-playlist", help="動画の再生リスト自動生成（条件指定）")
        parser_auto_playlist.add_argument("channel_id", help="チャンネルID")
        parser_auto_playlist.add_argument("keyword", help="キーワード")

        # 動画の平均評価・低評価率算出
        parser_rating = subparsers.add_parser("rating", help="動画の平均評価・低評価率算出")
        parser_rating.add_argument("video_id", help="動画ID")

        # コメントのいいね数ランキング取得
        parser_comment_like = subparsers.add_parser("comment-like", help="コメントのいいね数ランキング取得")
        parser_comment_like.add_argument("video_id", help="動画ID")

        # 動画の埋め込みコード自動生成
        parser_embed = subparsers.add_parser("embed", help="動画の埋め込みコード自動生成")
        parser_embed.add_argument("video_id", help="動画ID")

        # 動画・チャンネルのSNSシェア用URL生成
        parser_share = subparsers.add_parser("share", help="動画・チャンネルのSNSシェア用URL生成")
        parser_share.add_argument("type", choices=["video", "channel"], help="video or channel")
        parser_share.add_argument("id", help="ID")

        args = parser.parse_args()
        if args.command == "search":
            result = self.video_api.search_videos(args.query)
            for item in result.get("items", []):
                print(f"{item['snippet']['title']} ({item['id'].get('videoId', '')})")
        elif args.command == "channel":
            info = self.channel_api.get_channel_info(channel_id=args.channel_id)
            print(f"チャンネル名: {info['snippet']['title']}")
            print(f"登録者数: {info['statistics'].get('subscriberCount', 'N/A')}")
        elif args.command == "dates":
            if args.type == "video":
                info = self.video_api.get_video_info(args.id)
                print(f"登録日: {info['snippet']['publishedAt']}")
                print(f"最終更新日: {info['snippet'].get('updatedAt', 'N/A')}")
            elif args.type == "channel":
                info = self.channel_api.get_channel_info(channel_id=args.id)
                print(f"登録日: {info['snippet']['publishedAt']}")
                print(f"最終更新日: {info['snippet'].get('updatedAt', 'N/A')}")
        elif args.command == "auto-playlist":
            videos = self.video_api.get_channel_videos(args.channel_id)
            filtered = [v for v in videos.get("items", []) if args.keyword in v["snippet"]["title"]]
            print("自動生成プレイリスト:")
            for v in filtered:
                print(f"{v['snippet']['title']} ({v['id'].get('videoId', '')})")
        elif args.command == "rating":
            info = self.video_api.get_video_info(args.video_id)
            stats = info.get("statistics", {})
            like = int(stats.get("likeCount", 0))
            dislike = int(stats.get("dislikeCount", 0)) if "dislikeCount" in stats else 0
            total = like + dislike
            avg = like / total * 100 if total else 0
            print(f"高評価率: {avg:.2f}% (高評価: {like}, 低評価: {dislike})")
        elif args.command == "comment-like":
            comments = self.video_api.get_comments(args.video_id)
            ranked = sorted(comments, key=lambda x: x.get("likeCount", 0), reverse=True)
            print("コメントいいね数ランキング:")
            for c in ranked[:10]:
                print(f"{c['author']}: {c['text']} (いいね: {c['likeCount']})")
        elif args.command == "embed":
            print(f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{args.video_id}" frameborder="0" allowfullscreen></iframe>')
        elif args.command == "share":
            if args.type == "video":
                print(f"https://youtu.be/{args.id}")
            else:
                print(f"https://www.youtube.com/channel/{args.id}")
        else:
            parser.print_help()
