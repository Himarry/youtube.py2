@echo off
chcp 932 > nul
set ZIPNAME=�ؖ���_7day.zip
set SRCDIR=�ؖ���_7day
cd /d %~dp0
if exist %SRCDIR%\%ZIPNAME% del %SRCDIR%\%ZIPNAME%
powershell -Command "Compress-Archive -Path '%SRCDIR%\\pass.txt','%SRCDIR%\\readme.txt','%SRCDIR%\\set_license_env_system.bat','%SRCDIR%\\set_license_env_user.bat','%SRCDIR%\\License_7day_cert.pem','%SRCDIR%\\License_7day_issued_at.txt' -DestinationPath '%SRCDIR%\\%ZIPNAME%' -Force"
if exist %SRCDIR%\%ZIPNAME% (
    echo [����] �K�v�t�@�C���̂� %SRCDIR%\%ZIPNAME% �Ɉ��k���܂����B
) else (
    echo [���s] zip�쐬�Ɏ��s���܂����B
)
timeout /t 3 >nul
exit /b 0