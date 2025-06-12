#!/usr/bin/env python
"""
YouTube.py3 リリース管理スクリプト (完全バイナリ化対応)
"""

import os
import sys
import subprocess
import re
import shutil
from pathlib import Path
import argparse
import concurrent.futures

# --- 追加: パッケージ名を引数で指定できるようにする ---
def get_package_name():
    parser = argparse.ArgumentParser(description="リリース対象パッケージ名")
    parser.add_argument('--package', type=str, default='youtube_py2', help='パッケージ名 (例: youtube_py2)')
    args, unknown = parser.parse_known_args()
    return args.package

PACKAGE_NAME = get_package_name()


def get_version_type_interactive():
    """インタラクティブにバージョンタイプを選択"""
    print("\n📋 バージョンアップタイプを選択してください:")
    print("=" * 40)
    print("1. patch  - パッチバージョン (例: 1.3.4 → 1.3.5)")
    print("2. minor  - マイナーバージョン (例: 1.3.4 → 1.4.0)")
    print("3. major  - メジャーバージョン (例: 1.3.4 → 2.0.0)")
    print("=" * 40)
    
    while True:
        choice = input("選択 (1-3) [デフォルト: 1]: ").strip()
        
        if choice == "" or choice == "1":
            return "patch"
        elif choice == "2":
            return "minor"
        elif choice == "3":
            return "major"
        else:
            print("❌ 無効な選択です。1、2、3のいずれかを入力してください。")


def get_upload_target_interactive():
    """インタラクティブにアップロード先を選択"""
    print("\n🚀 アップロード先を選択してください:")
    print("=" * 40)
    print("1. TestPyPI - テスト環境 (推奨)")
    print("2. PyPI     - 本番環境 (注意: 元に戻せません)")
    print("3. ビルドのみ - アップロードしない")
    print("=" * 40)
    
    while True:
        choice = input("選択 (1-3) [デフォルト: 1]: ").strip()
        
        if choice == "" or choice == "1":
            return "testpypi"
        elif choice == "2":
            return "pypi"
        elif choice == "3":
            return "build_only"
        else:
            print("❌ 無効な選択です。1、2、3のいずれかを入力してください。")


def show_current_version():
    """現在のバージョンを表示（youtube_py2_bak/__init__.py対応）"""
    init_file = Path('youtube_py2_bak') / '__init__.py'
    if not init_file.exists():
        print(f"⚠️ {init_file} が見つかりません")
        return "不明"
    try:
        content = init_file.read_text(encoding='utf-8')
        version_match = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', content)
        if version_match:
            current_version = version_match.group(1)
            print(f"📌 現在のバージョン: {current_version}")
            return current_version
    except Exception as e:
        print(f"⚠️ バージョン取得エラー: {e}")
    print("⚠️ 現在のバージョンを取得できませんでした")
    return "不明"


def preview_new_version(current_version, version_type):
    """新しいバージョンをプレビュー"""
    try:
        major, minor, patch = map(int, current_version.split('.'))
        
        if version_type == 'major':
            new_version = f"{major + 1}.0.0"
        elif version_type == 'minor':
            new_version = f"{major}.{minor + 1}.0"
        else:  # patch
            new_version = f"{major}.{minor}.{patch + 1}"
        
        print(f"🔄 変更予定: {current_version} → {new_version}")
        return new_version
    except:
        print("⚠️ バージョンプレビューに失敗しました")
        return "不明"


def confirm_release(version_type, upload_target, current_version, new_version):
    """リリース確認"""
    print("\n" + "=" * 50)
    print("🔍 リリース設定確認")
    print("=" * 50)
    print(f"📦 パッケージ: youtube.py3")
    print(f"📌 現在のバージョン: {current_version}")
    print(f"🆕 新しいバージョン: {new_version}")
    print(f"🔧 バージョンタイプ: {version_type}")
    
    if upload_target == "testpypi":
        print(f"🚀 アップロード先: TestPyPI (テスト環境)")
    elif upload_target == "pypi":
        print(f"🚀 アップロード先: PyPI (本番環境) ⚠️")
    else:
        print(f"🚀 アップロード先: なし (ビルドのみ)")
    
    print(f"⚙️ ビルドモード: 完全バイナリ化 (Cython)")
    print("=" * 50)
    
    if upload_target == "pypi":
        print("⚠️  警告: 本番PyPIへのアップロードは元に戻すことができません！")
    
    while True:
        confirm = input("\n続行しますか？ (y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            return True
        elif confirm in ['n', 'no', '']:
            return False
        else:
            print("❌ 'y' または 'n' を入力してください。")


# 既存の関数はそのまま維持...
def bump_version(version_type='patch'):
    """バージョンを自動的に更新（youtube_py2_bak/__init__.py対応）"""
    init_file = Path('youtube_py2_bak') / '__init__.py'
    if not init_file.exists():
        print(f"警告: {init_file} が見つかりません。新規作成します。")
        current_version = "0.0.0"
        content = f'__version__ = "{current_version}"\n'
        try:
            init_file.write_text(content, encoding='utf-8')
        except Exception as e:
            print(f"エラー: {init_file} の新規作成に失敗しました: {e}")
            return None
    else:
        try:
            content = init_file.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                content = init_file.read_text(encoding='cp932')
            except UnicodeDecodeError:
                print(f"エラー: {init_file} の文字エンコーディングを読み取れません")
                return None
    version_match = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', content)
    if not version_match:
        print("バージョンが見つかりません。0.0.0から開始します。")
        current_version = "0.0.0"
    else:
        current_version = version_match.group(1)
    try:
        major, minor, patch = map(int, current_version.split('.'))
    except ValueError:
        print(f"エラー: 無効なバージョン形式: {current_version}")
        return None
    if version_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif version_type == 'minor':
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    new_version = f"{major}.{minor}.{patch}"
    new_content = re.sub(
        r'__version__\s*=\s*[\'"][^\'"]+[\'"]',
        f'__version__ = "{new_version}"',
        content
    )
    if not re.search(r'__version__\s*=\s*[\'"]', new_content):
        new_content += f'__version__ = "{new_version}"\n'
    try:
        init_file.write_text(new_content, encoding='utf-8')
    except Exception as e:
        print(f"エラー: ファイル書き込みに失敗しました: {e}")
        return None
    pyproject_file = Path('pyproject.toml')
    if pyproject_file.exists():
        try:
            toml_content = pyproject_file.read_text(encoding='utf-8')
            new_toml_content = re.sub(
                r'(version\s*=\s*[\'"])[^\'"]+([\'"])',
                rf'\g<1>{new_version}\g<2>',
                toml_content
            )
            pyproject_file.write_text(new_toml_content, encoding='utf-8')
            print(f"pyproject.toml のバージョンも更新しました")
        except Exception as e:
            print(f"警告: pyproject.toml の更新に失敗: {e}")
    print(f"バージョンを {current_version} → {new_version} に更新しました")
    return new_version


def run_command_safely(command, description="", cwd=None):
    """安全にコマンドを実行（cwd指定対応、常に詳細出力）"""
    if description:
        print(f"実行中: {description}")
    print(f"コマンド: {command}")
    try:
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONUTF8'] = '1'
        env['SETUPTOOLS_USE_DISTUTILS'] = 'stdlib'
        env['CYTHON_FORCE_REGEN'] = '1'
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env,
            cwd=cwd
        )
        if result.stdout.strip():
            print("[stdout]", result.stdout)
        if result.stderr.strip():
            print("[stderr]", result.stderr)
        if result.returncode == 0:
            return True
        else:
            print(f"コマンド失敗 (終了コード: {result.returncode})")
            return False
    except Exception as e:
        print(f"コマンド実行エラー: {e}")
        return False


def run_command_with_fallback(commands, descriptions=None, cwd=None):
    """複数のコマンドを順番に試行（cwd指定対応）"""
    if descriptions is None:
        descriptions = [""] * len(commands)
    for i, (command, desc) in enumerate(zip(commands, descriptions)):
        print(f"\n試行 {i+1}/{len(commands)}: {desc or command}")
        if run_command_safely(command, desc, cwd=cwd):
            return True
    return False


def clean_build_artifacts():
    """ビルド成果物をクリーンアップ（バイナリビルド対応）"""
    print("2. ビルド成果物をクリーンアップ中...")
    # src/配下やsrc/youtube_py2/のバイナリは絶対に消さない
    patterns = [
        'build',
        'dist',
        '*.egg-info',
        '.eggs',
        '**/*.c',
        '**/*.pyx',
        '**/*.html',
        f'{PACKAGE_NAME}/*.c',
        f'{PACKAGE_NAME}/*.pyx',
        # 'src/', 'src/youtube_py2/', 'src/youtube_py2/*.pyd', 'src/youtube_py2/*.so' などは絶対に含めない
    ]
    for pattern in patterns:
        for path in Path('.').glob(pattern):
            # src/配下は絶対に消さない
            if str(path).startswith('src'):
                continue
            if path.is_dir():
                try:
                    shutil.rmtree(path)
                    print(f"削除: {path}")
                except Exception as e:
                    print(f"警告: {path} の削除に失敗: {e}")
            elif path.is_file():
                try:
                    path.unlink()
                    print(f"削除: {path}")
                except Exception as e:
                    print(f"警告: {path} の削除に失敗: {e}")


def install_dependencies():
    """必要な依存関係をインストール（バイナリビルド対応）"""
    print("3. 必要なパッケージを確認・インストール中...")
    
    install_commands = [
        "pip install --upgrade build twine wheel setuptools cython",
        "pip install build twine cython wheel",
        "pip install --upgrade setuptools wheel cython"
    ]
    
    descriptions = [
        "すべてのビルドツール（Cython含む）を最新版にアップグレード",
        "基本的なビルドツール（Cython含む）をインストール",
        "setuptools、wheel、Cython のみアップグレード"
    ]
    
    if run_command_with_fallback(install_commands, descriptions):
        print("✅ 依存関係のインストール完了")
        return True
    else:
        print("⚠️ 依存関係のインストールに問題がありましたが、処理を続行します")
        return False


def build_binary_package():
    """完全バイナリ化パッケージをビルド（Nuitkaのみ）"""
    print("4. 完全バイナリ化パッケージをビルド中...")
    # .pyファイルをyoutube_py2_bak/から探す
    nuitka_targets = [str(f) for f in Path('youtube_py2_bak').glob('*.py') if f.name != '__init__.py']
    if not nuitka_targets:
        print("❌ Nuitkaビルド対象となる.pyファイルが1つも見つかりません。最低1つ必要です。")
        print("💡 youtube_py2_bak/ に.pyファイルを配置してください。")
        return False
    else:
        project_root = str(Path(__file__).parent.resolve())
        def build_one(pyfile):
            print(f"--- Nuitkaビルド開始: {pyfile} ---")
            cmd = f"python -m nuitka --module {pyfile} --output-dir=src/youtube_py2 --remove-output --nofollow-imports --plugin-enable=numpy"
            ok = run_command_safely(cmd, f"Nuitkaで暗号化バイナリ(.pyd/.so)をsrc/youtube_py2に生成: {pyfile}", cwd=project_root)
            if ok:
                print(f"--- Nuitkaビルド完了: {pyfile} ---")
            else:
                print(f"⚠️ Nuitkaビルド失敗: {pyfile}")
            return ok
        # 並列ビルド
        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            results = list(executor.map(build_one, nuitka_targets))
        if not all(results):
            print("⚠️ 一部のNuitkaビルドに失敗しました")
    # ビルド後のバイナリ一覧を表示
    print("\n[ビルド直後のsrc/youtube_py2/バイナリ一覧]")
    bin_files = list(Path('src/youtube_py2').glob('*.pyd')) + list(Path('src/youtube_py2').glob('*.so'))
    if not bin_files:
        print("⚠️ src/youtube_py2/にバイナリが1つもありません")
    else:
        for f in bin_files:
            print(f"  - {f.name}")
        if len(bin_files) != len(nuitka_targets):
            print(f"⚠️ Nuitkaでバイナリ化された数({len(bin_files)})と.pyファイル数({len(nuitka_targets)})が一致しません")
    # --- バイナリハッシュ自動生成・保存 ---
    import hashlib
    import json
    import base64
    import time
    # --- 署名用秘密鍵のパス（PEM形式/RSA2048推奨）---
    SIGN_KEY_PATH = Path('証明書/device_key.pem')
    from cryptography.hazmat.primitives import hashes as c_hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.backends import default_backend

    hashes = {}
    for f in bin_files:
        with open(f, 'rb') as fp:
            data = fp.read()
            sha256 = hashlib.sha256(data).hexdigest()
            sha512 = hashlib.sha512(data).hexdigest()
            blake2b = hashlib.blake2b(data).hexdigest()
            size = len(data)
            mtime = int(f.stat().st_mtime)
            hashes[f.name] = {
                'sha256': sha256,
                'sha512': sha512,
                'blake2b': blake2b,
                'size': size,
                'mtime': mtime
            }
    # --- 署名生成 ---
    # 署名対象はハッシュ部のみ
    hash_bytes = json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode('utf-8')
    if SIGN_KEY_PATH.exists():
        with open(SIGN_KEY_PATH, 'rb') as kf:
            private_key = serialization.load_pem_private_key(kf.read(), password=None, backend=default_backend())
        signature = private_key.sign(
            hash_bytes,
            padding.PKCS1v15(),
            c_hashes.SHA256()
        )
        signature_b64 = base64.b64encode(signature).decode('ascii')
    else:
        signature_b64 = None
    out = {
        'hashes': hashes,
        'signature': signature_b64,
        'signed_at': int(time.time())
    }
    hash_json_path = Path('src/youtube_py2') / 'binary_hashes.json'
    with open(hash_json_path, 'w', encoding='utf-8') as fp:
        json.dump(out, fp, ensure_ascii=False, indent=2)
    print(f"\n🔒 バイナリ多重ハッシュ＋署名を {hash_json_path} に保存しました ({len(hashes)} 件)")
    # --- Wheelパッケージビルド ---
    build_commands = [
        "python -m build --wheel",
        "python -m build --wheel --no-isolation",
        "python setup.py bdist_wheel"
    ]
    descriptions = [
        "標準のWheelビルド方法（バイナリ含む）",
        "分離環境を使わないWheelビルド",
        "従来のsetup.pyを使用したWheelビルド"
    ]
    # --- binary_hashes.jsonの存在確認・内容表示 ---
    hashes_path = Path('src/youtube_py2/binary_hashes.json')
    if hashes_path.exists():
        print(f"\n[バイナリハッシュファイル検出: {hashes_path}]")
        try:
            import json
            hashes = json.loads(hashes_path.read_text(encoding='utf-8'))
            for k, v in hashes.items():
                print(f"  {k}: {v}")
        except Exception as e:
            print(f"⚠️ binary_hashes.jsonの読み込み失敗: {e}")
    else:
        print("⚠️ binary_hashes.jsonが見つかりません。バイナリ改ざん検知が無効化されます")
    print("\n🔄 Wheelパッケージをビルド中...")
    if run_command_with_fallback(build_commands, descriptions, cwd=None):
        print("✅ バイナリWheelビルド完了")
        return True
    else:
        print("❌ すべてのバイナリWheelビルド方法が失敗しました")
        print("\n💡 解決策:")
        print("   1. Nuitkaがインストールされているか確認:")
        print("      pip install nuitka")
        print("   2. C++コンパイラがインストールされているか確認:")
        print("      - Windows: Visual Studio Build Tools")
        print("      - Mac: Xcode Command Line Tools")
        print("      - Linux: gcc, g++")
        print("   3. 仮想環境を使用してください:")
        print("      python -m venv venv")
        print("      venv\\Scripts\\activate")
        print("      pip install build twine wheel nuitka")
        return False


def verify_binary_build():
    """バイナリビルド結果を確認（dist/をルート直下に修正）"""
    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("❌ distフォルダが存在しません")
        return False
    wheel_files = list(dist_dir.glob('*.whl'))
    if not wheel_files:
        print("❌ distフォルダにWheelファイルが見つかりません")
        return False
    print("\n📦 作成されたバイナリWheelファイル:")
    total_size = 0
    binary_detected = False
    for file in wheel_files:
        size_mb = file.stat().st_size / 1024 / 1024
        total_size += size_mb
        filename = file.name
        if any(arch in filename for arch in ['win_amd64', 'linux_x86_64', 'macosx', 'cp3']):
            binary_detected = True
            status = "[バイナリ含む]"
        else:
            status = "[純粋Python]"
        print(f"  - {filename} ({size_mb:.2f} MB) {status}")
    binary_files = list(Path('.').rglob('*.pyd')) + list(Path('.').rglob('*.so'))
    if binary_files:
        print(f"\n🔍 生成されたバイナリファイル:")
        for binary_file in binary_files:
            size_kb = binary_file.stat().st_size / 1024
            print(f"  - {binary_file} ({size_kb:.1f} KB)")
        binary_detected = True
    source_files = list(dist_dir.glob('*.tar.gz'))
    if source_files:
        print("\n🗑️ ソース配布物を削除中（バイナリのみ保持）...")
        for file in source_files:
            try:
                file.unlink()
                print(f"削除: {file.name}")
            except Exception as e:
                print(f"警告: {file.name} の削除に失敗: {e}")
    if binary_detected:
        print(f"\n✅ バイナリ化検証: 成功")
        print(f"Wheel総サイズ: {total_size:.2f} MB")
    else:
        print(f"\n⚠️ バイナリ化検証: バイナリファイルが検出されませんでした")
        print(f"setup.pyのCython設定を確認してください")
    return True


def upload_to_testpypi():
    """TestPyPIにアップロード（cwdをルートに戻す）"""
    commands = [
        "python -m twine upload --repository testpypi dist/*.whl --disable-progress-bar",
        "python -m twine upload --repository testpypi dist/*.whl --verbose --disable-progress-bar",
        "twine upload --repository testpypi dist/*.whl"
    ]
    descriptions = [
        "TestPyPIにバイナリWheelをアップロード（プログレスバー無効）",
        "TestPyPIにバイナリWheelをアップロード（詳細ログ付き）",
        "TestPyPIにバイナリWheelをアップロード（直接twineコマンド）"
    ]
    return run_command_with_fallback(commands, descriptions, cwd=None)


def upload_to_pypi():
    """PyPIにアップロード（cwdをルートに戻す）"""
    commands = [
        "python -m twine upload dist/*.whl --disable-progress-bar",
        "python -m twine upload dist/*.whl --verbose --disable-progress-bar",
        "twine upload dist/*.whl"
    ]
    descriptions = [
        "PyPIにバイナリWheelをアップロード（プログレスバー無効）",
        "PyPIにバイナリWheelをアップロード（詳細ログ付き）",
        "PyPIにバイナリWheelをアップロード（直接twineコマンド）"
    ]
    return run_command_with_fallback(commands, descriptions, cwd=None)


def copy_binaries_to_src():
    """バイナリ(.pyd/.so)をsrc/youtube_py2/配下に自動コピー"""
    import glob
    import shutil
    src_dir = Path('src') / 'youtube_py2'
    src_dir.mkdir(parents=True, exist_ok=True)
    # youtube_py2_bak/配下の全pyd/soをコピー
    for ext in ('.pyd', '.so'):
        for file in Path('youtube_py2_bak').glob(f'*{ext}'):
            dest = src_dir / file.name
            shutil.copy2(file, dest)
            print(f"コピー: {file} → {dest}")


def sync_py_to_src():
    """__init__.py, _bootstrap.py だけ src/youtube_py2/ にコピー"""
    src_dir = Path('src') / 'youtube_py2'
    src_dir.mkdir(parents=True, exist_ok=True)
    for fname in ["__init__.py", "_bootstrap.py"]:
        src = Path('youtube_py2_bak') / fname
        if src.exists():
            dest = src_dir / fname
            shutil.copy2(src, dest)
            print(f"コピー: {src} → {dest}")


def release(version_type='patch', upload_target='testpypi'):
    """完全バイナリ化リリースプロセス"""
    print(f"=== {PACKAGE_NAME} 完全バイナリ化リリースプロセス ===")
    print(f"バージョンタイプ: {version_type}")
    print(f"アップロード先: {upload_target}")
    print(f"ビルドモード: 完全バイナリ化")
    print("=" * 50)
    # 0. 必須.pyファイルをsrc/youtube_py2/にコピー
    sync_py_to_src()
    # 1. バージョン更新
    print("1. バージョン更新中...")
    new_version = bump_version(version_type)
    if not new_version:
        print("❌ バージョン更新に失敗しました")
        return False
    
    # 2. クリーンアップ
    clean_build_artifacts()
    
    # 3. 依存関係インストール
    install_dependencies()
    
    # 4. バイナリビルド
    if not build_binary_package():
        return False
    # 5. バイナリビルド結果確認
    print("\n[copy_binaries_to_src直前のsrc/youtube_py2/バイナリ一覧]")
    bin_files = list(Path('src/youtube_py2').glob('*.pyd')) + list(Path('src/youtube_py2').glob('*.so'))
    for f in bin_files:
        print(f"  - {f.name}")
    if not verify_binary_build():
        return False
    # 追加: src/配下にバイナリコピー
    copy_binaries_to_src()
    print("\n[copy_binaries_to_src直後のsrc/youtube_py2/バイナリ一覧]")
    bin_files = list(Path('src/youtube_py2').glob('*.pyd')) + list(Path('src/youtube_py2').glob('*.so'))
    for f in bin_files:
        print(f"  - {f.name}")
    # 6. アップロード
    if upload_target == "testpypi":
        print("\n5. TestPyPIにバイナリパッケージをアップロード中...")
        if upload_to_testpypi():
            print(f"✅ バイナリ版 v{new_version} をTestPyPIにアップロードしました")
            print(f"TestPyPI: https://test.pypi.org/project/{PACKAGE_NAME.replace('_', '-')}/{new_version}/")
            print(f"テストインストール: pip install --index-url https://test.pypi.org/simple/ {PACKAGE_NAME.replace('_', '-')}=={new_version}")
            print(f"🔒 このバージョンは完全にバイナリ化されています（ソースコード保護済み）")
            return True
        else:
            print("❌ TestPyPIへのアップロードに失敗しました")
            return False
    elif upload_target == "pypi":
        print("\n5. 本番PyPIにバイナリパッケージをアップロード中...")
        if upload_to_pypi():
            print(f"🎉 バイナリ版 v{new_version} を本番PyPIにアップロードしました")
            print(f"PyPI: https://pypi.org/project/{PACKAGE_NAME.replace('_', '-')}/{new_version}/")
            print(f"インストール: pip install {PACKAGE_NAME.replace('_', '-')}=={new_version}")
            print(f"🔒 完全バイナリ化によりソースコードが保護されています")
            return True
        else:
            print("❌ 本番PyPIへのアップロードに失敗しました")
            return False
    else:  # build_only
        print("\n5. ビルドのみ完了")
        print(f"✅ バイナリ版 v{new_version} のビルドが完了しました")
        print(f"🔒 完全バイナリ化によりソースコードが保護されています")
        print("手動でアップロードする場合:")
        print(f"  TestPyPI: twine upload --repository testpypi dist/*.whl")
        print(f"  PyPI: twine upload dist/*.whl")
        return True

    # --- バイナリビルド・パッケージ化 ---
    if not build_binary_package():
        print("❌ バイナリパッケージ化に失敗しました。リリース中断。")
        return
    # --- 改ざん検知テスト ---
    try:
        import importlib.util
        import sys
        # youtube_py2/__init__.py の verify_binaries 関数を呼び出し
        spec = importlib.util.spec_from_file_location("youtube_py2", str(Path("youtube_py2/__init__.py")))
        youtube_py2 = importlib.util.module_from_spec(spec)
        sys.modules["youtube_py2"] = youtube_py2
        spec.loader.exec_module(youtube_py2)
        if hasattr(youtube_py2, "verify_binaries"):
            print("\n🔍 バイナリ改ざん検知テストを実行...")
            youtube_py2.verify_binaries()
            print("✅ バイナリ改ざん検知テスト完了")
        else:
            print("⚠️ verify_binaries() 関数が __init__.py に見つかりません")
    except Exception as e:
        print(f"⚠️ バイナリ改ざん検知テスト中に例外: {e}")


def test_binary_tamper_detection():
    """
    analytics.cp310-win_amd64.pyd を一時的に壊して verify_binaries() の改ざん検知をテストする。
    テスト後は元に戻す。
    """
    import sys
    from pathlib import Path
    import time
    from youtube_py2 import verify_binaries
    pyd_path = Path("src/youtube_py2/analytics.cp310-win_amd64.pyd")
    backup_path = pyd_path.with_suffix(".bak")
    # バックアップ
    shutil.copy2(pyd_path, backup_path)
    try:
        # 1バイト壊す
        with open(pyd_path, "r+b") as f:
            f.seek(0, 2)
            size = f.tell()
            if size > 0:
                f.seek(size - 1)
                last = f.read(1)
                f.seek(size - 1)
                f.write(bytes([(last[0] ^ 0xFF) & 0xFF]))
        print("[テスト] バイナリを一時的に壊しました。改ざん検知を実行します...")
        try:
            verify_binaries()
        except Exception as e:
            print(f"[OK] 改ざん検知が発動: {e}")
        else:
            print("[NG] 改ざん検知が発動しませんでした")
    finally:
        # 元に戻す
        shutil.move(backup_path, pyd_path)
        print("[テスト] バイナリを元に戻しました")


def main():
    """メイン処理"""
    # コマンドライン引数のヘルプ確認
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("使用方法:")
        print("  python release.py                    # インタラクティブモード")
        print("  python release.py [patch|minor|major] [--test]  # コマンドラインモード")
        print("")
        print("インタラクティブモード（推奨）:")
        print("  コンソールで選択肢を表示し、ユーザーが選択")
        print("")
        print("コマンドラインモード:")
        print("  patch    パッチバージョンアップ")
        print("  minor    マイナーバージョンアップ")
        print("  major    メジャーバージョンアップ")
        print("  --test   TestPyPIにのみアップロード")
        print("")
        print("特徴:")
        print("  🔒 完全バイナリ化ビルド（Cython使用）")
        print("  🚀 ソースコード保護")
        print("  ⚡ 高速実行")
        return
    
    # 前提条件チェック
    if not Path('setup.py').exists() and not Path(PACKAGE_NAME, 'setup.py').exists():
        print("❌ setup.py が見つかりません")
        print("完全バイナリ化にはsetup.pyが必要です")
        sys.exit(1)
    
    print("🎯 YouTube.py3 リリース管理ツール")
    print("=" * 50)
    
    # コマンドライン引数がある場合は従来の方法
    if len(sys.argv) > 1 and sys.argv[1] not in ['-h', '--help']:
        version_type = 'patch'
        test_only = False
        
        for arg in sys.argv[1:]:
            if arg == '--test':
                test_only = True
            elif arg in ['patch', 'minor', 'major']:
                version_type = arg
        
        upload_target = 'testpypi' if test_only else 'pypi'
        success = release(version_type, upload_target)
    else:
        # インタラクティブモード
        current_version = show_current_version()
        
        # バージョンタイプを選択
        version_type = get_version_type_interactive()
        
        # 新しいバージョンをプレビュー
        new_version = preview_new_version(current_version, version_type)
        
        # アップロード先を選択
        upload_target = get_upload_target_interactive()
        
        # 確認
        if confirm_release(version_type, upload_target, current_version, new_version):
            success = release(version_type, upload_target)
        else:
            print("❌ リリースをキャンセルしました")
            return
    
    if success:
        print("\n🎉 完全バイナリ化リリースプロセスが正常に完了しました！")
    else:
        print("\n❌ リリースプロセスでエラーが発生しました")
        sys.exit(1)


if __name__ == '__main__':
    main()