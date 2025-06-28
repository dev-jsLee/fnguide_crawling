@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
echo =====================================
echo FnGuide 크롤러 환경 설정
echo =====================================
echo.

:: 1. 파이썬 3.11 설치 확인
echo [1/5] 파이썬 3.11 설치 확인 중...

:: py -3.11 명령어로 Python 3.11 확인
py -3.11 --version >nul 2>&1
if %errorlevel% equ 0 (
    :: Python 3.11이 설치되어 있음
    for /f "tokens=2" %%i in ('py -3.11 --version 2^>^&1') do set python311_version=%%i
    echo 파이썬 3.11 버전이 설치되어 있습니다: !python311_version!
    goto setup_venv
) else (
    :: Python 3.11이 설치되어 있지 않음
    echo 파이썬 3.11 버전이 설치되어 있지 않습니다.
    
    :: 일반 python 명령어로 다른 버전 확인
    python --version >nul 2>&1
    if %errorlevel% equ 0 (
        for /f "tokens=2" %%i in ('python --version 2^>^&1') do set current_version=%%i
        echo 현재 설치된 파이썬 버전: !current_version!
        echo 파이썬 3.11 버전이 필요합니다.
    ) else (
        echo 파이썬이 전혀 설치되어 있지 않습니다.
    )
    goto install_python
)

:install_python
echo.
set /p install_python="파이썬 3.11을 설치하시겠습니까? (y/n): "
if /i "!install_python!"=="y" (
    echo 파이썬 3.11 설치 중...
    winget install Python.Python.3.11
    if %errorlevel% neq 0 (
        echo 파이썬 설치에 실패했습니다. 수동으로 설치해주세요.
        echo https://www.python.org/downloads/release/python-3118/
        pause
        exit /b 1
    )
    echo 파이썬 3.11 설치가 완료되었습니다.
    echo PATH를 업데이트하기 위해 새 터미널에서 다시 실행해주세요.
    pause
    exit /b 0
) else (
    echo 파이썬 3.11 설치를 취소했습니다.
    echo 파이썬 3.11을 수동으로 설치한 후 다시 실행해주세요.
    echo https://www.python.org/downloads/release/python-3118/
    pause
    exit /b 1
)

:setup_venv
echo.

:: 2. 파이썬 가상환경 세팅
echo [2/5] 가상환경 생성 중...
if exist .venv (
    echo 기존 가상환경이 발견되었습니다.
    set /p recreate_venv="기존 가상환경을 삭제하고 새로 만드시겠습니까? (y/n): "
    if /i "!recreate_venv!"=="y" (
        echo 기존 가상환경 삭제 중...
        rmdir /s /q .venv
    ) else (
        echo 기존 가상환경을 사용합니다.
        goto activate_venv
    )
)

py -3.11 -m venv .venv
if %errorlevel% neq 0 (
    echo 가상환경 생성에 실패했습니다.
    pause
    exit /b 1
)
echo 파이썬 3.11로 가상환경이 생성되었습니다.

:activate_venv
:: 3. 가상환경 활성화
echo.
echo [3/5] 가상환경 활성화 중...
call .venv\Scripts\activate
if %errorlevel% neq 0 (
    echo 가상환경 활성화에 실패했습니다.
    pause
    exit /b 1
)
echo 가상환경이 활성화되었습니다.

:: 4. uv 설치
echo.
echo [4/5] uv 설치 중...
python -m pip install --upgrade pip
python -m pip install uv
if %errorlevel% neq 0 (
    echo uv 설치에 실패했습니다.
    pause
    exit /b 1
)
echo uv가 설치되었습니다.

:: 5. uv를 이용한 패키지 설치
echo.
echo [5/5] 의존성 패키지 설치 중...
if not exist requirements.txt (
    echo requirements.txt 파일이 없습니다. 수동으로 패키지를 설치해주세요.
    goto complete_setup
)

uv pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 경고: 일부 패키지 설치에 실패했습니다.
    echo pip을 사용하여 수동으로 설치를 시도합니다...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo 경고: pip을 통한 패키지 설치도 실패했습니다.
        echo 수동으로 패키지를 설치해주세요: pip install -r requirements.txt
    ) else (
        echo pip을 통한 패키지 설치가 완료되었습니다.
    )
) else (
    echo 패키지 설치가 완료되었습니다.
)

:complete_setup
echo.
echo =====================================
echo 환경 설정이 완료되었습니다!
echo =====================================
echo.
echo 다음 명령어로 가상환경을 활성화할 수 있습니다:
echo   .venv\Scripts\activate
echo.
echo 프로그램을 실행하려면:
echo   python run_GUI.py
echo.
pause
