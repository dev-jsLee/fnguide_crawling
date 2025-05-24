import os
import pandas as pd
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from .base import BaseCrawler
from config.config import (
    ITEM_DETAIL_URL, 
    DATA_DIR, 
    BASE_URL, 
    USERNAME, 
    PASSWORD,
    SELECTORS,
    REQUEST_DELAY
)
import time
# from auth import login

class FnGuideCrawler(BaseCrawler):
    def __init__(self, headless=True, debug_mode=False):
        """
        FnGuide 크롤러 초기화
        
        Args:
            headless (bool): 브라우저 화면 표시 여부 (True: 화면 없음, False: 화면 표시)
            debug_mode (bool): 디버그 모드 여부 (True: 각 단계에서 사용자 입력 대기)
        """
        super().__init__(headless)
        self.debug_mode = debug_mode
        
    def _wait_debug_step(self, step_name):
        """디버그 모드에서 사용자 입력 대기"""
        if self.debug_mode:
            input(f"\n[디버그 모드] '{step_name}' 단계 완료. 계속하려면 Enter를 누르세요...")
        
    def login(self):
        """
        FnGuide 웹사이트 로그인
        
        Returns:
            bool: 로그인 성공 여부
        """
        if self.debug_mode:
            self.logger.info("[디버그 모드] 로그인 프로세스 시작")
        
        def login_process():
            try:
                # 로그인 페이지로 이동
                self.get_page(BASE_URL)
                
                # ID 입력
                id_field = self.wait_for_element(
                    By.CSS_SELECTOR, 
                    SELECTORS['login']['id_field']
                )
                if not id_field:
                    self.logger.error("ID 입력 필드를 찾을 수 없습니다.")
                    return False
                
                id_field.clear()
                id_field.send_keys(USERNAME)
                
                if self.debug_mode:
                    self.logger.info("ID 입력 완료")
                    
                # 비밀번호 입력
                pw_field = self.wait_for_element(
                    By.CSS_SELECTOR, 
                    SELECTORS['login']['pw_field']
                )
                if not pw_field:
                    self.logger.error("비밀번호 입력 필드를 찾을 수 없습니다.")
                    return False
                
                pw_field.clear()
                pw_field.send_keys(PASSWORD + Keys.RETURN)  # 비밀번호 입력 후 Enter 키 입력
                
                if self.debug_mode:
                    self.logger.info("비밀번호 입력 및 로그인 시도 완료")
                
                # 로그인 버튼 클릭
                submit_button = self.wait_for_element(
                    By.CSS_SELECTOR,
                    SELECTORS['login']['submit_button']
                )
                if not submit_button:
                    self.logger.error("로그인 버튼을 찾을 수 없습니다.")
                    return False
                    
                submit_button.click()
                return True
                
            except Exception as e:
                self.logger.error(f"로그인 프로세스 중 오류 발생: {str(e)}")
                return False
                
        result = login_process()
        self._wait_debug_step("로그인")
        return result
    
    def get_item_detail(self, stock_code):
        """
        특정 종목의 상세 정보 조회
        
        Args:
            stock_code (str): 조회할 종목 코드
            
        Returns:
            dict: 추출된 데이터 또는 실패 시 None
        """
        if self.debug_mode:
            self.logger.info(f"[디버그 모드] 종목 {stock_code} 상세정보 조회 시작")
            
        # 로그인 상태 확인
        if not self.login_manager.ensure_logged_in():
            return None
            
        # 종목 상세 페이지로 이동
        url = f"{ITEM_DETAIL_URL}"
        if not self.get_page(url):
            return None
            
        self._wait_debug_step("페이지 로딩")
        
        try:
            # 검색 창 찾기
            search_input = self.wait_for_element(By.ID, "txtSearchWd")
            if not search_input:
                self.logger.error("검색 창을 찾을 수 없습니다.")
                return None
            # 검색창에 종목코드 입력
            search_input.clear()
            search_input.send_keys(stock_code)
            search_input.send_keys(Keys.RETURN)
            
            time.sleep(REQUEST_DELAY)  # 검색 결과 로딩 대기
            
            # 콘텐츠 로딩 대기
            content_loaded = self.wait_for_element(By.ID, "txtSearchWd")
            if not content_loaded:
                self.logger.error(f"종목 {stock_code}의 콘텐츠 로딩 실패")
                return None
                
            self._wait_debug_step("콘텐츠 로딩")
            
            # BeautifulSoup으로 데이터 추출
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            
            # 기본 정보 추출
            data = {
                'stock_code': stock_code,
                'timestamp': datetime.now().isoformat(),
                'company_name': self._extract_company_name(soup),
                'current_price': self._extract_current_price(soup),
                'financial_info': self._extract_financial_info(soup),
                'trading_info': self._extract_trading_info(soup)
            }
            
            self._wait_debug_step("데이터 추출")
            
            # CSV 파일로 저장
            self._save_to_csv(data, stock_code)
            
            self._wait_debug_step("데이터 저장")
            
            return data
            
        except Exception as e:
            self.logger.error(f"종목 {stock_code} 데이터 추출 실패: {str(e)}")
            return None
            
    def _extract_company_name(self, soup):
        """회사명 추출"""
        try:
            name_element = soup.find('h1', class_='company-name')
            return name_element.text.strip() if name_element else None
        except Exception as e:
            self.logger.warning(f"회사명 추출 실패: {str(e)}")
            return None
            
    def _extract_current_price(self, soup):
        """현재가 추출"""
        try:
            price_element = soup.find('div', class_='current-price')
            return float(price_element.text.strip().replace(',', '')) if price_element else None
        except Exception as e:
            self.logger.warning(f"현재가 추출 실패: {str(e)}")
            return None
            
    def _extract_financial_info(self, soup):
        """
        재무 정보 추출
        
        Note: FnGuide 웹사이트의 실제 HTML 구조에 맞게 수정 필요
        """
        try:
            financial_data = {}
            financial_table = soup.find('table', class_='financial-info')
            if financial_table:
                rows = financial_table.find_all('tr')
                for row in rows:
                    cols = row.find_all(['th', 'td'])
                    if len(cols) >= 2:
                        key = cols[0].text.strip()
                        value = cols[1].text.strip()
                        financial_data[key] = value
            return financial_data
        except Exception as e:
            self.logger.warning(f"재무 정보 추출 실패: {str(e)}")
            return {}
            
    def _extract_trading_info(self, soup):
        """
        거래 정보 추출
        
        Note: FnGuide 웹사이트의 실제 HTML 구조에 맞게 수정 필요
        """
        try:
            trading_data = {}
            trading_table = soup.find('table', class_='trading-info')
            if trading_table:
                rows = trading_table.find_all('tr')
                for row in rows:
                    cols = row.find_all(['th', 'td'])
                    if len(cols) >= 2:
                        key = cols[0].text.strip()
                        value = cols[1].text.strip()
                        trading_data[key] = value
            return trading_data
        except Exception as e:
            self.logger.warning(f"거래 정보 추출 실패: {str(e)}")
            return {}
            
    def _save_to_csv(self, data, stock_code):
        """
        추출된 데이터를 CSV 파일로 저장
        
        Args:
            data (dict): 저장할 데이터
            stock_code (str): 종목 코드
        """
        try:
            # 타임스탬프를 포함한 파일명 생성
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{stock_code}_{timestamp}.csv"
            filepath = os.path.join(DATA_DIR, filename)
            
            # DataFrame으로 변환
            df = pd.DataFrame([data])
            
            # CSV로 저장
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            self.logger.info(f"데이터 저장 완료: {filepath}")
            
        except Exception as e:
            self.logger.error(f"CSV 저장 실패: {str(e)}") 