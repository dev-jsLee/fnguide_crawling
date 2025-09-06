@echo off
chcp 65001 >nul
echo ========================================
echo FnGuide 크롤러 exe 빌드 스크립트
echo ========================================
echo.

REM 가상환경 활성화 확인
if not exist ".venv\Scripts\activate.bat" (
    echo ❌ 가상환경이 없습니다. 먼저 가상환경을 생성하세요.
    echo.
    echo 다음 명령어를 실행하세요:
    echo python -m venv .venv
    echo .venv\Scripts\activate
    echo.
    pause
    exit /b 1
)

echo 🔄 가상환경 활성화 중...
call .venv\Scripts\activate.bat

echo.
echo 🐍 Python 버전 확인:
python --version

echo.
echo 📦 현재 설치된 패키지 확인:
pip list | findstr -i "selenium pyqt5 pandas"

echo.
echo 🚀 빌드 시작...
python build_exe.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 빌드가 성공적으로 완료되었습니다!
    echo 📁 배포 패키지 위치: dist\FnGuide_Crawler_Package\
    echo.
    echo 배포 패키지를 확인하시겠습니까? (Y/N)
    set /p choice=
    if /i "%choice%"=="Y" (
        explorer dist\FnGuide_Crawler_Package\
    )
) else (
    echo.
    echo ❌ 빌드 중 오류가 발생했습니다.
    echo 로그를 확인하고 문제를 해결한 후 다시 시도하세요.
)

echo.
pause
