import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from collections import Counter

class YouTubeCommentCounter:
    def __init__(self):
        """
        YouTube Comment Counterの初期化
        環境変数からAPIキーを取得
        """
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("環境変数 YOUTUBE_API_KEY が設定されていません")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        
        # チャンネルIDを設定
        self.channel_id = "UCYrHEsf7bhiFJssY5btS7Zg"
        self.channel_author_name = None
    
    def get_latest_video(self):
        """
        指定されたチャンネルの最新動画を取得
        """
        try:
            channel_response = self.youtube.channels().list(
                part='contentDetails,snippet',
                id=self.channel_id
            ).execute()
            
            if not channel_response['items']:
                print(f"チャンネルID {self.channel_id} が見つかりません")
                return None
            
            channel_info = channel_response['items'][0]
            channel_name = channel_info['snippet']['title']
            self.channel_author_name = channel_name
            uploads_playlist_id = channel_info['contentDetails']['relatedPlaylists']['uploads']
            
            print(f"チャンネル名: {channel_name}")
            
            playlist_response = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=1
            ).execute()
            
            if playlist_response['items']:
                latest_video = playlist_response['items'][0]
                video_id = latest_video['snippet']['resourceId']['videoId']
                video_title = latest_video['snippet']['title']
                published_at = latest_video['snippet']['publishedAt']
                
                print(f"最新動画: {video_title}")
                return video_id, video_title, published_at
            else:
                print("動画が見つかりませんでした")
                return None
            
        except HttpError as e:
            print(f"チャンネル情報取得エラー: {e}")
            return None
    
    def count_comments_with_reply_details(self, video_id):
        """
        コメントと返信者を詳細に分析
        """
        comments_with_replies = 0
        comments_without_replies = 0
        author_comments_with_replies = 0
        author_comments_without_replies = 0
        all_reply_authors = []
        
        try:
            print(f"コメントと返信者をカウント中...")
            next_page_token = None
            total_processed = 0
            total_replies_found = 0
            
            while True:
                # コメントスレッドを取得（repliesを含める）
                comment_response = self.youtube.commentThreads().list(
                    part='snippet,replies',
                    videoId=video_id,
                    maxResults=100,
                    pageToken=next_page_token
                ).execute()
                
                for item in comment_response['items']:
                    top_comment = item['snippet']['topLevelComment']['snippet']
                    author_name = top_comment['authorDisplayName']
                    author_channel_id = top_comment.get('authorChannelId', {}).get('value', '')
                    reply_count = item['snippet']['totalReplyCount']
                    
                    # 投稿者のコメントかチェック
                    is_author_comment = (author_channel_id == self.channel_id or 
                                       author_name == self.channel_author_name)
                    
                    # 返信がある場合の処理
                    if reply_count > 0:
                        print(f"    返信付きコメント発見: {reply_count} 返信")
                        
                        # 返信を処理
                        if 'replies' in item and 'comments' in item['replies']:
                            for reply in item['replies']['comments']:
                                reply_snippet = reply['snippet']
                                reply_author_channel_id = reply_snippet.get('authorChannelId', {}).get('value', '')
                                reply_author_name = reply_snippet['authorDisplayName']
                                
                                # 返信者のIDを作成
                                if reply_author_channel_id:
                                    reply_id = f"@{reply_author_channel_id}"
                                else:
                                    # 表示名から安全なIDを作成
                                    clean_name = ''.join(c for c in reply_author_name if c.isalnum() or c in ['_', '-'])
                                    reply_id = f"@{clean_name}" if clean_name else f"@User{len(all_reply_authors)}"
                                
                                all_reply_authors.append(reply_id)
                                total_replies_found += 1
                                
                                print(f"      返信者: {reply_id}")
                        
                        # 返信ありコメントとしてカウント
                        if is_author_comment:
                            author_comments_with_replies += 1
                        else:
                            comments_with_replies += 1
                    else:
                        # 返信なしコメント
                        if is_author_comment:
                            author_comments_without_replies += 1
                        else:
                            comments_without_replies += 1
                    
                    total_processed += 1
                
                print(f"  処理済み: {total_processed} コメント, 返信: {total_replies_found}")
                
                next_page_token = comment_response.get('nextPageToken')
                if not next_page_token:
                    break
            
            print(f"カウント完了: 総 {total_processed} コメント, 総 {total_replies_found} 返信")
            print(f"返信者数: {len(set(all_reply_authors))} 人")
            
            # 返信者の統計を作成
            reply_author_counts = Counter(all_reply_authors)
            
            # デバッグ情報
            print(f"返信者データ: {len(reply_author_counts)} 人の返信者")
            if reply_author_counts:
                print("返信者サンプル:")
                for author, count in list(reply_author_counts.items())[:3]:
                    print(f"  {author}: {count} 返信")
            
            return {
                'total_comments': total_processed,
                'viewer_comments_with_replies': comments_with_replies,
                'viewer_comments_without_replies': comments_without_replies,
                'author_comments_with_replies': author_comments_with_replies,
                'author_comments_without_replies': author_comments_without_replies,
                'reply_authors': dict(reply_author_counts),
                'total_replies': total_replies_found,
                'unique_repliers': len(reply_author_counts)
            }
                    
        except HttpError as e:
            print(f"コメント取得エラー: {e}")
            return {
                'total_comments': 0,
                'viewer_comments_with_replies': 0,
                'viewer_comments_without_replies': 0,
                'author_comments_with_replies': 0,
                'author_comments_without_replies': 0,
                'reply_authors': {},
                'total_replies': 0,
                'unique_repliers': 0
            }
    
    def analyze_latest_video(self):
        """
        最新動画のコメント数分析を実行
        """
        print("="*70)
        print("YouTube コメント数カウンター（返信者ID付き）")
        print("="*70)
        
        # 最新動画を取得
        latest_video_info = self.get_latest_video()
        if not latest_video_info:
            return None
        
        video_id, video_title, published_at = latest_video_info
        
        # 動画の統計情報を取得
        try:
            video_response = self.youtube.videos().list(
                part='statistics',
                id=video_id
            ).execute()
            
            video_stats = video_response['items'][0]['statistics'] if video_response['items'] else {}
            api_comment_count = int(video_stats.get('commentCount', 0))
            
        except HttpError as e:
            print(f"動画統計取得エラー: {e}")
            api_comment_count = 0
        
        # コメント数をカウント
        comment_stats = self.count_comments_with_reply_details(video_id)
        
        if comment_stats['total_comments'] == 0:
            print("コメントが見つかりませんでした")
            return None
        
        # 計算
        total_viewer_comments = comment_stats['viewer_comments_with_replies'] + comment_stats['viewer_comments_without_replies']
        total_author_comments = comment_stats['author_comments_with_replies'] + comment_stats['author_comments_without_replies']
        total_analyzed = comment_stats['total_comments']
        
        # 結果を表示
        print("\n" + "="*70)
        print("分析結果")
        print("="*70)
        print(f"動画タイトル: {video_title}")
        print(f"公開日: {published_at}")
        print(f"動画ID: {video_id}")
        print(f"チャンネル投稿者: {self.channel_author_name}")
        print("-" * 70)
        print(f"API取得コメント総数: {api_comment_count:,}")
        print(f"実際に分析したコメント数: {total_analyzed:,}")
        print(f"総返信数: {comment_stats['total_replies']:,}")
        print(f"ユニーク返信者数: {comment_stats['unique_repliers']:,}")
        print("-" * 70)
        
        print("【視聴者コメント】")
        print(f"  返信ありコメント: {comment_stats['viewer_comments_with_replies']:,}")
        print(f"  返信なしコメント: {comment_stats['viewer_comments_without_replies']:,}")
        print(f"  視聴者コメント合計: {total_viewer_comments:,}")
        
        if total_viewer_comments > 0:
            viewer_reply_rate = (comment_stats['viewer_comments_with_replies'] / total_viewer_comments) * 100
            print(f"  視聴者コメント返信率: {viewer_reply_rate:.2f}%")
        
        print("-" * 70)
        print("【投稿者コメント】")
        print(f"  返信ありコメント: {comment_stats['author_comments_with_replies']:,}")
        print(f"  返信なしコメント: {comment_stats['author_comments_without_replies']:,}")
        print(f"  投稿者コメント合計: {total_author_comments:,}")
        
        if total_author_comments > 0:
            author_reply_rate = (comment_stats['author_comments_with_replies'] / total_author_comments) * 100
            print(f"  投稿者コメント返信率: {author_reply_rate:.2f}%")
        
        print("-" * 70)
        print("【返信者ランキング TOP 10】")
        
        if comment_stats['reply_authors'] and len(comment_stats['reply_authors']) > 0:
            sorted_repliers = sorted(comment_stats['reply_authors'].items(), 
                                   key=lambda x: x[1], reverse=True)[:10]
            
            for i, (author_id, count) in enumerate(sorted_repliers, 1):
                # 投稿者かどうかをマーク
                is_channel_owner = self.channel_id in author_id
                owner_mark = " (投稿者)" if is_channel_owner else ""
                print(f"  {i:2d}. {author_id}{owner_mark}: {count:,} 返信")
        else:
            print("  返信が見つかりませんでした")
            print(f"  デバッグ: reply_authors辞書のサイズ = {len(comment_stats['reply_authors'])}")
        
        print("-" * 70)
        print("【全体統計】")
        total_reply_rate = ((comment_stats['viewer_comments_with_replies'] + comment_stats['author_comments_with_replies']) / total_analyzed * 100) if total_analyzed > 0 else 0
        print(f"全コメント返信率: {total_reply_rate:.2f}%")
        
        if total_analyzed > 0:
            author_comment_ratio = (total_author_comments / total_analyzed) * 100
            print(f"投稿者コメント比率: {author_comment_ratio:.2f}%")
            
            if comment_stats['total_replies'] > 0:
                avg_replies_per_comment = comment_stats['total_replies'] / total_analyzed
                print(f"コメントあたり平均返信数: {avg_replies_per_comment:.2f}")
        
        print("="*70)
        print(f"分析完了時刻: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        
        return comment_stats

def main():
    try:
        counter = YouTubeCommentCounter()
        result = counter.analyze_latest_video()
        
        if result and result['total_replies'] > 0:
            print(f"\n✅ カウント完了！")
            print(f"総返信数: {result['total_replies']:,}")
            print(f"ユニーク返信者数: {result['unique_repliers']:,}")
            
            if result['reply_authors']:
                top_replier = max(result['reply_authors'].items(), key=lambda x: x[1])
                print(f"最も活発な返信者: {top_replier[0]} ({top_replier[1]} 返信)")
        else:
            print("❌ 返信データを取得できませんでした")
            
    except ValueError as e:
        print(f"❌ エラー: {e}")
    except Exception as e:
        print(f"❌ 予期しないエラーが発生しました: {e}")

if __name__ == "__main__":
    main()