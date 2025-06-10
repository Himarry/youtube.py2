import youtube_py2.export

def main():
    exporter = youtube_py2.export.YouTubeExport()
    data = [
        {"title": "動画1", "views": 100},
        {"title": "動画2", "views": 200}
    ]
    exporter.export_to_csv(data, "test_export.csv")
    print("[OK] export_to_csv 実行・CSV出力成功")

if __name__ == "__main__":
    main()