"""
크롤러 서비스 모듈
공통 크롤링 워크플로우 및 비즈니스 로직 제공
"""
import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from bs4 import BeautifulSoup

from src.crawler.fnguide import FnGuideCrawler
from src.utils.logging_utils import LoggerManager
from src.utils.file_utils import FileManager


class CrawlingMode(Enum):
    """크롤링 모드"""
    QUARTERLY = "quarterly"  # 분기별
    ANNUAL = "annual"       # 연간


class CrawlerService:
    """크롤러 서비스 클래스"""
    
    def __init__(
        self,
        headless: bool = True,
        debug_mode: bool = False,
        skip_step: bool = False,
        log_dir: str = "logs",
        encoding: str = "utf-8"
    ):
        self.headless = headless
        self.debug_mode = debug_mode
        self.skip_step = skip_step
        self.encoding = encoding
        
        # 매니저 초기화
        self.logger_manager = LoggerManager(log_dir)
        self.file_manager = FileManager(encoding)
        self.logger = None
        self.crawler = None
    
    def setup_logger(self, log_prefix: str = "crawler") -> logging.Logger:
        """로거 설정"""
        self.logger = self.logger_manager.setup_logger(
            name=__name__,
            log_file_prefix=log_prefix
        )
        return self.logger
    
    def initialize_crawler(
        self, 
        year: int, 
        quarter: Optional[int] = None
    ) -> bool:
        """
        크롤러 초기화
        
        Args:
            year: 연도
            quarter: 분기 (연간 데이터의 경우 None)
            
        Returns:
            초기화 성공 여부
        """
        try:
            self.crawler = FnGuideCrawler(
                headless=self.headless,
                debug_mode=self.debug_mode,
                skip_step=self.skip_step,
                year=year,
                quarter=quarter
            )
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"크롤러 초기화 실패: {str(e)}")
            return False
    
    def login(self, login_url: str) -> bool:
        """
        로그인 수행
        
        Args:
            login_url: 로그인 URL
            
        Returns:
            로그인 성공 여부
        """
        if not self.crawler:
            if self.logger:
                self.logger.error("크롤러가 초기화되지 않았습니다.")
            return False
        
        try:
            self.crawler.get_page(login_url)
            success = self.crawler.login()
            
            if self.logger:
                if success:
                    self.logger.info("로그인 성공")
                else:
                    self.logger.error("로그인 실패")
            
            return success
        except Exception as e:
            if self.logger:
                self.logger.error(f"로그인 중 오류 발생: {str(e)}")
            return False
    
    def crawl_stock_data(
        self,
        stock_codes: List[str],
        mode: CrawlingMode,
        csv_columns: List[str],
        item_detail_url: Optional[str] = None
    ) -> Tuple[str, int, int]:
        """
        종목 데이터 크롤링
        
        Args:
            stock_codes: 종목코드 리스트
            mode: 크롤링 모드 (분기/연간)
            csv_columns: CSV 컬럼 리스트
            item_detail_url: 종목 상세 URL (연간 모드에서 필요)
            
        Returns:
            (파일명, 성공 개수, 실패 개수)
        """
        if not self.crawler or not self.logger:
            raise ValueError("크롤러 또는 로거가 초기화되지 않았습니다.")
        
        # CSV 파일명 생성
        if mode == CrawlingMode.QUARTERLY:
            file_name = f'{datetime.now().strftime("%Y%m%d")}_{self.crawler.quarter_value}.csv'
            log_prefix = "분기"
        else:
            file_name = f'{datetime.now().strftime("%Y%m%d")}_year.csv'
            log_prefix = "연간"
        
        self.logger.info(f"{log_prefix} 데이터 크롤링 시작")
        self.logger.info(f"총 {len(stock_codes)}개의 종목코드를 처리합니다.")
        
        success_count = 0
        failure_count = 0
        is_first = True
        
        for idx, code in enumerate(stock_codes, 1):
            self.logger.info(f"[{idx}/{len(stock_codes)}] 종목 {code} {log_prefix} 데이터 수집 시작")
            
            try:
                data = None
                
                if mode == CrawlingMode.ANNUAL:
                    # 연간 데이터 처리
                    data = self._crawl_annual_data(code, item_detail_url)
                else:
                    # 분기 데이터 처리
                    data = self._crawl_quarterly_data(code, item_detail_url)
                
                # 데이터 저장
                if self._save_crawled_data(data, file_name, csv_columns, is_first, code):
                    success_count += 1
                    self.logger.info(f"종목 {code} 데이터 처리 완료")
                else:
                    failure_count += 1
                    self.logger.error(f"종목 {code} 데이터 저장 실패")
                
                is_first = False
                
            except Exception as e:
                failure_count += 1
                self.logger.error(f"종목 {code} 처리 중 오류 발생: {str(e)}")
                continue
        
        self.logger.info(f"{log_prefix} 데이터 크롤링 완료 - 성공: {success_count}, 실패: {failure_count}")
        return file_name, success_count, failure_count
    
    def _crawl_annual_data(self, code: str, item_detail_url: str) -> Optional[Dict[str, Any]]:
        """연간 데이터 크롤링"""
        try:
            self.logger.info(f"종목 {code} 연간 데이터 크롤링 시작")
            
            # 1. 검색창 페이지로 이동
            self.logger.info(f"검색 페이지로 이동: {item_detail_url}")
            if not self.crawler.get_page(item_detail_url):
                self.logger.error(f"종목 {code} 검색 페이지 이동 실패")
                return None
            
            # 페이지 로딩 대기
            time.sleep(2)
            
            # 2. 종목코드 검색
            self.logger.info(f"종목 {code} 검색 시작")
            search_input = self.crawler._search_stock(code)
            if not search_input:
                self.logger.error(f"종목 {code} 검색 실패")
                return None
            
            # 검색 결과 로딩 대기
            time.sleep(1)
            
            # 3. 연간 데이터 선택 및 조회
            self.logger.info(f"종목 {code} 연간 데이터 선택")
            if not self.crawler.select_annual_data():
                self.logger.error(f"종목 {code} 연간 데이터 선택 실패")
                return {
                    'stock_code': code,
                    'stock_name': None,
                    'sales': None,
                    'operating_profit': None
                }
            
            # 연간 데이터 조회 결과 로딩 대기
            time.sleep(2)
            
            # 4. 콘텐츠 로딩 대기
            self.logger.info(f"종목 {code} 데이터 로딩 대기")
            if not self.crawler._wait_for_content_load():
                self.logger.error(f"종목 {code} 콘텐츠 로딩 실패")
                return None
            
            # 5. 데이터 추출 (get_item_detail 대신 직접 추출)
            self.logger.info(f"종목 {code} 데이터 추출 시작")
            soup = BeautifulSoup(self.crawler.driver.page_source, 'lxml')
            stock_name = search_input.get_attribute('value') if search_input else code
            
            # 데이터 추출
            data = self.crawler._extract_stock_data(soup, code, stock_name)
            
            if data:
                self.logger.info(f"종목 {code} 연간 데이터 추출 성공: {data}")
            else:
                self.logger.warning(f"종목 {code} 연간 데이터 추출 실패 또는 데이터 없음")
                # 데이터가 없어도 기본 구조는 반환
                data = {
                    'stock_code': code,
                    'stock_name': stock_name,
                    'sales': None,
                    'operating_profit': None
                }
            
            return data
            
        except Exception as e:
            self.logger.error(f"종목 {code} 연간 데이터 크롤링 중 오류: {str(e)}")
            return None
    
    def _crawl_quarterly_data(self, code: str, item_detail_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """분기 데이터 크롤링"""
        try:
            self.logger.info(f"종목 {code} 분기 데이터 크롤링 시작")
            
            # 분기 데이터의 경우 각 종목마다 검색 페이지로 이동
            if item_detail_url:
                self.logger.info(f"검색 페이지로 이동: {item_detail_url}")
                if not self.crawler.get_page(item_detail_url):
                    self.logger.error(f"종목 {code} 검색 페이지 이동 실패")
                    return None
                
                # 페이지 로딩 대기
                time.sleep(1)
                self.logger.info(f"검색 페이지 로딩 완료")
            
            # 기존 get_item_detail 메서드 사용 (내부적으로 검색 및 분기 선택 처리)
            self.logger.info(f"종목 {code} 데이터 추출 시작")
            data = self.crawler.get_item_detail(code)
            
            if data:
                self.logger.info(f"종목 {code} 데이터 추출 성공: {data}")
            else:
                self.logger.warning(f"종목 {code} 데이터 추출 실패 또는 데이터 없음")
            
            return data
            
        except Exception as e:
            self.logger.error(f"종목 {code} 분기 데이터 크롤링 중 오류: {str(e)}")
            return None
    
    def _save_crawled_data(
        self,
        data: Optional[Dict[str, Any]],
        file_name: str,
        csv_columns: List[str],
        is_first: bool,
        stock_code: str
    ) -> bool:
        """크롤링된 데이터 저장"""
        try:
            if not data:
                # 데이터가 없는 경우 기본값으로 저장
                data = {
                    'stock_code': stock_code,
                    'stock_name': None,
                    'sales': None,
                    'operating_profit': None
                }
            
            return self.file_manager.save_data_to_csv(
                data, file_name, csv_columns, is_first
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"데이터 저장 중 오류: {str(e)}")
            return False
    
    def get_user_input_quarterly(self) -> Tuple[Optional[int], Optional[int]]:
        """분기 정보 사용자 입력 받기"""
        try:
            user_input = input("연도와 분기를 입력하세요 (예: 2024 3): ")
            year, quarter = map(int, user_input.strip().split())
            
            if not (2000 <= year <= 2100):
                if self.logger:
                    self.logger.error("연도는 2000년부터 2100년 사이여야 합니다.")
                return None, None
            
            if not (1 <= quarter <= 4):
                if self.logger:
                    self.logger.error("분기는 1부터 4 사이여야 합니다.")
                return None, None
            
            return year, quarter
            
        except ValueError:
            if self.logger:
                self.logger.error("올바른 형식으로 입력해주세요. 예: 2024 3")
            return None, None
        except Exception as e:
            if self.logger:
                self.logger.error(f"입력 중 오류가 발생했습니다: {str(e)}")
            return None, None
    
    def get_user_input_annual(self) -> Optional[int]:
        """연도 정보 사용자 입력 받기"""
        try:
            year = int(input("연도를 입력하세요 (예: 2024): "))
            
            if not (2000 <= year <= 2100):
                if self.logger:
                    self.logger.error("연도는 2000년부터 2100년 사이여야 합니다.")
                return None
            
            return year
            
        except ValueError:
            if self.logger:
                self.logger.error("올바른 연도를 입력해주세요.")
            return None
        except Exception as e:
            if self.logger:
                self.logger.error(f"입력 중 오류가 발생했습니다: {str(e)}")
            return None
    
    def close(self):
        """리소스 정리"""
        if self.crawler:
            self.crawler.close()
            if self.logger:
                self.logger.info("크롤링 종료") 