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
    LOGIN_URL,
    USERNAME, 
    PASSWORD,
    SELECTORS,
    REQUEST_DELAY,
    QUARTER_CONFIG
)
import time
# from auth import login

class FnGuideCrawler(BaseCrawler):
    def __init__(self, headless=True, debug_mode=False, skip_step=0, year=None, quarter=None):
        """
        FnGuide 크롤러 초기화
        
        Args:
            headless (bool): 브라우저 화면 표시 여부 (True: 화면 없음, False: 화면 표시)
            debug_mode (bool): 디버그 모드 여부 (True: 각 단계에서 사용자 입력 대기)
            skip_step (int): 디버그 모드에서 스킵할 단계
            year (int): 조회할 연도 (None인 경우 사용자 입력)
            quarter (int): 조회할 분기 (None인 경우 사용자 입력)
        """
        super().__init__(headless)
        self.debug_mode = debug_mode
        self.skip_step = skip_step
        self.year = year
        self.quarter = quarter
        self.quarter_value = self._get_quarter_value()
        
    def _wait_debug_step(self, step_name, step=1):
        """디버그 모드에서 사용자 입력 대기
        step 값이 0이면 모든 단계에서 대기
        """
        if self.debug_mode and self.skip_step <= step:
            input(f"\n[디버그 모드] '{step_name}' 단계 준비 완료. 계속하려면 Enter를 누르세요...")
        
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
                # ID 입력
                id_field = self.wait_for_element(
                    By.CSS_SELECTOR,
                    SELECTORS['login']['id_field']
                )
                if not id_field:
                    self.logger.error("ID 입력 필드를 찾을 수 없습니다.")
                    return False
                
                self._wait_debug_step("ID 입력")
                # id_field.clear()
                id_field.send_keys(str(USERNAME))
                
                # 비밀번호 입력
                pw_field = self.wait_for_element(
                    By.CSS_SELECTOR, 
                    SELECTORS['login']['pw_field']
                )
                if not pw_field:
                    self.logger.error("비밀번호 입력 필드를 찾을 수 없습니다.")
                    return False
                
                self._wait_debug_step("비밀번호 입력")
                pw_field.clear()
                pw_field.send_keys(PASSWORD + Keys.RETURN)  # 비밀번호 입력 후 Enter 키 입력
                
                # 로그인 버튼 클릭
                submit_button = self.wait_for_element(
                    By.CSS_SELECTOR,
                    SELECTORS['login']['submit_button']
                )
                if not submit_button:
                    self.logger.error("로그인 버튼을 찾을 수 없습니다.")
                    return False
                
                self._wait_debug_step("로그인 버튼 클릭")
                submit_button.click()
                return True
                
            except Exception as e:
                self.logger.error(f"로그인 프로세스 중 오류 발생: {str(e)}")
                return False
                
        self._wait_debug_step("로그인 시도")
        
        result = login_process()
        return result
    
    def _search_stock(self, stock_code):
        """종목 검색 수행"""
        try:
            search_input = self.wait_for_element(By.ID, "txtSearchWd")
            if not search_input:
                self.logger.error("검색 창을 찾을 수 없습니다.")
                return None
                
            search_input.clear()
            search_input.send_keys(stock_code)
            time.sleep(1)
            search_input.send_keys(Keys.RETURN)
            time.sleep(REQUEST_DELAY)
            
            return search_input
        except Exception as e:
            self.logger.error(f"종목 검색 실패: {str(e)}")
            return None
            
    def _wait_for_content_load(self):
        """콘텐츠 로딩 대기"""
        try:
            time.sleep(1)
            content_loaded = self.wait_for_element(By.ID, "txtSearchWd")
            if not content_loaded:
                self.logger.error("콘텐츠 로딩 실패")
                return False
            return True
        except Exception as e:
            self.logger.error(f"콘텐츠 로딩 대기 실패: {str(e)}")
            return False
            
    def _extract_stock_data(self, soup, stock_code, stock_name):
        """주식 데이터 추출"""
        try:
            time.sleep(1)
            sales, profit = self._extract_sales_and_operating_profit(soup)
            
            return {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'sales': sales,
                'operating_profit': profit
            }
        except Exception as e:
            self.logger.error(f"데이터 추출 실패: {str(e)}")
            return None

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
        
        self._wait_debug_step("페이지 로딩", 2)
        # 종목 상세 페이지로 이동
        url = f"{ITEM_DETAIL_URL}"
        if not self.get_page(url):
            return None
        current_url = self.driver.current_url
        if current_url == "https://www.fnguide.com/home/login":
            self.logger.info("로그인 페이지로 이동. 로그인 프로세스 재시작.")
            if not self.login():
                self.logger.error("로그인 실패. 프로세스 종료.")
                return None
        try:
            # 1. 종목 검색
            self._wait_debug_step("검색창 입력", 2)
            search_input = self._search_stock(stock_code)
            if not search_input:
                return None
            
            time.sleep(1)
            
            self._wait_debug_step("분기 확인 및 입력", 2)
            branch = self._check_branch()
            if not branch:
                return None
            
            self._wait_debug_step("분기 조회", 2)
            
            quarter_submit = self.wait_for_element(
                By.CSS_SELECTOR,
                SELECTORS['login']['quarter_submit']
            )
            if not quarter_submit:
                return None
                
            # 2. 콘텐츠 로딩 대기
            self._wait_debug_step("콘텐츠 로딩", 2)
            if not self._wait_for_content_load():
                return None
                
            # 3. 데이터 추출
            self._wait_debug_step("데이터 추출", 2)
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            stock_name = search_input.get_attribute('value')
            
            # 4. 데이터 저장
            self._wait_debug_step("데이터 저장", 2)
            data = self._extract_stock_data(soup, stock_code, stock_name)
            if data:
                print("stock_name: ", stock_name)
                return data
            return None

        except Exception as e:
            self.logger.error(f"종목 {stock_code} 데이터 추출 실패: {str(e)}")
            return None
            
    

    def _extract_sales_and_operating_profit(self, soup):
        """매출액과 영업이익 추출"""
        try:
            sales = soup.select_one('#contents > table > tbody > tr:nth-child(4) > td:nth-child(2)')
            operating_profit = soup.select_one('#contents > table > tbody > tr:nth-child(4) > td:nth-child(3)')
            
            def convert_to_number(value_str):
                if not value_str:
                    return None
                # 쉼표 제거 후 숫자로 변환
                try:
                    return float(value_str.replace(',', ''))
                except ValueError:
                    return None
            
            sales_value = convert_to_number(sales.text.strip() if sales else None)
            operating_profit_value = convert_to_number(operating_profit.text.strip() if operating_profit else None)
            
            return (sales_value, operating_profit_value)
        except Exception as e:
            self.logger.warning(f"매출액/영업이익 추출 실패: {str(e)}")
            return (None, None)
            
    def _save_to_csv(self, data, stock_code):
        """
        추출된 데이터를 CSV 파일로 저장
        
        Args:
            data (dict): 저장할 데이터
            stock_code (str): 종목 코드
        """
        try:
            # 타임스탬프를 포함한 파일명 생성
            timestamp = datetime.now().strftime('%Y%m%d')
            filename = f"{stock_code}_{timestamp}.csv"
            filepath = os.path.join(DATA_DIR, filename)
            
            # DataFrame으로 변환
            df = pd.DataFrame([data])
            
            # CSV로 저장
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            self.logger.info(f"데이터 저장 완료: {filepath}")
            
        except Exception as e:
            self.logger.error(f"CSV 저장 실패: {str(e)}") 

    def _get_user_input(self):
        """사용자로부터 연도와 분기 입력 받기"""
        # 이미 설정된 값이 있으면 사용
        if self.year is not None and self.quarter is not None:
            return self.year, self.quarter
            
        while True:
            try:
                user_input = input(QUARTER_CONFIG['input_prompt'])
                year, quarter = user_input.strip().split()
                
                # 입력값 검증
                year = int(year)
                quarter = int(quarter)
                
                if not (2000 <= year <= 2100):
                    print("연도는 2000년부터 2100년 사이여야 합니다.")
                    continue
                    
                if not (1 <= quarter <= 4):
                    print("분기는 1부터 4 사이여야 합니다.")
                    continue
                    
                # 입력받은 값을 저장
                self.year = year
                self.quarter = quarter
                return year, quarter
                
            except ValueError:
                print(f"올바른 형식으로 입력해주세요. 예: {QUARTER_CONFIG['input_format']}")
            except Exception as e:
                print(f"입력 중 오류가 발생했습니다: {str(e)}")
                
    def _get_quarter_value(self):
        """설정된 연도와 분기로 value 값 생성"""
        # 사용자 입력 받기
        year, quarter = self._get_user_input()
        
        # value 형식: YYYYMMQ (예: 2025062)
        # YYYY: 연도, MM: 월(03, 06, 09, 12), Q: 분기(1,2,3,4)
        month_map = {1: '03', 2: '06', 3: '09', 4: '12'}
        month = month_map.get(quarter, '01')
        
        return f"{year}{month}{quarter}"
        
    def _check_branch(self):
        """분기 선택 확인 및 처리"""
        try:
            # 분기 선택 드롭다운 찾기
            branch_selector = self.wait_for_element(
                By.CSS_SELECTOR,
                SELECTORS['branch']['selector']
            )
            if not branch_selector:
                self.logger.error("분기 선택 드롭다운을 찾을 수 없습니다.")
                return False
                
            # 분기 선택 드롭다운 클릭
            branch_selector.click()
            time.sleep(1)  # 옵션 로딩 대기
            
            # 설정된 분기 value 값 가져오기
            self.quarter_value = self._get_quarter_value()
            self.logger.info(f"선택할 분기: {self.quarter_value}")
            
            # 해당 value를 가진 옵션 선택
            option_selector = SELECTORS['branch']['option_template'].format(self.quarter_value)
            target_option = self.wait_for_element(
                By.CSS_SELECTOR,
                option_selector
            )
            if not target_option:
                self.logger.error(f"분기 옵션을 찾을 수 없습니다. (value: {self.quarter_value})")
                return False
                
            # 옵션 선택
            target_option.click()
            time.sleep(1)  # 선택 적용 대기
            
            # 드롭다운 닫기 (다른 요소 클릭)
            self.driver.find_element(By.TAG_NAME, "body").click()
            time.sleep(1)  # 드롭다운 닫힘 대기
            
            # 조회 버튼 클릭
            quarter_submit = self.wait_for_element(
                By.CSS_SELECTOR,
                SELECTORS['login']['quarter_submit']
            )
            if not quarter_submit:
                self.logger.error("조회 버튼을 찾을 수 없습니다.")
                return False
                
            quarter_submit.click()
            time.sleep(1)  # 조회 결과 로딩 대기
            
            self.logger.info(f"분기 선택 완료: {self.quarter_value}")
            return True
            
        except Exception as e:
            self.logger.error(f"분기 선택 중 오류 발생: {str(e)}")
            return False 