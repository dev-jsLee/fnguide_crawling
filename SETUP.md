# FnGuide 크롤러 설정 가이드

## 🚀 빠른 시작

### 1. uv 설치
```bash
pip install uv
```

### 2. 프로젝트 클론
```bash
git clone https://github.com/dev-jsLee/fnguide_crawling.git
cd fnguide_crawling
```

### 3. 가상환경 설정 및 의존성 설치
```bash
uv venv
uv sync
```

### 4. exe 파일 빌드
```bash
# Windows
build.bat

# 또는 Python으로
python build.py
```

## 📋 상세 설정

### 환경 요구사항
- Python 3.11 이상
- uv (Python 패키지 관리자)
- Windows 10 이상 (GUI 실행용)

### 프로젝트 구조
```
fnguide-crawler/
├── src/                    # 소스 코드
│   ├── gui/               # GUI 관련 코드
│   ├── crawler/           # 크롤러 로직
│   ├── core/              # 핵심 서비스
│   └── utils/             # 유틸리티
├── config/                # 설정 파일
├── docs/                  # 문서
├── .github/workflows/     # GitHub Actions
├── build.py              # 빌드 스크립트
├── build.bat             # Windows 빌드 배치
├── pyproject.toml        # 프로젝트 설정
├── requirements.txt      # 의존성 목록
└── README.md            # 프로젝트 설명
```

### 설정 파일 수정

#### 1. 로그인 정보 설정
`config/config.py` 파일에서 다음을 수정하세요:
```python
# FnGuide 로그인 정보
USERNAME = "your_username"
PASSWORD = "your_password"
```

#### 2. 종목코드 파일 설정
`code.txt` 파일에 조회할 종목코드를 입력하세요:
```
000660
005930
035720
```

#### 3. 브라우저 설정
`config/config.py`에서 브라우저 설정을 변경할 수 있습니다:
```python
# 브라우저 설정
BROWSER_CONFIG = {
    'headless': False,  # True: 브라우저 숨김, False: 브라우저 표시
    'debug_mode': False,  # 디버그 모드
}
```

## 🔧 개발 환경 설정

### 개발용 의존성 설치
```bash
uv sync --dev
```

### 코드 포맷팅
```bash
uv run black src/
uv run isort src/
```

### 코드 검사
```bash
uv run flake8 src/
```

### 테스트 실행
```bash
uv run pytest
```

## 📦 빌드 옵션

### 기본 빌드
```bash
python build.py
```

### 수동 빌드 (고급 사용자)
```bash
# 가상환경 활성화
uv venv
uv sync --extra build

# PyInstaller 직접 실행
uv run pyinstaller --onefile --windowed --name FnGuide_Crawler --add-data "config;config" --add-data "code.txt;." run_GUI.py
```

### 빌드 결과
빌드 완료 후 `dist/FnGuide_Crawler_Package/` 폴더에 다음이 생성됩니다:
- `FnGuide_Crawler.exe`: 메인 실행 파일
- `code.txt`: 종목코드 예시 파일
- `config/`: 설정 폴더
- `data/`: 데이터 저장 폴더
- `사용법.txt`: 사용 설명서

## 🐛 문제 해결

### 1. uv 설치 오류
```bash
# pip 업그레이드 후 재설치
python -m pip install --upgrade pip
pip install uv
```

### 2. 의존성 설치 오류
```bash
# 캐시 정리 후 재설치
uv cache clean
uv sync
```

### 3. 빌드 오류
- Python 버전 확인: `python --version` (3.11 이상 필요)
- 가상환경 활성화 확인
- 필요한 파일들이 모두 있는지 확인

### 4. 실행 오류
- Windows Defender나 백신 프로그램이 exe 파일을 차단하지 않는지 확인
- 관리자 권한으로 실행해보기
- Chrome 브라우저가 설치되어 있는지 확인

## 📞 지원

문제가 지속되면 다음을 확인하세요:
1. [Issues](https://github.com/your-username/fnguide-crawler/issues) 페이지에서 유사한 문제 검색
2. 새로운 이슈 생성
3. 로그 파일 확인 (`logs/` 폴더)

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.
