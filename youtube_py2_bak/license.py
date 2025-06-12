from youtube_py2 import _bootstrap
_bootstrap._detect_debugger()
_bootstrap._internal_update()

import os

def require_device_cert(cert_path=None):
    """
    device_cert.pem（開発者専用機能用証明書）の存在を検証。
    優先順位:
      1. cert_path引数
      2. YOUTUBE_PY2_DEVICE_CERT環境変数
      3. DEVICE_CERT_PATH環境変数
      4. カレントディレクトリのdevice_cert.pem
      5. 証明書/device_cert.pem
    """
    candidates = []
    if cert_path:
        candidates.append(cert_path)
    env1 = os.environ.get("YOUTUBE_PY2_DEVICE_CERT")
    if env1:
        candidates.append(env1)
    env2 = os.environ.get("DEVICE_CERT_PATH")
    if env2:
        candidates.append(env2)
    candidates.append("device_cert.pem")
    candidates.append(os.path.join("証明書", "device_cert.pem"))
    for path in candidates:
        if path and os.path.exists(path):
            return path  # 証明書パスを返す（必要ならreturnを削除しpassに）
    raise Exception("開発者専用機能用証明書(device_cert.pem)が見つかりません。YOUTUBE_PY2_DEVICE_CERTやDEVICE_CERT_PATH環境変数、またはパス指定を確認してください。")
