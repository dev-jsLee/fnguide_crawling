import os
from src.crawler.fnguide import FnGuideCrawler
import logging
from datetime import datetime
from config.config import (
    CRAWLER_CONFIG, 
    FILE_PATHS, 
    LOGGING_CONFIG, 
    CSV_CONFIG,
    QUARTER_CONFIG,
    LOGIN_URL
)
import csv

def setup_logging():
    """로깅 설정"""
    log_dir = FILE_PATHS['log_dir']
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, f'crawler_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    logging.basicConfig(
        level=getattr(logging, LOGGING_CONFIG['level']),
        format=LOGGING_CONFIG['format'],
        handlers=[
            logging.FileHandler(log_file, encoding=LOGGING_CONFIG['encoding']),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def read_stock_codes(file_path=FILE_PATHS['stock_codes']):
    """종목코드 파일 읽기"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 빈 줄 제거하고 공백 제거
            codes = [line.strip() for line in f.readlines() if line.strip()]
        return codes
    except Exception as e:
        print(f"종목코드 파일 읽기 실패: {str(e)}")
        return []

def save_data_to_csv(data, file_name, is_first=False):
    """데이터를 CSV 파일에 저장"""
    try:
        mode = 'w' if is_first else 'a'
        header = is_first
        
        with open(file_name, mode=mode, newline='', encoding=CSV_CONFIG['encoding']) as file:
            writer = csv.writer(file)
            if header:
                writer.writerow(CSV_CONFIG['columns'])
            
            value = data.values()
            writer.writerow("None" if value is None else value)
        return True
    except Exception as e:
        print(f"데이터 저장 실패: {str(e)}")
        return False

def main():
    logger = setup_logging()
    logger.info("크롤링 시작")
    
    # 종목코드 읽기
    stock_codes = read_stock_codes()
    if not stock_codes:
        logger.error("종목코드가 없습니다.")
        return
        
    logger.info(f"총 {len(stock_codes)}개의 종목코드를 읽었습니다.")
    
    # 분기 설정
    year = None
    quarter = None
    
    # 첫 번째 종목에 대해서만 분기 입력 받기
    if stock_codes:
        try:
            user_input = input(QUARTER_CONFIG['input_prompt'])
            year, quarter = map(int, user_input.strip().split())
            
            if not (2000 <= year <= 2100):
                logger.error("연도는 2000년부터 2100년 사이여야 합니다.")
                return
                
            if not (1 <= quarter <= 4):
                logger.error("분기는 1부터 4 사이여야 합니다.")
                return
                
        except ValueError:
            logger.error(f"올바른 형식으로 입력해주세요. 예: {QUARTER_CONFIG['input_format']}")
            return
        except Exception as e:
            logger.error(f"입력 중 오류가 발생했습니다: {str(e)}")
            return
    
    # 크롤러 초기화
    crawler = FnGuideCrawler(
        headless=CRAWLER_CONFIG['headless'],
        debug_mode=CRAWLER_CONFIG['debug_mode'],
        skip_step=CRAWLER_CONFIG['skip_step'],
        year=year,
        quarter=quarter
    )
    
    try:
        # 로그인
        crawler.get_page(LOGIN_URL)
        if not crawler.login():
            logger.error("로그인 실패")
            return
            
        logger.info("로그인 성공")
        
        # CSV 파일명 생성
        file_name = f'{datetime.now().strftime("%Y%m%d")}_{crawler.quarter_value}.csv'
        is_first = True
        
        # 각 종목별로 데이터 수집
        for idx, code in enumerate(stock_codes, 1):
            logger.info(f"[{idx}/{len(stock_codes)}] 종목 {code} 데이터 수집 시작")
            data = None # 데이터 초기화
            logger.info(f"종목 {code} 데이터 수집 시작")
            try:
                # 데이터 추출, 만약 없으면 None 반환
                data = crawler.get_item_detail(code)
                if data:
                    logger.info(f"종목 {code} 데이터 수집 완료")
                    # 데이터를 즉시 파일에 저장
                    if save_data_to_csv(data, file_name, is_first):
                        logger.info(f"종목 {code} 데이터 저장 완료")
                        is_first = False
                    else:
                        logger.error(f"종목 {code} 데이터 저장 실패")
                else:
                    logger.error(f"종목 {code} 데이터 수집 실패")
            except Exception as e:
                logger.error(f"종목 {code} 처리 중 오류 발생: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"크롤링 중 오류 발생: {str(e)}")
    finally:
        crawler.close()
        logger.info("크롤링 종료")

if __name__ == "__main__":
    main() 