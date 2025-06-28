# FnGuide 재무제표 크롤러

FnGuide 웹사이트(www.fnguide.com)에서 기업의 재무제표 데이터를 크롤링하는 파이썬 프로젝트입니다.

## 요구사항
- Python 3.11.8
- 주요 패키지 버전:
  - selenium 4.15.2
  - requests 2.31.0
  - beautifulsoup4 4.12.2
  - pandas 2.1.3
  - python-dotenv 1.0.0
  - webdriver-manager 4.0.1
  - lxml 4.9.3

## 주요 기능
- FnGuide 웹사이트 자동 로그인
- 기업별 매출액, 영업이익 데이터 추출
- 분기별 데이터 조회 및 저장
- 실시간 CSV 파일 저장 (중간 종료 시에도 데이터 보존)

## 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/dev-jsLee/fnguide_crawling.git
cd fnguide
```

2. 가상환경 생성 및 활성화
```bash
# Windows
python -m venv venv
venv\Scripts\activate
```
```bash
# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경변수 설정
`.env` 파일을 생성하고 다음 내용을 추가:
```
FNGUIDE_USERNAME=your_username
FNGUIDE_PASSWORD=your_password
```

## 사용 방법

1. 종목코드 파일 준비
`code.txt` 파일을 생성하고 조회할 종목코드를 한 줄에 하나씩 입력:
```
000660
005930
035720
```

2. 크롤러 실행
```bash
python main2.py
```

3. 분기 입력
프로그램 실행 시 조회할 연도와 분기를 입력:
```
연도와 분기를 입력하세요 (예: 2025 2): 2025 2
```

4. 결과 확인
- 데이터는 `YYYYMMDD_YYYYMMQ.csv` 형식의 파일로 저장됩니다.
  (예: 20240315_2025032.csv)
- 각 종목의 데이터는 실시간으로 파일에 저장됩니다.

## 설정 변경

`config/config.py` 파일에서 다음 설정을 변경할 수 있습니다:

1. 크롤러 설정
```python
CRAWLER_CONFIG = {
    'headless': False,  # 브라우저 화면 표시 여부
    'debug_mode': True,  # 디버그 모드 여부
    'skip_step': 0,  # 디버그 모드에서 스킵할 단계
}
```

2. 파일 경로 설정
```python
FILE_PATHS = {
    'stock_codes': 'code.txt',  # 종목코드 파일 경로
    'data_dir': 'data',  # 데이터 저장 디렉토리
    'log_dir': 'logs',  # 로그 저장 디렉토리
}
```

## 주의사항
- FnGuide의 이용약관을 준수하여 사용하시기 바랍니다.
- 과도한 요청은 서버에 부하를 줄 수 있으므로 적절한 간격을 두고 크롤링하세요.
- 크롤링한 데이터는 개인 용도로만 사용하시기 바랍니다. 
- 로그인 세션이 만료되면 자동으로 재로그인을 시도합니다.
- 크롤링 중 오류가 발생해도 이전까지 수집된 데이터는 파일에 저장됩니다. 