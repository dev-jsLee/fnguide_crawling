from PyQt6.QtCore import QThread, pyqtSignal
from src.core.crawler_service import CrawlerService, CrawlingMode
from config.config import (
    CRAWLER_CONFIG, 
    CSV_CONFIG,
    LOGIN_URL,
    ITEM_DETAIL_URL
)
import logging
from datetime import datetime
import os

class CrawlerWorker(QThread):
    progress = pyqtSignal(int)  # 진행률 시그널
    log = pyqtSignal(str)      # 로그 시그널
    finished = pyqtSignal()    # 완료 시그널
    error = pyqtSignal(str)    # 에러 시그널
    data_saved = pyqtSignal(dict)  # 데이터 저장 완료 시그널
    
    def __init__(self, stock_codes, year, quarter, user_id=None, password=None):
        super().__init__()
        self.stock_codes = stock_codes
        self.year = year
        self.quarter = quarter
        self.is_running = True
        
        # 파일명 생성 (연간/분기에 따라 다르게)
        if quarter is None:
            self.file_name = f'{datetime.now().strftime("%Y%m%d")}_연간.csv'
            self.mode = CrawlingMode.ANNUAL
        else:
            self.file_name = f'{datetime.now().strftime("%Y%m%d")}_{quarter}분기.csv'
            self.mode = CrawlingMode.QUARTERLY
            
        self.is_first = True
        self.service = None
        
    def run(self):
        try:
            # 크롤러 서비스 초기화
            self.service = CrawlerService(
                headless=CRAWLER_CONFIG['headless'],
                debug_mode=CRAWLER_CONFIG['debug_mode'],
                skip_step=CRAWLER_CONFIG['skip_step'],
                log_dir='logs'
            )
            
            # 로거 설정 (GUI용)
            logger = self.service.setup_logger("crawler_gui")
            
            # 크롤러 초기화
            self.log.emit("크롤러 초기화 중...")
            if not self.service.initialize_crawler(self.year, self.quarter):
                self.error.emit("크롤러 초기화 실패")
                return
            
            # 로그인
            self.log.emit("로그인 시도 중...")
            if not self.service.login(LOGIN_URL):
                self.error.emit("로그인 실패")
                return
            self.log.emit("로그인 성공")
            
            # 데이터 타입 확인
            if self.mode == CrawlingMode.ANNUAL:
                data_type = "연간"
            else:
                data_type = f"{self.quarter}분기"
            
            self.log.emit(f"{data_type} 데이터 크롤링을 시작합니다...")
            
            # 각 종목별로 데이터 수집
            total = len(self.stock_codes)
            success_count = 0
            failure_count = 0
            
            for idx, code in enumerate(self.stock_codes, 1):
                if not self.is_running:
                    self.log.emit("크롤링이 중단되었습니다.")
                    break
                    
                self.log.emit(f"[{idx}/{total}] 종목 {code} {data_type} 데이터 수집 시작")
                
                try:
                    # CrawlerService를 통한 데이터 수집
                    if self.mode == CrawlingMode.ANNUAL:
                        data = self.service._crawl_annual_data(code, ITEM_DETAIL_URL)
                    else:
                        data = self.service._crawl_quarterly_data(code, ITEM_DETAIL_URL)
                    
                    if data:
                        # 데이터 유효성 검사 및 저장
                        if self.save_data_to_csv(data):
                            success_count += 1
                            self.log.emit(f"종목 {code} 데이터 저장 완료")
                            # 데이터 저장 완료 시그널 발생
                            self.data_saved.emit(data)
                        else:
                            failure_count += 1
                            self.log.emit(f"종목 {code} 데이터 저장 실패")
                    else:
                        failure_count += 1
                        self.log.emit(f"종목 {code} 데이터 수집 실패")
                        
                except Exception as e:
                    failure_count += 1
                    self.log.emit(f"종목 {code} 처리 중 오류 발생: {str(e)}")
                
                # 진행률 업데이트
                progress = int((idx / total) * 100)
                self.progress.emit(progress)
            
            self.log.emit(f"{data_type} 데이터 크롤링이 완료되었습니다.")
            self.log.emit(f"성공: {success_count}개, 실패: {failure_count}개")
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(f"크롤링 중 오류 발생: {str(e)}")
        finally:
            if self.service:
                self.service.close()
    
    def save_data_to_csv(self, data):
        """데이터를 CSV 파일에 저장"""
        try:
            if not isinstance(data, dict):
                self.log.emit(f"CSV 저장 오류: 데이터가 dict 타입이 아님 - {type(data)}")
                return False
            
            # 파일 저장 로직 (기존과 동일)
            import csv
            mode = 'w' if self.is_first else 'a'
            header = self.is_first
            
            with open(self.file_name, mode=mode, newline='', encoding=CSV_CONFIG['encoding']) as file:
                writer = csv.writer(file)
                if header:
                    writer.writerow(CSV_CONFIG['columns'])
                
                # 안전한 데이터 추출
                row_data = []
                for column in CSV_CONFIG['columns']:
                    value = data.get(column, None)
                    row_data.append(value if value is not None else "")
                
                writer.writerow(row_data)
            
            self.is_first = False
            return True
        except Exception as e:
            self.log.emit(f"데이터 저장 실패: {str(e)}")
            return False
    
    def stop(self):
        self.is_running = False 