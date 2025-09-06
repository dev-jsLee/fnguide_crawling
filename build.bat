@echo off
chcp 65001 >nul
echo ========================================
echo FnGuide 크롤러 exe 빌드 (uv 기반)
echo ========================================
echo.

REM uv 설치 확인
echo 🔍 uv 설치 확인 중...
uv --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ uv가 설치되지 않았습니다.
    echo.
    echo 📥 uv 설치 중...
    pip install uv
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ uv 설치에 실패했습니다.
        echo 💡 수동 설치: pip install uv
        pause
        exit /b 1
    )
    echo ✅ uv 설치 완료
) else (
    echo ✅ uv가 이미 설치되어 있습니다.
)

echo.
echo 🚀 빌드 시작...
python build.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 빌드 성공!
    echo 📁 결과 위치: dist\FnGuide_Crawler_Package\
    echo.
    echo 실행하시겠습니까? (Y/N)
    set /p choice=
    if /i "%choice%"=="Y" (
        start "dist\FnGuide_Crawler_Package\FnGuide_Crawler.exe"
    )
) else (
    echo.
    echo ❌ 빌드 실패!
    echo 💡 해결 방법:
    echo 1. uv 설치 확인: pip install uv
    echo 2. Python 버전 확인: python --version
    echo 3. 인터넷 연결 확인
)

echo.
pause
