# 크롤러 기본 설정
CRAWLER_CONFIG = {
    # 'headless': True,  # 브라우저 화면 표시 여부
    'headless': False,  # 브라우저 화면 표시 여부
    # 'debug_mode': False,  # 디버그 모드 여부
    'debug_mode': True,  # 디버그 모드 여부
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