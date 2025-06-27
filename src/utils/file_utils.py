"""
파일 유틸리티 모듈
종목코드 읽기, CSV 저장 등 파일 관련 공통 기능 제공
"""
import csv
import os
from typing import List, Dict, Any, Optional
import logging


class FileManager:
    """파일 관리 클래스"""
    
    def __init__(self, encoding: str = "utf-8"):
        self.encoding = encoding
        self.logger = logging.getLogger(__name__)
    
    def read_stock_codes(self, file_path: str) -> List[str]:
        """
        종목코드 파일 읽기
        
        Args:
            file_path: 종목코드 파일 경로
            
        Returns:
            종목코드 리스트
        """
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"종목코드 파일이 존재하지 않습니다: {file_path}")
                return []
            
            with open(file_path, 'r', encoding=self.encoding) as f:
                # 빈 줄 제거하고 공백 제거
                codes = [line.strip() for line in f.readlines() if line.strip()]
            
            self.logger.info(f"종목코드 {len(codes)}개를 읽었습니다.")
            return codes
            
        except Exception as e:
            self.logger.error(f"종목코드 파일 읽기 실패: {str(e)}")
            return []
    
    def save_data_to_csv(
        self, 
        data: Dict[str, Any], 
        file_name: str, 
        columns: List[str],
        is_first: bool = False
    ) -> bool:
        """
        데이터를 CSV 파일에 저장
        
        Args:
            data: 저장할 데이터 딕셔너리
            file_name: CSV 파일명
            columns: CSV 컬럼 리스트
            is_first: 첫 번째 데이터 여부 (헤더 작성용)
            
        Returns:
            저장 성공 여부
        """
        try:
            mode = 'w' if is_first else 'a'
            
            with open(file_name, mode=mode, newline='', encoding=self.encoding) as file:
                writer = csv.writer(file)
                
                # 헤더 작성 (첫 번째 데이터인 경우)
                if is_first:
                    writer.writerow(columns)
                
                # 데이터 작성
                if data:
                    row_data = []
                    for column in columns:
                        value = data.get(column)
                        row_data.append("None" if value is None else value)
                    writer.writerow(row_data)
                else:
                    # 데이터가 없는 경우 None으로 채움
                    writer.writerow(["None"] * len(columns))
            
            return True
            
        except Exception as e:
            self.logger.error(f"데이터 저장 실패: {str(e)}")
            return False
    
    def ensure_directory(self, directory_path: str) -> bool:
        """
        디렉토리 존재 확인 및 생성
        
        Args:
            directory_path: 디렉토리 경로
            
        Returns:
            생성 성공 여부
        """
        try:
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
                self.logger.info(f"디렉토리 생성: {directory_path}")
            return True
        except Exception as e:
            self.logger.error(f"디렉토리 생성 실패: {str(e)}")
            return False


# 편의 함수들 (기존 코드와의 호환성을 위해)
def read_stock_codes(file_path: str, encoding: str = "utf-8") -> List[str]:
    """종목코드 파일 읽기 (편의 함수)"""
    manager = FileManager(encoding)
    return manager.read_stock_codes(file_path)


def save_data_to_csv(
    data: Dict[str, Any], 
    file_name: str, 
    columns: List[str],
    is_first: bool = False,
    encoding: str = "utf-8"
) -> bool:
    """CSV 저장 (편의 함수)"""
    manager = FileManager(encoding)
    return manager.save_data_to_csv(data, file_name, columns, is_first) 