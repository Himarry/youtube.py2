from youtube_py2 import _bootstrap
_bootstrap._detect_debugger()
_bootstrap._internal_update()

import requests
import pandas
from youtube_py2.license import require_device_cert

class YouTubeAnalytics:
    """
    YouTube Analytics & Reporting API
    - get_analytics()
    - download_bulk_reports()
    """
    def __init__(self, auth):
        self.auth = auth
        self.base_url = "https://youtubeanalytics.googleapis.com/v2"

    def get_analytics(self, channel_id, metrics, start_date, end_date):
        url = f"{self.base_url}/reports"
        params = {
            "ids": f"channel=={channel_id}",
            "metrics": ",".join(metrics),
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": "day",
            "key": self.auth.get_api_key() if self.auth.api_key else None
        }
        headers = self.auth.get_headers()
        resp = requests.get(url, params={k: v for k, v in params.items() if v}, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(f"アナリティクス取得失敗: {resp.text}")

    def download_bulk_reports(self, channel_id, metrics, save_path):
        # Bulk Reports APIはOAuth2必須、ここではダミー実装
        data = self.get_analytics(channel_id, metrics, "2023-01-01", "2023-01-31")
        df = pandas.DataFrame(data.get("rows", []), columns=data.get("columnHeaders", []))
        df.to_csv(save_path, index=False, encoding="utf-8-sig")
        return save_path

    def get_analytics_report(self, channel_id, metrics, start_date, end_date):
        require_device_cert()
        # 入力バリデーション
        if not isinstance(channel_id, str) or not channel_id:
            raise ValueError("channel_idは非空の文字列で指定してください")
        if not isinstance(metrics, (list, tuple)) or not metrics or not all(isinstance(m, str) for m in metrics):
            raise ValueError("metricsは1つ以上の文字列からなるリストまたはタプルで指定してください")
        if not isinstance(start_date, str) or not isinstance(end_date, str):
            raise ValueError("start_date, end_dateはYYYY-MM-DD形式の文字列で指定してください")
        # 日付フォーマット簡易チェック
        import re
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(date_pattern, start_date) or not re.match(date_pattern, end_date):
            raise ValueError("日付はYYYY-MM-DD形式で指定してください")
        # データ取得
        try:
            data = self.get_analytics(channel_id, metrics, start_date, end_date)
        except Exception as e:
            raise RuntimeError(f"アナリティクスデータ取得失敗: {e}")
        # データ整形
        rows = data.get("rows", [])
        columns = data.get("columnHeaders", [])
        if not rows or not columns:
            raise RuntimeError("アナリティクスデータが取得できませんでした")
        import pandas as pd
        df = pd.DataFrame(rows, columns=columns)
        return df
