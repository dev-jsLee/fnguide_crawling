#!/usr/bin/env python3
"""
FnGuide 크롤러 exe 빌드 스크립트 (uv 기반)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description, shell=True):
    """명령어 실행 및 결과 확인"""
    print(f"\n{'='*60}")
    print(f"실행 중: {description}")
    print(f"명령어: {command}")
    print(f"{'='*60}")
    
    try:
        if shell:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
        
        print("✅ 성공!")
        if result.stdout:
            print("출력:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 실패: {e}")
        if e.stdout:
            print("출력:")
            print(e.stdout)
        if e.stderr:
            print("에러:")
            print(e.stderr)
        return False

def check_uv_installed():
    """uv 설치 확인"""
    print("\n🔍 uv 설치 확인 중...")
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ uv 설치됨: {result.stdout.strip()}")
            return True
        else:
            print("❌ uv가 설치되지 않았습니다.")
            return False
    except FileNotFoundError:
        print("❌ uv를 찾을 수 없습니다.")
        return False

def setup_environment():
    """가상환경 설정 및 의존성 설치"""
    print("\n🔧 가상환경 설정 중...")
    
    # uv venv로 가상환경 생성
    if not run_command("uv venv", "가상환경 생성"):
        return False
    
    # uv sync로 의존성 설치
    if not run_command("uv sync", "의존성 설치"):
        return False
    
    # 빌드용 의존성 설치
    if not run_command("uv sync --extra build", "빌드용 의존성 설치"):
        return False
    
    return True

def clean_build_dirs():
    """빌드 디렉토리 정리"""
    print("\n🧹 빌드 디렉토리 정리 중...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  - {dir_name} 디렉토리 삭제됨")
    
    # src 디렉토리의 __pycache__ 정리
    for root, dirs, files in os.walk('src'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                shutil.rmtree(os.path.join(root, dir_name))
                print(f"  - {os.path.join(root, dir_name)} 삭제됨")

def check_requirements():
    """필수 파일들 확인"""
    print("\n📋 필수 파일 확인 중...")
    
    required_files = [
        'run_GUI.py',
        'pyproject.toml',
        'config/config.py',
        'src/gui/main_window.py',
        'src/crawler/fnguide.py',
        'code.txt',
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ 누락된 파일들:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    print("✅ 모든 필수 파일이 존재합니다.")
    return True

def build_exe():
    """exe 파일 빌드"""
    print("\n🔨 exe 파일 빌드 중...")
    
    # uv run을 사용하여 PyInstaller 실행
    build_command = [
        "uv", "run", "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "FnGuide_Crawler",
        "--add-data", "config;config",
        "--add-data", "code.txt;.",
        "--add-data", "README.md;.",
        "run_GUI.py"
    ]
    
    if not run_command(" ".join(build_command), "PyInstaller로 exe 빌드"):
        return False
    
    return True

def create_distribution_package():
    """배포 패키지 생성"""
    print("\n📦 배포 패키지 생성 중...")
    
    dist_dir = Path("dist")
    package_dir = dist_dir / "FnGuide_Crawler_Package"
    
    # 패키지 디렉토리 생성
    package_dir.mkdir(exist_ok=True)
    
    # exe 파일 복사
    exe_file = dist_dir / "FnGuide_Crawler.exe"
    if exe_file.exists():
        shutil.copy2(exe_file, package_dir)
        print(f"  ✅ {exe_file.name} 복사됨")
    else:
        print(f"  ❌ {exe_file} 파일을 찾을 수 없습니다.")
        return False
    
    # 필요한 파일들 복사
    files_to_copy = [
        ("README.md", "사용 설명서"),
        ("code.txt", "종목코드 예시 파일"),
        ("config", "설정 폴더"),
    ]
    
    for file_path, description in files_to_copy:
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                shutil.copytree(file_path, package_dir / file_path, dirs_exist_ok=True)
            else:
                shutil.copy2(file_path, package_dir)
            print(f"  ✅ {description} 복사됨")
        else:
            print(f"  ⚠️  {file_path} 파일이 없습니다.")
    
    # data 디렉토리 생성
    (package_dir / "data").mkdir(exist_ok=True)
    print("  ✅ data 디렉토리 생성됨")
    
    # 사용자 매뉴얼 생성
    manual_content = """# FnGuide 크롤러 사용법

## 실행 방법
1. FnGuide_Crawler.exe 파일을 더블클릭하여 실행
2. 종목코드 파일(code.txt)에 조회할 종목코드를 입력
3. 연도와 분기를 선택
4. '크롤링 시작' 버튼 클릭

## 설정 파일
- config/config.py: 기본 설정 파일
- code.txt: 종목코드 입력 파일

## 데이터 저장
- 수집된 데이터는 data 폴더에 CSV 파일로 저장됩니다.

## 문제 해결
- 크롤링이 실패하는 경우, 인터넷 연결을 확인하세요.
- 로그인 정보가 올바른지 확인하세요.
- 브라우저가 차단되지 않았는지 확인하세요.
"""
    
    with open(package_dir / "사용법.txt", "w", encoding="utf-8") as f:
        f.write(manual_content)
    print("  ✅ 사용법.txt 생성됨")
    
    print(f"\n🎉 배포 패키지가 생성되었습니다: {package_dir}")
    return True

def main():
    """메인 빌드 프로세스"""
    print("🚀 FnGuide 크롤러 exe 빌드 시작 (uv 기반)")
    print("="*70)
    
    # 1. uv 설치 확인
    if not check_uv_installed():
        print("\n❌ uv가 설치되지 않았습니다.")
        print("💡 설치 방법: pip install uv")
        return False
    
    # 2. 빌드 디렉토리 정리
    clean_build_dirs()
    
    # 3. 필수 파일 확인
    if not check_requirements():
        print("\n❌ 빌드를 중단합니다.")
        return False
    
    # 4. 가상환경 설정 및 의존성 설치
    if not setup_environment():
        print("\n❌ 환경 설정에 실패했습니다.")
        return False
    
    # 5. exe 파일 빌드
    if not build_exe():
        print("\n❌ exe 빌드에 실패했습니다.")
        return False
    
    # 6. 배포 패키지 생성
    if not create_distribution_package():
        print("\n❌ 배포 패키지 생성에 실패했습니다.")
        return False
    
    print("\n" + "="*70)
    print("🎉 빌드가 완료되었습니다!")
    print("📁 배포 패키지 위치: dist/FnGuide_Crawler_Package/")
    print("📄 실행 파일: dist/FnGuide_Crawler_Package/FnGuide_Crawler.exe")
    print("="*70)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
