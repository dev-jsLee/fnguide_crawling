@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
echo =====================================
echo FnGuide 크롤러 GUI 실행
echo =====================================
echo.

:: 현재 디렉토리를 스크립트 위치로 설정
cd /d "%~dp0"
echo 현재 디렉토리: %CD%
echo.

:: 가상환경 확인 및 활성화
echo 가상환경 확인 중...
if exist .venv\Scripts\activate.bat (
    echo 가상환경을 활성화합니다...
    call .venv\Scripts\activate
    echo 가상환경이 활성화되었습니다.
    echo.
) else (
    echo 경고: 가상환경이 없습니다.
    echo.
    if exist install_env.bat (
        set /p setup_choice="완전한 환경 설정을 위해 install_env.bat을 실행하시겠습니까? (y/n): "
        if /i "!setup_choice!"=="y" (
            echo.
            echo 새 창에서 install_env.bat을 실행합니다...
            start "FnGuide 환경 설정" cmd /c "install_env.bat"
            echo.
            echo 환경 설정이 완료된 후 다시 run.bat을 실행해주세요.
            pause
            exit /b 0
        ) else (
            echo 환경 설정을 건너뛰었습니다.
            echo 시스템 Python을 사용합니다. (권장하지 않음)
            echo.
        )
    ) else (
        echo install_env.bat 파일을 찾을 수 없습니다.
        echo 시스템 Python을 사용합니다. (권장하지 않음)
        echo.
    )
)

:: Python 및 run_GUI.py 파일 확인
echo Python 설치 확인 중...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 오류: Python이 설치되어 있지 않습니다.
    echo.
    if exist install_env.bat (
        set /p install_choice="환경 설정을 위해 install_env.bat을 실행하시겠습니까? (y/n): "
        if /i "!install_choice!"=="y" (
            echo.
            echo 새 창에서 install_env.bat을 실행합니다...
            start "FnGuide 환경 설정" cmd /c "install_env.bat"
            echo.
            echo 환경 설정이 완료된 후 다시 run.bat을 실행해주세요.
        ) else (
            echo 환경 설정을 건너뛰었습니다.
            echo 수동으로 Python을 설치한 후 다시 실행해주세요.
        )
    ) else (
        echo install_env.bat 파일을 찾을 수 없습니다.
        echo 수동으로 Python을 설치해주세요.
    )
    pause
    exit /b 1
)

echo run_GUI.py 파일 확인 중...
if not exist run_GUI.py (
    echo 오류: run_GUI.py 파일을 찾을 수 없습니다.
    echo 현재 디렉토리의 파일 목록:
    dir *.py
    pause
    exit /b 1
) else (
    echo run_GUI.py 파일을 찾았습니다.
)

:: GUI 프로그램 실행
echo FnGuide 크롤러 GUI를 시작합니다...
echo.
python run_GUI.py

:: 프로그램 종료 후 메시지
echo.
echo =====================================
echo 프로그램이 종료되었습니다.
echo =====================================
pause 