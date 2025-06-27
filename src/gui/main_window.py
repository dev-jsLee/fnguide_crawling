import sys
import re
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QProgressBar,
    QTextEdit, QFileDialog, QSpinBox, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from .crawler_worker import CrawlerWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FnGuide 크롤러")
        self.setMinimumSize(1000, 800)
        
        # 크롤러 작업자 초기화
        self.crawler_worker = None
        self.current_data = []  # 현재까지 수집된 데이터 저장
        
        # 메인 위젯과 레이아웃 설정
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 종목코드 입력 영역
        stock_code_layout = QHBoxLayout()
        self.stock_code_input = QLineEdit()
        self.stock_code_input.setPlaceholderText("종목코드를 입력하세요 (예: 005930, 035720)")
        self.file_select_btn = QPushButton("파일 선택")
        stock_code_layout.addWidget(QLabel("종목코드:"))
        stock_code_layout.addWidget(self.stock_code_input)
        stock_code_layout.addWidget(self.file_select_btn)
        layout.addLayout(stock_code_layout)
        
        # 연도/분기 선택 영역
        period_layout = QHBoxLayout()
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2000, 2100)
        self.year_spin.setValue(2024)
        self.quarter_combo = QComboBox()
        self.quarter_combo.addItems(["1분기", "2분기", "3분기", "4분기"])
        period_layout.addWidget(QLabel("연도:"))
        period_layout.addWidget(self.year_spin)
        period_layout.addWidget(QLabel("분기:"))
        period_layout.addWidget(self.quarter_combo)
        period_layout.addStretch()
        layout.addLayout(period_layout)
        
        # 크롤링 제어 버튼
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("크롤링 시작")
        self.stop_btn = QPushButton("중지")
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # 진행 상황 표시
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # 데이터 테이블
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(0)
        self.data_table.setRowCount(0)
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.data_table)
        
        # 로그 표시 영역
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)
        
        # 시그널 연결
        self.file_select_btn.clicked.connect(self.select_file)
        self.start_btn.clicked.connect(self.start_crawling)
        self.stop_btn.clicked.connect(self.stop_crawling)
    
    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "종목코드 파일 선택",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    codes = f.read().strip()
                    self.stock_code_input.setText(codes)
            except Exception as e:
                self.log_text.append(f"파일 읽기 오류: {str(e)}")
    
    def start_crawling(self):
        # 입력값 검증
        input_text = self.stock_code_input.text().strip()
        if not input_text:
            QMessageBox.warning(self, "경고", "종목코드를 입력해주세요.")
            return
        
        # 정규표현식으로 6자리 숫자 찾기
        stock_codes = re.findall(r'\d{6}', input_text)
        if not stock_codes:
            QMessageBox.warning(self, "경고", "유효한 종목코드(6자리 숫자)를 입력해주세요.")
            return
        
        year = self.year_spin.value()
        quarter = self.quarter_combo.currentIndex() + 1
        
        # 데이터 초기화
        self.current_data = []
        self.data_table.clear()
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)
        
        # 크롤러 작업자 초기화 및 시작
        self.crawler_worker = CrawlerWorker(
            stock_codes=stock_codes,
            year=year,
            quarter=quarter
        )
        self.crawler_worker.progress.connect(self.update_progress)
        self.crawler_worker.log.connect(self.update_log)
        self.crawler_worker.finished.connect(self.crawling_finished)
        self.crawler_worker.error.connect(self.crawling_error)
        self.crawler_worker.data_saved.connect(self.update_data_table)
        
        # UI 상태 업데이트
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.log_text.clear()
        
        # 크롤링 시작
        self.crawler_worker.start()
    
    def stop_crawling(self):
        if self.crawler_worker and self.crawler_worker.isRunning():
            self.crawler_worker.stop()
            self.log_text.append("크롤링 중지 요청됨...")
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def update_log(self, message):
        self.log_text.append(message)
    
    def update_data_table(self, data):
        """데이터 테이블 업데이트"""
        try:
            # 데이터 유효성 검사
            if not isinstance(data, dict):
                self.log_text.append(f"데이터 형식 오류: dict 타입이 아님 - {type(data)}: {data}")
                return
                
            # 필수 키 확인
            required_keys = ['stock_code', 'stock_name', 'sales', 'operating_profit']
            for key in required_keys:
                if key not in data:
                    self.log_text.append(f"데이터 키 누락: {key}")
                    data[key] = None  # 누락된 키에 기본값 설정
            
            # 컬럼 설정 (첫 번째 데이터 기준)
            if self.data_table.columnCount() == 0:
                columns = ['종목코드', '종목명', '매출액', '영업이익']
                self.data_table.setColumnCount(len(columns))
                self.data_table.setHorizontalHeaderLabels(columns)
            
            # 행 추가
            row = self.data_table.rowCount()
            self.data_table.insertRow(row)
            
            # 데이터 입력 (안전한 문자열 변환)
            self.data_table.setItem(row, 0, QTableWidgetItem(str(data.get('stock_code', '-'))))
            self.data_table.setItem(row, 1, QTableWidgetItem(str(data.get('stock_name', '-'))))
            self.data_table.setItem(row, 2, QTableWidgetItem(str(data.get('sales', '-') if data.get('sales') is not None else '-')))
            self.data_table.setItem(row, 3, QTableWidgetItem(str(data.get('operating_profit', '-') if data.get('operating_profit') is not None else '-')))
            
            # 테이블 스크롤을 최신 데이터로 이동
            self.data_table.scrollToBottom()
            
            # 현재 데이터 저장
            self.current_data.append(data)
            
        except Exception as e:
            self.log_text.append(f"데이터 테이블 업데이트 실패: {str(e)}")
            self.log_text.append(f"문제 데이터: {data}")
            self.log_text.append(f"데이터 타입: {type(data)}")
    
    def crawling_finished(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.log_text.append("크롤링이 완료되었습니다.")
    
    def crawling_error(self, error_message):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        QMessageBox.critical(self, "오류", error_message)
        self.log_text.append(f"오류 발생: {error_message}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 