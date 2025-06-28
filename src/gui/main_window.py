import sys
import re
import json
import os
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QProgressBar,
    QTextEdit, QFileDialog, QSpinBox, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QSettings
from .crawler_worker import CrawlerWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FnGuide 크롤러")
        self.setMinimumSize(500, 800)  # 가로 크기를 1000에서 500으로 반으로 줄임
        
        # 설정 파일 경로
        self.settings_file = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'window_settings.json')
        
        # 창 크기와 위치 복원
        self.restore_window_state()
        
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
        period_layout = QVBoxLayout()
        
        # 연간/분기 선택 라디오 버튼
        period_type_layout = QHBoxLayout()
        self.annual_radio = QPushButton("연간 데이터")
        self.quarterly_radio = QPushButton("분기 데이터")
        self.annual_radio.setCheckable(True)
        self.quarterly_radio.setCheckable(True)
        self.annual_radio.setChecked(True)  # 기본값: 연간
        
        # 버튼 스타일 설정
        self.annual_radio.setStyleSheet("""
            QPushButton:checked { background-color: #0078d4; color: white; }
            QPushButton { padding: 5px 10px; }
        """)
        self.quarterly_radio.setStyleSheet("""
            QPushButton:checked { background-color: #0078d4; color: white; }
            QPushButton { padding: 5px 10px; }
        """)
        
        period_type_layout.addWidget(QLabel("데이터 유형:"))
        period_type_layout.addWidget(self.annual_radio)
        period_type_layout.addWidget(self.quarterly_radio)
        period_type_layout.addStretch()
        period_layout.addLayout(period_type_layout)
        
        # 연도/분기 입력 영역
        period_input_layout = QHBoxLayout()
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2000, 2100)
        self.year_spin.setValue(2024)
        self.quarter_combo = QComboBox()
        self.quarter_combo.addItems(["1분기", "2분기", "3분기", "4분기"])
        self.quarter_combo.setEnabled(False)  # 기본적으로 비활성화
        
        period_input_layout.addWidget(QLabel("연도:"))
        period_input_layout.addWidget(self.year_spin)
        period_input_layout.addWidget(QLabel("분기:"))
        period_input_layout.addWidget(self.quarter_combo)
        period_input_layout.addStretch()
        period_layout.addLayout(period_input_layout)
        
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
        self.annual_radio.clicked.connect(self.on_annual_selected)
        self.quarterly_radio.clicked.connect(self.on_quarterly_selected)
    
    def restore_window_state(self):
        """저장된 창 크기와 위치 복원"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # 창 크기 복원
                if 'width' in settings and 'height' in settings:
                    self.resize(settings['width'], settings['height'])
                else:
                    self.resize(800, 900)  # 기본 크기 (가로를 줄임)
                
                # 창 위치 복원
                if 'x' in settings and 'y' in settings:
                    self.move(settings['x'], settings['y'])
                    
            else:
                # 설정 파일이 없으면 기본 크기로 설정
                self.resize(800, 900)
                
        except Exception as e:
            # 오류 발생 시 기본 크기로 설정
            self.resize(800, 900)
            print(f"창 설정 복원 실패: {e}")
    
    def save_window_state(self):
        """현재 창 크기와 위치 저장"""
        try:
            # 설정 디렉토리 생성
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            settings = {
                'width': self.width(),
                'height': self.height(),
                'x': self.x(),
                'y': self.y()
            }
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            print(f"창 설정 저장 실패: {e}")
    
    def closeEvent(self, event):
        """프로그램 종료 시 창 설정 저장"""
        self.save_window_state()
        
        # 크롤링이 진행 중이면 중지
        if self.crawler_worker and self.crawler_worker.isRunning():
            self.crawler_worker.stop()
            self.crawler_worker.wait()  # 작업 완료까지 대기
        
        event.accept()
    
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
        
        # 연간/분기 선택에 따른 처리
        if self.annual_radio.isChecked():
            quarter = None  # 연간 데이터
            data_type = "연간"
        else:
            quarter = self.quarter_combo.currentIndex() + 1  # 분기 데이터
            data_type = f"{quarter}분기"
        
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
        self.log_text.append(f"{data_type} 데이터 크롤링을 시작합니다...")
        self.log_text.append(f"대상 종목: {len(stock_codes)}개")
        
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
        
        # 데이터 유형 확인
        if self.annual_radio.isChecked():
            data_type = "연간"
        else:
            quarter = self.quarter_combo.currentIndex() + 1
            data_type = f"{quarter}분기"
            
        self.log_text.append(f"{data_type} 데이터 크롤링이 완료되었습니다.")
        self.log_text.append(f"총 {len(self.current_data)}개의 데이터가 수집되었습니다.")
    
    def crawling_error(self, error_message):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        QMessageBox.critical(self, "오류", error_message)
        self.log_text.append(f"오류 발생: {error_message}")
    
    def on_annual_selected(self):
        """연간 데이터 선택 시"""
        if self.annual_radio.isChecked():
            self.quarterly_radio.setChecked(False)
            self.quarter_combo.setEnabled(False)
    
    def on_quarterly_selected(self):
        """분기 데이터 선택 시"""
        if self.quarterly_radio.isChecked():
            self.annual_radio.setChecked(False)
            self.quarter_combo.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 