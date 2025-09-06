from PyQt5.QtCore import QThread, pyqtSignal
from src.crawler.fnguide import FnGuideCrawler
from config.config import USERNAME, PASSWORD
import logging
from datetime import datetime
import os
import pandas as pd

class FnGuideWorker(QThread):
    log_signal = pyqtSignal(str)      # 로그 시그널
    data_signal = pyqtSignal(dict)    # 데이터 시그널
    finished_signal = pyqtSignal()    # 완료 시그널
    error_signal = pyqtSignal(str)    # 에러 시그널
    
    def __init__(self, stock_codes, year, quarter, headless=True, debug_mode=False):
        super().__init__()
        self.stock_codes = stock_codes
        self.year = year
        self.quarter = quarter
        self.headless = headless
        self.debug_mode = debug_mode
        self.is_running = True
        self.crawler = None
        
    def run(self):
        try:
            # 크롤러 초기화
            self.log_signal.emit("크롤러 초기화 중...")
            self.crawler = FnGuideCrawler(
                headless=self.headless,
                debug_mode=self.debug_mode,  # GUI에서 설정한 디버그 모드 사용
                skip_step=0,
                year=self.year,
                quarter=self.quarter
            )
            
            # 로그인
            self.log_signal.emit("로그인 시도 중...")
            if not self.crawler.login():
                self.error_signal.emit("로그인 실패")
                return
            self.log_signal.emit("로그인 성공")
            
            # 데이터 타입 확인
            if self.quarter is None:
                data_type = "연간"
            else:
                data_type = f"{self.quarter}분기"
            
            self.log_signal.emit(f"{data_type} 데이터 크롤링을 시작합니다...")
            self.log_signal.emit(f"설정된 연도: {self.year}, 분기: {self.quarter}")
            
            # 각 종목별로 데이터 수집
            total = len(self.stock_codes)
            success_count = 0
            failure_count = 0
            
            for idx, code in enumerate(self.stock_codes, 1):
                if not self.is_running:
                    self.log_signal.emit("크롤링이 중단되었습니다.")
                    break
                    
                self.log_signal.emit(f"[{idx}/{total}] 종목 {code} {data_type} 데이터 수집 시작")
                
                try:
                    # FnGuideCrawler를 통한 데이터 수집
                    data = self.crawler.get_item_detail(code, year=self.year, quarter=self.quarter)
                    
                    if data:
                        success_count += 1
                        self.log_signal.emit(f"종목 {code} 데이터 수집 성공")
                        # 데이터 시그널 발생
                        self.data_signal.emit(data)
                    else:
                        failure_count += 1
                        self.log_signal.emit(f"종목 {code} 데이터 수집 실패 또는 데이터 없음")
                        
                except Exception as e:
                    failure_count += 1
                    self.log_signal.emit(f"종목 {code} 처리 중 오류 발생: {str(e)}")
                
                # 진행률 업데이트 (간단한 로그로 표시)
                progress = int((idx / total) * 100)
                self.log_signal.emit(f"진행률: {progress}%")
            
            self.log_signal.emit(f"{data_type} 데이터 크롤링이 완료되었습니다.")
            self.log_signal.emit(f"성공: {success_count}개, 실패: {failure_count}개")
            self.finished_signal.emit()
            
        except Exception as e:
            self.error_signal.emit(f"크롤링 중 오류 발생: {str(e)}")
        finally:
            if self.crawler:
                self.crawler.close()
    
    def stop(self):
        self.is_running = False
