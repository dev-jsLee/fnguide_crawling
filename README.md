# FnGuide Crawler

FnGuide 웹사이트(www.fnguide.com)에서 금융 데이터를 크롤링하는 파이썬 프로젝트입니다.

## 기능
- FnGuide 웹사이트 자동 로그인
- 종목 상세 정보 크롤링
- 데이터 저장 및 관리

## 설치 방법

1. 저장소 클론
```bash
git clone [repository-url]
cd fnguide
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
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

1. 크롤러 실행
```python
from src.crawler.fnguide import FnGuideCrawler

crawler = FnGuideCrawler()
crawler.login()
data = crawler.get_item_detail("종목코드")
```

## 주의사항
- FnGuide의 이용약관을 준수하여 사용하시기 바랍니다.
- 과도한 요청은 서버에 부하를 줄 수 있으므로 적절한 간격을 두고 크롤링하세요.
- 크롤링한 데이터는 개인 용도로만 사용하시기 바랍니다. 