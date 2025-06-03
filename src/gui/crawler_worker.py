from PyQt6.QtCore import QThread, pyqtSignal
from src.crawler.fnguide import FnGuideCrawler
import logging
from datetime import datetime
from config.config import CRAWLER_CONFIG, LOGIN_URL, CSV_CONFIG
import csv
import os

class CrawlerWorker(QThread):
    progress = pyqtSignal(int)  # 진행률 시그널
    log = pyqtSignal(str)      # 로그 시그널
    finished = pyqtSignal()    # 완료 시그널
    error = pyqtSignal(str)    # 에러 시그널
    data_saved = pyqtSignal(str, dict)  # 데이터 저장 완료 시그널 (파일명, 데이터)
    
    def __init__(self, stock_codes, year, quarter, user_id=None, password=None):
        super().__init__()
        self.stock_codes = stock_codes
        self.year = year
        self.quarter = quarter
        self.is_running = True
        self.file_name = f'{datetime.now().strftime("%Y%m%d")}_{quarter}분기.csv'
        self.is_first = True
        
    def save_data_to_csv(self, data):
        """데이터를 CSV 파일에 저장"""
        try:
            mode = 'w' if self.is_first else 'a'
            header = self.is_first
            
            with open(self.file_name, mode=mode, newline='', encoding=CSV_CONFIG['encoding']) as file:
                writer = csv.writer(file)
                if header:
                    writer.writerow(CSV_CONFIG['columns'])
                
                writer.writerow(data.values())
            
            self.is_first = False
            return True
        except Exception as e:
            self.log.emit(f"데이터 저장 실패: {str(e)}")
            return False
        
    def run(self):
        try:
            # 크롤러 초기화
            crawler = FnGuideCrawler(
                headless=CRAWLER_CONFIG['headless'],
                debug_mode=CRAWLER_CONFIG['debug_mode'],
                skip_step=CRAWLER_CONFIG['skip_step'],
                year=self.year,
                quarter=self.quarter
            )
            
            # 로그인
            self.log.emit("로그인 시도 중...")
            crawler.get_page(LOGIN_URL)
            if not crawler.login():
                self.error.emit("로그인 실패")
                return
            self.log.emit("로그인 성공")
            
            # 각 종목별로 데이터 수집
            total = len(self.stock_codes)
            for idx, code in enumerate(self.stock_codes, 1):
                if not self.is_running:
                    self.log.emit("크롤링이 중단되었습니다.")
                    break
                    
                self.log.emit(f"[{idx}/{total}] 종목 {code} 데이터 수집 시작")
                try:
                    data = crawler.get_item_detail(code)
                    if data:
                        # 데이터를 즉시 파일에 저장
                        if self.save_data_to_csv(data):
                            self.log.emit(f"종목 {code} 데이터 저장 완료")
                            # 데이터 저장 완료 시그널 발생
                            self.data_saved.emit(self.file_name, data)
                        else:
                            self.log.emit(f"종목 {code} 데이터 저장 실패")
                    else:
                        self.log.emit(f"종목 {code} 데이터 수집 실패")
                except Exception as e:
                    self.log.emit(f"종목 {code} 처리 중 오류 발생: {str(e)}")
                
                # 진행률 업데이트
                progress = int((idx / total) * 100)
                self.progress.emit(progress)
            
            self.log.emit("크롤링이 완료되었습니다.")
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(f"크롤링 중 오류 발생: {str(e)}")
        finally:
            if 'crawler' in locals():
                crawler.close()
    
    def stop(self):
        self.is_running = False 