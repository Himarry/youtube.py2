import sys
import traceback

print("[TEST] import youtube_py2 ...")
try:
    import youtube_py2
except Exception as e:
    print(f"[FAIL] import youtube_py2: {e}")
    traceback.print_exc()
    sys.exit(1)

# ダミー認証情報
DUMMY_AUTH = object()
DUMMY_API_KEY = "dummy_api_key"
DUMMY_CLIENT_ID = "dummy_client_id"
DUMMY_CLIENT_SECRET = "dummy_client_secret"
DUMMY_REFRESH_TOKEN = "dummy_refresh_token"
DUMMY_TOKEN_FILE = "dummy_token.json"
DUMMY_LICENSE_KEY = "dummy_license"
DUMMY_LOG_FILE = "dummy.log"

success = True

def try_instance(name, func):
    global success
    try:
        func()
        print(f"[OK] {name} インスタンス生成成功")
    except Exception as e:
        print(f"[FAIL] {name} インスタンス生成失敗: {e}")
        traceback.print_exc()
        success = False

# APIクラスごとに必須引数を正しく渡す
try_instance("YouTubeAuth", lambda: youtube_py2.YouTubeAuth(DUMMY_API_KEY, DUMMY_CLIENT_ID, DUMMY_CLIENT_SECRET, DUMMY_REFRESH_TOKEN, DUMMY_TOKEN_FILE))
try_instance("YouTubeVideo", lambda: youtube_py2.YouTubeVideo(auth=DUMMY_AUTH))
try_instance("YouTubeChannel", lambda: youtube_py2.YouTubeChannel(auth=DUMMY_AUTH))
try_instance("YouTubeComment", lambda: youtube_py2.YouTubeComment(auth=DUMMY_AUTH))
try_instance("YouTubePlaylist", lambda: youtube_py2.YouTubePlaylist(auth=DUMMY_AUTH))
try_instance("YouTubeCaptions", lambda: youtube_py2.YouTubeCaptions(auth=DUMMY_AUTH))
try_instance("YouTubeAnalytics", lambda: youtube_py2.YouTubeAnalytics(auth=DUMMY_AUTH))
try_instance("YouTubeExport", lambda: youtube_py2.YouTubeExport())
try_instance("YouTubeAsync", lambda: youtube_py2.YouTubeAsync(auth=DUMMY_AUTH))
try_instance("YouTubeCLI", lambda: youtube_py2.YouTubeCLI(youtube_py2.YouTubeVideo(auth=DUMMY_AUTH), youtube_py2.YouTubeChannel(auth=DUMMY_AUTH), DUMMY_LICENSE_KEY))
try_instance("YouTubeLogger", lambda: youtube_py2.YouTubeLogger(DUMMY_LOG_FILE))
try_instance("YouTubeLive", lambda: youtube_py2.YouTubeLive(auth=DUMMY_AUTH))
try_instance("YouTubeMembership", lambda: youtube_py2.YouTubeMembership(auth=DUMMY_AUTH))
try_instance("YouTubePagination", lambda: youtube_py2.YouTubePagination())
try_instance("YouTubePubSub", lambda: youtube_py2.YouTubePubSub(auth=DUMMY_AUTH))
try_instance("YouTubeLocalization", lambda: youtube_py2.YouTubeLocalization(auth=DUMMY_AUTH))

if success:
    print("\n[RESULT] すべてのAPIクラスのインスタンス生成に成功しました")
    sys.exit(0)
else:
    print("\n[RESULT] 一部のAPIクラスのインスタンス生成に失敗しました")
    sys.exit(1)
