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
        """디버그 모드에서 사용자 입력 대기"""
        if self.debug_mode and self.skip_step <= step:
            input(f"\n[디버그 모드] '{step_name}' 단계 준비 완료. 계속하려면 Enter를 누르세요...")
            
    def _get_user_input(self):
        """사용자로부터 연도와 분기 입력 받기"""
        # 이미 설정된 값이 있으면 사용
        if self.year is not None:
            return self.year, self.quarter
            
        while True:
            try:
                # 연간 데이터인 경우 연도만 입력 받기
                if self.quarter is None:
                    year = int(input("연도를 입력하세요 (예: 2024): "))
                    if not (2000 <= year <= 2100):
                        print("연도는 2000년부터 2100년 사이여야 합니다.")
                        continue
                    self.year = year
                    return year, None
                else:
                    # 분기 데이터인 경우 기존 로직 유지
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
                print("올바른 형식으로 입력해주세요.")
            except Exception as e:
                print(f"입력 중 오류가 발생했습니다: {str(e)}")
                
    def _get_quarter_value(self):
        """설정된 연도와 분기로 value 값 생성"""
        # 이미 설정된 값이 있으면 사용
        if self.year is not None:
            year = self.year
            quarter = self.quarter
        else:
            # 설정된 값이 없으면 사용자 입력 받기
            year, quarter = self._get_user_input()
        
        self.logger.info(f"연도/분기 설정 - 연도: {year}, 분기: {quarter}")
        
        # 연간 데이터인 경우
        if quarter is None:
            quarter_value = f"{year}12D"  # 연간 데이터는 12월 + D 접미사
        else:
            # 분기 데이터인 경우: yyyymmn 형식
            month_map = {1: '03', 2: '06', 3: '09', 4: '12'}
            month = month_map.get(quarter, '01')
            quarter_value = f"{year}{month}{quarter}"
        
        self.logger.info(f"생성된 quarter_value: {quarter_value}")
        return quarter_value
        
    def _search_stock(self, stock_code):
        """종목 검색 수행 (페이지 이동 없이 검색만)"""
        try:
            # 페이지 이동 제거 - 이미 올바른 페이지에 있다고 가정
            search_input = self.wait_for_element(By.ID, "txtSearchWd")
            if not search_input:
                self.logger.error("검색 창을 찾을 수 없습니다.")
                return None
            
            search_input.clear()
            search_input.send_keys(stock_code)
            time.sleep(1.5)  # 종목코드 입력 후 1.5초 대기 (자동완성 처리 시간 확보)
            search_input.send_keys(Keys.ARROW_DOWN)  # 아래 방향키로 자동완성 첫 번째 항목 선택
            time.sleep(0.2)  # 방향키 처리 대기
            search_input.send_keys(Keys.RETURN)
            time.sleep(REQUEST_DELAY)
            
            return search_input
        except Exception as e:
            self.logger.error(f"종목 검색 실패: {str(e)}")
            return None
            
    def _wait_for_content_load(self):
        """콘텐츠 로딩 대기"""
        try:
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
            
    def select_annual_data(self):
        """연간 데이터 선택 및 조회"""
        try:
            # 1. 연간/분기 선택 드롭다운 찾기
            annual_selector = self.wait_for_element(
                By.ID,
                "selAqGb"
            )
            if not annual_selector:
                self.logger.error("연간/분기 선택 드롭다운을 찾을 수 없습니다.")
                return False
                
            # 2. 연간/분기 선택 드롭다운 클릭
            annual_selector.click()
            
            # 3. 연간 옵션 선택
            annual_option = self.wait_for_element(
                By.CSS_SELECTOR,
                "#selAqGb > option[value='A']"
            )
            if not annual_option:
                self.logger.error("연간 옵션을 찾을 수 없습니다.")
                return False
                
            # 4. 옵션 선택
            annual_option.click()
            
            # 5. 드롭다운 닫기 (다른 요소 클릭)
            self.driver.find_element(By.TAG_NAME, "body").click()
            time.sleep(0.5)  # 드롭다운 닫힘 대기
            
            # 6. 조회 버튼 클릭
            submit_button = self.wait_for_element(
                By.CSS_SELECTOR,
                "#btnSubmit"
            )
            if not submit_button:
                self.logger.error("조회 버튼을 찾을 수 없습니다.")
                return False
                
            submit_button.click()
            
            # 7. 데이터 테이블 또는 '데이터 없음' 메시지 대기
            # try:
            #     # 먼저 '데이터 없음' 메시지 확인
            #     no_data = self.wait_for_element(
            #         By.CSS_SELECTOR,
            #         "td.nodata[colspan='8']",
            #         timeout=3  # 짧은 타임아웃으로 빠르게 확인
            #     )
            #     if no_data and "데이터가 없습니다" in no_data.text:
            #         self.logger.info("해당 기간의 데이터가 없습니다.")
            #         return False
            # except:
            #     # '데이터 없음' 메시지가 없으면 정상적인 데이터 테이블 확인
            #     data_element = self.wait_for_element(
            #         By.CSS_SELECTOR,
            #         "#contents > table > tbody > tr:nth-child(4) > td:nth-child(2)"
            #     )
            #     if not data_element:
            #         self.logger.error("데이터 테이블 로딩 실패")
            #         return False
            
            self.logger.info("연간 데이터 선택 및 조회 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"연간 데이터 선택 중 오류 발생: {str(e)}")
            return False
            
    def select_quarter_data(self):
        """분기 데이터 선택 및 조회"""
        try:
            # 1. 연간/분기 선택 드롭다운 찾기
            quarter_selector = self.wait_for_element(
                By.ID,
                "selAqGb"
            )
            if not quarter_selector:
                self.logger.error("연간/분기 선택 드롭다운을 찾을 수 없습니다.")
                return False
                
            # 2. 연간/분기 선택 드롭다운 클릭
            quarter_selector.click()
            
            # 3. 분기 옵션 선택
            quarter_option = self.wait_for_element(
                By.CSS_SELECTOR,
                "#selAqGb > option[value='Q']"
            )
            if not quarter_option:
                self.logger.error("분기 옵션을 찾을 수 없습니다.")
                return False
                
            # 4. 옵션 선택
            quarter_option.click()
            
            # 5. 드롭다운 닫기 (다른 요소 클릭)
            self.driver.find_element(By.TAG_NAME, "body").click()
            time.sleep(0.5)  # 드롭다운 닫힘 대기
            
            # 6. 분기 선택
            if not self._check_branch():
                return False
                
            # 7. 데이터 테이블 또는 '데이터 없음' 메시지 대기
            # try:
            #     # 먼저 '데이터 없음' 메시지 확인
            #     no_data = self.wait_for_element(
            #         By.CSS_SELECTOR,
            #         "td.nodata",
            #         timeout=3  # 짧은 타임아웃으로 빠르게 확인
            #     )
            #     if no_data and "데이터가 없습니다" in no_data.text:
            #         self.logger.info("해당 기간의 데이터가 없습니다.")
            #         return False
            # except:
            #     # '데이터 없음' 메시지가 없으면 정상적인 데이터 테이블 확인
            #     data_element = self.wait_for_element(
            #         By.CSS_SELECTOR,
            #         "#contents > table > tbody > tr:nth-child(4) > td:nth-child(2)"
            #     )
            #     if not data_element:
            #         self.logger.error("데이터 테이블 로딩 실패")
            #         return False
                
            self.logger.info("분기 데이터 선택 및 조회 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"분기 데이터 선택 중 오류 발생: {str(e)}")
            return False
            
    def get_item_detail(self, stock_code: str, year: int = None, quarter: int = None):
        """
        특정 종목의 상세 정보 조회
        
        Args:
            stock_code (str): 조회할 종목 코드
            year (int): 조회할 연도 (None이면 기존 설정값 사용)
            quarter (int): 조회할 분기 (None이면 연간 데이터)
            
        Returns:
            dict: 추출된 데이터 또는 실패 시 None
        """
        # 연도와 분기 설정
        if year is not None:
            self.year = year
        if quarter is not None:
            self.quarter = quarter
        if self.debug_mode:
            self.logger.info(f"[디버그 모드] 종목 {stock_code} 상세정보 조회 시작")
        
        self._wait_debug_step("페이지 로딩", 2)
        
        # 현재 페이지 확인
        current_url = self.driver.current_url
        self.logger.info(f"현재 페이지: {current_url}")
        
        # 로그인 페이지로 돌아간 경우 재로그인
        if current_url == "https://www.fnguide.com/home/login":
            self.logger.info("로그인 페이지로 이동. 로그인 프로세스 재시작.")
            if not self.login():
                self.logger.error("로그인 실패. 프로세스 종료.")
                return None
        # 올바른 검색 페이지가 아닌 경우 이동
        elif ITEM_DETAIL_URL not in current_url:
            self.logger.info(f"검색 페이지가 아닙니다. 올바른 페이지로 이동 중...")
            self.get_page(ITEM_DETAIL_URL)
            time.sleep(2)  # 페이지 로딩 대기
                
        try:
            # 1. 종목 검색
            self._wait_debug_step("검색창 입력", 2)
            search_input = self._search_stock(stock_code)
            if not search_input:
                return None
            
            # 2. 데이터 선택 (연간/분기) - 먼저 연간/분기 선택
            if self.quarter is None:
                if not self.select_annual_data():
                    return None
            else:
                if not self.select_quarter_data():
                    return None
            
            # 3. 연도/분기 선택 - 연간/분기 선택 후 연도 선택
            if not self._check_branch():
                self.logger.error("연도/분기 선택 실패")
                return None
            
            # 3. 콘텐츠 로딩 대기
            self._wait_debug_step("콘텐츠 로딩", 2)
            if not self._wait_for_content_load():
                return None
                
            # 4. 데이터 추출
            self._wait_debug_step("데이터 추출", 2)
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            stock_name = search_input.get_attribute('value')
            # 5. 데이터 저장
            self._wait_debug_step("데이터 저장", 2)
            data = self._extract_stock_data(soup, stock_code, stock_name)
            print("stock_name: ", stock_name)
            print(f"data: {data}")
            if data:
                return data
            return None

        except Exception as e:
            self.logger.error(f"종목 {stock_code} 데이터 추출 실패: {str(e)}")
            return None
            
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
                # 1. 로그인 페이지로 이동
                self.logger.info("로그인 페이지로 이동 중...")
                if not self.get_page(LOGIN_URL):
                    self.logger.error("로그인 페이지 이동 실패")
                    return False
                
                # 2. 페이지 로딩 대기
                time.sleep(2)
                
                # 3. ID 입력 필드 찾기
                self.logger.info("ID 입력 필드 찾는 중...")
                id_field = self.wait_for_element(
                    By.CSS_SELECTOR,
                    SELECTORS['login']['id_field'],
                    timeout=10
                )
                if not id_field:
                    self.logger.error("ID 입력 필드를 찾을 수 없습니다.")
                    return False
                
                self._wait_debug_step("ID 입력")
                # id_field.clear()
                id_field.send_keys(str(USERNAME))
                
                # 4. 비밀번호 입력 필드 찾기
                self.logger.info("비밀번호 입력 필드 찾는 중...")
                pw_field = self.wait_for_element(
                    By.CSS_SELECTOR, 
                    SELECTORS['login']['pw_field'],
                    timeout=10
                )
                if not pw_field:
                    self.logger.error("비밀번호 입력 필드를 찾을 수 없습니다.")
                    return False
                
                self._wait_debug_step("비밀번호 입력")
                pw_field.clear()
                pw_field.send_keys(PASSWORD + Keys.RETURN)  # 비밀번호 입력 후 Enter 키 입력
                
                # 5. 로그인 버튼 클릭
                self.logger.info("로그인 버튼 찾는 중...")
                submit_button = self.wait_for_element(
                    By.CSS_SELECTOR,
                    SELECTORS['login']['submit_button'],
                    timeout=10
                )
                if not submit_button:
                    self.logger.error("로그인 버튼을 찾을 수 없습니다.")
                    return False
                
                self._wait_debug_step("로그인 버튼 클릭")
                submit_button.click()
                
                # 6. 로그인 완료 대기
                self.logger.info("로그인 처리 대기 중...")
                time.sleep(5)  # 로그인 처리 대기 시간 증가
                
                # 7. 로그인 성공 확인
                current_url = self.driver.current_url
                self.logger.info(f"로그인 후 현재 URL: {current_url}")
                
                # 로그인 페이지에 여전히 있는지 확인
                if "login" in current_url.lower():
                    self.logger.error("로그인 실패 - 여전히 로그인 페이지에 있음")
                    return False
                
                self.logger.info("로그인 성공 확인됨")
                
                # 8. 로그인 후 검색 페이지로 이동
                self.logger.info("검색 페이지로 이동 중...")
                if not self.get_page(ITEM_DETAIL_URL):
                    self.logger.error("검색 페이지 이동 실패")
                    return False
                time.sleep(2)  # 페이지 로딩 대기
                
                return True
                
            except Exception as e:
                self.logger.error(f"로그인 프로세스 중 오류 발생: {str(e)}")
                return False
                
        self._wait_debug_step("로그인 시도")
        
        result = login_process()
        return result
            
    def _check_branch(self):
        """분기 선택 확인 및 처리"""
        try:
            # 설정된 분기 value 값 가져오기
            self.quarter_value = self._get_quarter_value()
            self.logger.info(f"선택할 기간: {self.quarter_value}")
            
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
            time.sleep(0.5)  # 드롭다운 열림 대기
            
            # 해당 value를 가진 옵션 선택
            option_selector = f"#selGsYm > option[value='{self.quarter_value}']"
            self.logger.info(f"옵션 선택자: {option_selector}")
            
            target_option = self.wait_for_element(
                By.CSS_SELECTOR,
                option_selector,
                timeout=5
            )
            if not target_option:
                # 사용 가능한 옵션들을 확인
                available_options = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "#selGsYm > option"
                )
                available_values = [opt.get_attribute('value') for opt in available_options]
                self.logger.error(f"기간 옵션을 찾을 수 없습니다. (value: {self.quarter_value})")
                self.logger.error(f"사용 가능한 옵션들: {available_values}")
                return False
                
            # 옵션 선택
            target_option.click()
            time.sleep(0.5)  # 옵션 선택 대기
            
            # 드롭다운 닫기 (다른 요소 클릭)
            self.driver.find_element(By.TAG_NAME, "body").click()
            time.sleep(0.5)  # 드롭다운 닫힘 대기
            
            # 조회 버튼 클릭
            quarter_submit = self.wait_for_element(
                By.CSS_SELECTOR,
                SELECTORS['login']['quarter_submit']
            )
            if not quarter_submit:
                self.logger.error("조회 버튼을 찾을 수 없습니다.")
                return False
                
            quarter_submit.click()
            time.sleep(REQUEST_DELAY)  # 페이지 로딩 대기
            
            self.logger.info(f"기간 선택 완료: {self.quarter_value}")
            return True
            
        except Exception as e:
            self.logger.error(f"기간 선택 중 오류 발생: {str(e)}")
            return False

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