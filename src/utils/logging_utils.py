"""
로깅 유틸리티 모듈
공통 로깅 설정 및 관리 기능 제공
"""
import os
import logging
from datetime import datetime
from typing import Optional


class LoggerManager:
    """로거 관리 클래스"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """로그 디렉토리 생성"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def setup_logger(
        self, 
        name: str,
        log_file_prefix: str = "crawler",
        level: str = "INFO",
        format_string: Optional[str] = None,
        encoding: str = "utf-8"
    ) -> logging.Logger:
        """
        로거 설정
        
        Args:
            name: 로거 이름
            log_file_prefix: 로그 파일 접두사
            level: 로그 레벨
            format_string: 로그 포맷 문자열
            encoding: 파일 인코딩
            
        Returns:
            설정된 로거 객체
        """
        if format_string is None:
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # 로그 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(self.log_dir, f'{log_file_prefix}_{timestamp}.log')
        
        # 로거 생성
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        # 기존 핸들러 제거 (중복 방지)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # 파일 핸들러
        file_handler = logging.FileHandler(log_file, encoding=encoding)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_formatter = logging.Formatter(format_string)
        file_handler.setFormatter(file_formatter)
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, level.upper()))
        console_formatter = logging.Formatter(format_string)
        console_handler.setFormatter(console_formatter)
        
        # 핸들러 추가
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger


def setup_logging(
    log_dir: str = "logs",
    log_file_prefix: str = "crawler",
    level: str = "INFO",
    format_string: Optional[str] = None,
    encoding: str = "utf-8"
) -> logging.Logger:
    """
    간편한 로깅 설정 함수 (기존 코드와의 호환성을 위해)
    
    Args:
        log_dir: 로그 디렉토리
        log_file_prefix: 로그 파일 접두사
        level: 로그 레벨
        format_string: 로그 포맷 문자열
        encoding: 파일 인코딩
        
    Returns:
        설정된 로거 객체
    """
    manager = LoggerManager(log_dir)
    return manager.setup_logger(
        name=__name__,
        log_file_prefix=log_file_prefix,
        level=level,
        format_string=format_string,
        encoding=encoding
    ) 