from youtube_py2 import _bootstrap
_bootstrap._detect_debugger()
_bootstrap._internal_update()

import pandas
import json
from youtube_py2.license import require_device_cert

class YouTubeExport:
    """
    データ処理・エクスポート
    - DataFrame化
    - CSV/JSONエクスポート
    - 一時キャッシュ
    """
    def to_dataframe(self, data):
        require_device_cert()
        return pandas.DataFrame(data)

    def to_csv(self, data, file_path):
        require_device_cert()
        df = self.to_dataframe(data)
        df.to_csv(file_path, index=False, encoding="utf-8-sig")

    def to_json(self, data, file_path):
        require_device_cert()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def export_to_csv(self, data, file_path):
        require_device_cert()
        self.to_csv(data, file_path)
