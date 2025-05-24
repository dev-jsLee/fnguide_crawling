import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from config.config import WEBDRIVER_TIMEOUT, IMPLICIT_WAIT, REQUEST_DELAY

class BaseCrawler:
    def __init__(self, headless=True):
        """
        기본 크롤러 초기화
        
        Args:
            headless (bool): 브라우저 화면 표시 여부 (True: 화면 없음, False: 화면 표시)
        """
        self.logger = self._setup_logger()
        self.driver = self._setup_driver(headless)
        self.wait = WebDriverWait(self.driver, WEBDRIVER_TIMEOUT)
        
    def _setup_logger(self):
        """로깅 설정 초기화"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        # 로그 핸들러 생성
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler('logs/crawler.log')
        
        # 로그 포맷 설정
        format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        c_format = logging.Formatter(format_str)
        f_format = logging.Formatter(format_str)
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)
        
        # 로거에 핸들러 추가
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)
        
        return logger
        
    def _setup_driver(self, headless):
        """
        크롬 웹드라이버 설정
        
        Args:
            headless (bool): 헤드리스 모드 사용 여부
        """
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(IMPLICIT_WAIT)
        
        return driver
        
    def get_page(self, url):
        """
        웹 페이지 안전하게 로드
        
        Args:
            url (str): 접속할 URL
            
        Returns:
            bool: 성공 여부
        """
        try:
            self.driver.get(url)
            time.sleep(REQUEST_DELAY)  # 요청 간격 준수
            return True
        except WebDriverException as e:
            self.logger.error(f"페이지 로드 실패 {url}: {str(e)}")
            return False
            
    def wait_for_element(self, by, value, timeout=None):
        """
        페이지에서 특정 요소가 나타날 때까지 대기
        
        Args:
            by: Selenium 요소 찾기 방식 (ID, CLASS_NAME 등)
            value: 찾을 요소의 값
            timeout (int, optional): 대기 시간(초)
            
        Returns:
            WebElement or None: 찾은 요소 또는 None
        """
        try:
            wait = WebDriverWait(self.driver, timeout or WEBDRIVER_TIMEOUT)
            return wait.until(EC.presence_of_element_located((by, value)))
        except TimeoutException:
            self.logger.warning(f"요소 대기 시간 초과 {by}={value}")
            return None
            
    def close(self):
        """브라우저 종료 및 자원 정리"""
        if self.driver:
            self.driver.quit()
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료 처리"""
        self.close()
        if exc_type:
            self.logger.error(f"오류 발생: {exc_type.__name__}: {str(exc_val)}")
            return False  # 예외 다시 발생
        return True 