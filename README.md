# youtube.py2

youtube.py3を廃止し、youtube.py2に以降しました。
※youtube.py3は機能しないようにしています※
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
