#!/usr/bin/env python3
"""
YouTubeManager - ダミー版
YouTubeチャンネル管理CLIツール（機能サンプル・ダミー実装）
"""

import sys
import os
import json
from datetime import datetime

# --- youtube.py2_APIラッパーのimportをfromではなくimportで統一 ---
import youtube_py2

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'youtube_py3_config.json')
SAVED_CHANNELS_PATH = os.path.join(os.path.dirname(__file__), 'saved_channels.json')

def load_saved_channels():
    if os.path.exists(SAVED_CHANNELS_PATH):
        with open(SAVED_CHANNELS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'channels': [], 'last_updated': ''}

def save_saved_channels(data):
    with open(SAVED_CHANNELS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_youtube():
    auth = get_youtube_auth()
    if not auth:
        return None
    return {
        'auth': auth,
        'channel': youtube_py2.YouTubeChannel(auth),
        'video': youtube_py2.YouTubeVideo(auth),
        'comment': youtube_py2.YouTubeComment(auth),
        'playlist': youtube_py2.YouTubePlaylist(auth)
    }

def get_youtube_auth():
    api_key = os.environ.get('YOUTUBE_API_KEY', '')
    if not api_key and os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            conf = json.load(f)
            api_key = conf.get('api_key', '')
    if not api_key:
        print('APIキーが設定されていません。API管理から設定してください。')
        return None
    return youtube_py2.YouTubeAuth(api_key=api_key)

def display_menu():
    print("\n=== YouTubeManager（ダミー） ===")
    print("1. チャンネル検索")
    print("2. チャンネルID管理")
    print("3. 最新動画コメント数取得")
    print("4. API管理")
    print("5. OAuth")
    print("6. 設定")
    print("7. 終了")
    print("=" * 25)

def get_menu_choice():
    while True:
        try:
            choice = input("選択してください (1-7): ").strip()
            if choice in [str(i) for i in range(1,8)]:
                return int(choice)
            print("1から7の数字を入力してください。")
        except KeyboardInterrupt:
            print("\n終了します。")
            sys.exit(0)

# --- 機能実装 ---
def channel_search():
    yt = get_youtube()
    if yt is None:
        input("\nEnterキーでメニューに戻る..."); return
    query = input("検索するチャンネル名を入力してください: ").strip()
    if not query:
        print("検索キーワードを入力してください。")
        return
    try:
        result = yt['channel'].get_channel_info(for_username=query)
        if not result or not result.get('items'):
            print("該当するチャンネルが見つかりませんでした。")
            input("\nEnterキーでメニューに戻る..."); return
        items = result['items']
        print(f"'{query}' の検索結果:")
        for idx, item in enumerate(items, 1):
            ch = item['snippet']
            print(f"{idx}. {ch['title']} (ID: {item['id']})")
        sel = input("\n保存したいチャンネル番号を入力（Enterでスキップ）: ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(items):
            idx = int(sel) - 1
            ch = items[idx]['snippet']
            channel_id = items[idx]['id']
            ch_data = items[idx]
            saved = load_saved_channels()
            saved['channels'].append({
                'channel_id': channel_id,
                'title': ch['title'],
                'description': ch.get('description', ''),
                'url': f"https://www.youtube.com/channel/{channel_id}",
                'thumbnail': ch['thumbnails']['default']['url'],
                'saved_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'save_reason': '検索結果から保存',
                'subscriber_count': ch_data.get('statistics', {}).get('subscriberCount', ''),
                'video_count': ch_data.get('statistics', {}).get('videoCount', ''),
                'view_count': ch_data.get('statistics', {}).get('viewCount', ''),
            })
            saved['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_saved_channels(saved)
            print(f"チャンネル '{ch['title']}' を保存しました。")
    except Exception as e:
        print(f"エラー: {e}")
    input("\nEnterキーでメニューに戻る...")

def channel_management():
    saved = load_saved_channels()
    channels = saved.get('channels', [])
    if not channels:
        print("\n=== チャンネルID管理 ===")
        print("保存されているチャンネルはありません")
        input("\nEnterキーでメニューに戻る...")
        return
    print("\n=== チャンネルID管理 ===")
    for idx, ch in enumerate(channels, 1):
        print(f"{idx}. {ch['title']} (ID: {ch['channel_id']}) 登録日: {ch['saved_date']}")
    print("\n1. チャンネル削除  2. 戻る")
    sel = input("操作を選択してください: ").strip()
    if sel == '1':
        del_idx = input("削除するチャンネル番号: ").strip()
        if del_idx.isdigit() and 1 <= int(del_idx) <= len(channels):
            removed = channels.pop(int(del_idx)-1)
            saved['channels'] = channels
            saved['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_saved_channels(saved)
            print(f"チャンネル '{removed['title']}' を削除しました。")
        else:
            print("無効な番号です。")
    input("\nEnterキーでメニューに戻る...")

def comment_count():
    yt = get_youtube()
    if yt is None:
        input("\nEnterキーでメニューに戻る..."); return
    saved = load_saved_channels()
    channels = saved.get('channels', [])
    if not channels:
        print("保存チャンネルがありません。チャンネル検索から追加してください。")
        input("\nEnterキーでメニューに戻る..."); return
    print("\n=== 最新動画コメント数取得 ===")
    for idx, ch in enumerate(channels, 1):
        print(f"{idx}. {ch['title']} (ID: {ch['channel_id']})")
    sel = input("対象チャンネル番号を選択: ").strip()
    if not sel.isdigit() or not (1 <= int(sel) <= len(channels)):
        print("無効な番号です。")
        input("\nEnterキーでメニューに戻る..."); return
    ch = channels[int(sel)-1]
    try:
        videos = yt['channel'].get_channel_info(channel_id=ch['channel_id'])
        items = videos.get('items', [])
        if not items:
            print("動画が見つかりませんでした。"); input("\nEnterキーでメニューに戻る..."); return
        uploads_playlist = items[0]['contentDetails']['relatedPlaylists']['uploads']
        playlist_items = yt['playlist'].get_playlist_items(uploads_playlist, max_results=1)
        video_id = playlist_items['items'][0]['contentDetails']['videoId']
        comments = yt['comment'].get_comments(video_id, exclude_owner=True, no_replies=True, max_results=100, owner_channel_id=ch['channel_id'])
        print(f"対象チャンネル: {ch['title']} (ID: {ch['channel_id']})")
        print(f"最新動画ID: {video_id}")
        print(f"コメント数（投稿主除外・返信なし）: {len(comments)}件")
    except Exception as e:
        print(f"エラー: {e}")
    input("\nEnterキーでメニューに戻る...")

def api_management():
    api_key = ''
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            conf = json.load(f)
            api_key = conf.get('api_key', '')
    print("\n=== API管理 ===")
    print(f"現在のAPIキー: {'未設定' if not api_key else api_key[:6] + '...' }")
    print("1. APIキーを設定  2. 接続テスト  3. 戻る")
    sel = input("操作を選択してください: ").strip()
    if sel == '1':
        new_key = input("新しいAPIキーを入力: ").strip()
        if new_key:
            conf = {'api_key': new_key}
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(conf, f, ensure_ascii=False, indent=2)
            print("APIキーを保存しました。")
        else:
            print("APIキーが空です。")
    elif sel == '2':
        yt = get_youtube()
        if yt is None:
            print("APIキーが未設定です。")
        else:
            try:
                yt['channel'].get_channel_info(channel_id='UC_x5XG1OV2P6uZZ5FSM9Ttw')
                print("API接続テスト: 成功")
            except Exception as e:
                print(f"API接続テスト: 失敗 ({e})")
    input("\nEnterキーでメニューに戻る...")

def oauth_management():
    print("\n=== OAuth ===")
    print(f"OAuth認証状態: 未実装（APIキーのみ対応）")
    print("1. 戻る")
    input("\nEnterキーでメニューに戻る...")

def settings_menu():
    print("\n=== 設定 ===")
    print("設定項目はありません")
    input("\nEnterキーでメニューに戻る...")

def main():
    print("YouTubeManagerを起動しました。")
    while True:
        display_menu()
        choice = get_menu_choice()
        if choice == 1:
            channel_search()
        elif choice == 2:
            channel_management()
        elif choice == 3:
            comment_count()
        elif choice == 4:
            api_management()
        elif choice == 5:
            oauth_management()
        elif choice == 6:
            settings_menu()
        elif choice == 7:
            print("YouTubeManagerを終了します。")
            break

if __name__ == "__main__":
    main()