# FnGuide 크롤러

FnGuide 웹사이트(www.fnguide.com)에서 기업의 재무제표 데이터를 크롤링하는 GUI 애플리케이션입니다.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)](https://pypi.org/project/PyQt5/)
[![Selenium](https://img.shields.io/badge/Selenium-4.15+-orange.svg)](https://pypi.org/project/selenium/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 주요 기능

- 🖥️ **사용자 친화적 GUI**: PyQt5 기반의 직관적인 인터페이스
- 🔐 **자동 로그인**: FnGuide 웹사이트 자동 로그인 및 세션 관리
- 📊 **데이터 추출**: 기업별 매출액, 영업이익 등 재무제표 데이터 추출
- 📅 **연간/분기 지원**: 연간 및 분기별 데이터 조회 가능
- 💾 **실시간 저장**: 중간 종료 시에도 데이터 보존
- 📦 **독립 실행**: exe 파일로 배포 가능

## 🚀 빠른 시작

### 1. uv 설치
```bash
pip install uv
```

### 2. 프로젝트 클론 및 설정
```bash
git clone https://github.com/your-username/fnguide-crawler.git
cd fnguide-crawler
uv venv
uv sync
```

### 3. exe 파일 빌드
```bash
# Windows
build.bat

# 또는 Python으로
python build.py
```

### 4. 실행
`dist/FnGuide_Crawler_Package/FnGuide_Crawler.exe` 파일을 실행하세요.

## 📋 시스템 요구사항

- **Python**: 3.11 이상
- **운영체제**: Windows 10 이상 (GUI 실행용)
- **브라우저**: Chrome (자동 설치됨)
- **메모리**: 최소 4GB RAM 권장

## 🛠️ 설치 방법

### 방법 1: uv 사용 (권장)
```bash
# 1. uv 설치
pip install uv

# 2. 프로젝트 클론
git clone https://github.com/your-username/fnguide-crawler.git
cd fnguide-crawler

# 3. 가상환경 설정 및 의존성 설치
uv venv
uv sync

# 4. exe 빌드
python build.py
```

### 방법 2: pip 사용
```bash
# 1. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. PyInstaller 설치
pip install pyinstaller

# 4. exe 빌드
pyinstaller --onefile --windowed --name FnGuide_Crawler --add-data "config;config" --add-data "code.txt;." run_GUI.py
```

## 📖 사용 방법

### 1. 종목코드 입력
`code.txt` 파일에 조회할 종목코드를 한 줄에 하나씩 입력:
```
000660
005930
035720
```

### 2. 설정 파일 수정
`config/config.py`에서 로그인 정보를 설정:
```python
USERNAME = "your_username"
PASSWORD = "your_password"
```

### 3. GUI 실행
- `FnGuide_Crawler.exe` 실행
- 연도와 분기 선택
- '크롤링 시작' 버튼 클릭

### 4. 결과 확인
- 수집된 데이터는 `data/` 폴더에 CSV 파일로 저장
- 파일명 형식: `stock_data_YYYYMMDD.csv`

## ⚙️ 설정 옵션

`config/config.py`에서 다음 설정을 변경할 수 있습니다:

```python
# 브라우저 설정
BROWSER_CONFIG = {
    'headless': False,  # True: 브라우저 숨김, False: 브라우저 표시
    'debug_mode': False,  # 디버그 모드
}

# 크롤링 설정
CRAWLER_CONFIG = {
    'timeout': 10,  # 페이지 로딩 타임아웃 (초)
    'retry_count': 3,  # 재시도 횟수
}
```

## 📁 프로젝트 구조

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
└── README.md            # 프로젝트 설명
```

## 🔧 개발

### 개발 환경 설정
```bash
# 개발용 의존성 설치
uv sync --dev

# 코드 포맷팅
uv run black src/
uv run isort src/

# 코드 검사
uv run flake8 src/

# 테스트 실행
uv run pytest
```

### 빌드 옵션
```bash
# 기본 빌드
python build.py

# 수동 빌드
uv run pyinstaller --onefile --windowed --name FnGuide_Crawler --add-data "config;config" --add-data "code.txt;." run_GUI.py
```

## 🐛 문제 해결

### 일반적인 문제
1. **uv 설치 오류**: `pip install uv` 실행
2. **의존성 설치 오류**: `uv cache clean && uv sync` 실행
3. **빌드 오류**: Python 3.11 이상 버전 확인
4. **실행 오류**: Windows Defender나 백신 프로그램 확인

### 로그 확인
- 로그 파일: `logs/` 폴더
- 디버그 모드: `config/config.py`에서 `debug_mode: True` 설정

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🤝 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚠️ 주의사항

- FnGuide의 이용약관을 준수하여 사용하시기 바랍니다.
- 과도한 요청은 서버에 부하를 줄 수 있으므로 적절한 간격을 두고 크롤링하세요.
- 크롤링한 데이터는 개인 용도로만 사용하시기 바랍니다.
- 로그인 세션이 만료되면 자동으로 재로그인을 시도합니다.
- 크롤링 중 오류가 발생해도 이전까지 수집된 데이터는 파일에 저장됩니다. 