@echo off
chcp 932 > nul
set ZIPNAME=証明書_7day.zip
set SRCDIR=証明書_7day
cd /d %~dp0
if exist %SRCDIR%\%ZIPNAME% del %SRCDIR%\%ZIPNAME%
powershell -Command "Compress-Archive -Path '%SRCDIR%\\pass.txt','%SRCDIR%\\readme.txt','%SRCDIR%\\set_license_env_system.bat','%SRCDIR%\\set_license_env_user.bat','%SRCDIR%\\License_7day_cert.pem','%SRCDIR%\\License_7day_issued_at.txt' -DestinationPath '%SRCDIR%\\%ZIPNAME%' -Force"
if exist %SRCDIR%\%ZIPNAME% (
    echo [成功] 必要ファイルのみ %SRCDIR%\%ZIPNAME% に圧縮しました。
) else (
    echo [失敗] zip作成に失敗しました。
)
timeout /t 3 >nul
exit /b 0