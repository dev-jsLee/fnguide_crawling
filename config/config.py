import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# URLs
BASE_URL = "https://www.fnguide.com"
LOGIN_URL = f"{BASE_URL}/home/login"
ITEM_DETAIL_URL = f"{BASE_URL}/Fgdc/ItemDetail"

# Credentials
USERNAME = os.getenv("FNGUIDE_USERNAME")
PASSWORD = os.getenv("FNGUIDE_PASSWORD")

# 분기 설정
QUARTER_CONFIG = {
    'year': None,  # 조회할 연도 (사용자 입력)
    'quarter': None,  # 조회할 분기 (사용자 입력)
    'input_format': 'YYYY Q',  # 입력 형식 (예: 2025 2)
    'input_prompt': '연도와 분기를 입력하세요 (예: 2025 2): '  # 입력 프롬프트
}

# 연간 데이터 설정
ANNUAL_CONFIG = {
    'year': None,  # 조회할 연도 (사용자 입력)
    'input_format': 'YYYY',  # 입력 형식 (예: 2025)
    'input_prompt': '연도를 입력하세요 (예: 2025): '  # 입력 프롬프트
}

# CSS Selectors
SELECTORS = {
    # 로그인 폼 관련 선택자
    'login': {
        'id_field': "#txtID",
        'pw_field': "#txtPW",
        'submit_button': "#divLogin > div.lay--popFooter > form > button.btn--back",
        'success_check': ".user-profile, .welcome-message",
        'search_button': "#divAutoComp > div.result > ul > li > button",
        'quarter_submit': "#btnSubmit"
    },
    # 분기 선택 관련 선택자
    'branch': {
        'selector': "#selGsYm",
        'option_template': "#selGsYm > option[value='{}']"  # value 값으로 옵션 선택
    },
    # 연간/분기 선택 관련 선택자
    'annual': {
        'selector': "#selAqGb",
        'annual_option': "#selAqGb > option[value='A']",
        'quarter_option': "#selAqGb > option[value='Q']"
    }
}

# Selenium Settings
WEBDRIVER_TIMEOUT = 30  # seconds
IMPLICIT_WAIT = 10  # seconds

# Request Settings
REQUEST_TIMEOUT = 30  # seconds
REQUEST_DELAY = 2  # seconds between requests

# File Paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True) 

# 크롤러 기본 설정
CRAWLER_CONFIG = {
    # 'headless': True,  # 브라우저 화면 안 보임
    'headless': False,  # 브라우저 화면 보임
    'debug_mode': False,  # 디버그 안 보임
    # 'debug_mode': True,  # 디버그 모드
    'skip_step': 0,  # 디버그 모드에서 스킵할 단계
}

# 파일 경로 설정
FILE_PATHS = {
    'stock_codes': 'code.txt',  # 종목코드 파일 경로
    'data_dir': 'data',  # 데이터 저장 디렉토리
    'log_dir': 'logs',  # 로그 저장 디렉토리
}

# 로깅 설정
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'encoding': 'utf-8'
}

# CSV 파일 설정
CSV_CONFIG = {
    'encoding': 'utf-8',
    'columns': ['stock_code', 'stock_name', 'sales', 'operating_profit']
} 