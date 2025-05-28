import os
from src.crawler.fnguide import FnGuideCrawler
import logging
from datetime import datetime
from src.config.config import CRAWLER_CONFIG, FILE_PATHS, LOGGING_CONFIG, CSV_CONFIG

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

def main():
    logger = setup_logging()
    logger.info("크롤링 시작")
    
    # 종목코드 읽기
    stock_codes = read_stock_codes()
    if not stock_codes:
        logger.error("종목코드가 없습니다.")
        return
        
    logger.info(f"총 {len(stock_codes)}개의 종목코드를 읽었습니다.")
    
    # 크롤러 초기화
    crawler = FnGuideCrawler(
        headless=CRAWLER_CONFIG['headless'],
        debug_mode=CRAWLER_CONFIG['debug_mode'],
        skip_step=CRAWLER_CONFIG['skip_step']
    )
    
    try:
        # 로그인
        if not crawler.login():
            logger.error("로그인 실패")
            return
            
        logger.info("로그인 성공")
        
        datas :list[dict] = []
        # 각 종목별로 데이터 수집
        for code in stock_codes:
            logger.info(f"종목 {code} 데이터 수집 시작")
            try:
                data :dict = crawler.get_item_detail(code)
                if data:
                    logger.info(f"종목 {code} 데이터 수집 완료")
                    datas.append(data)
                else:
                    logger.error(f"종목 {code} 데이터 수집 실패")
            except Exception as e:
                logger.error(f"종목 {code} 처리 중 오류 발생: {str(e)}")
                continue
        # 수집된 데이터를 CSV 파일로 내보내기
        if datas:
            import csv
            file_name = f'collected_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            with open(file_name, mode='w', newline='', encoding=CSV_CONFIG['encoding']) as file:
                writer = csv.writer(file)
                writer.writerow(CSV_CONFIG['columns'])
                for data in datas:
                    writer.writerow(data.values())
            logger.info(f"수집된 데이터를 {file_name} 파일로 내보냈습니다.")
        else:
            logger.error("수집된 데이터가 없습니다.")
    except Exception as e:
        logger.error(f"크롤링 중 오류 발생: {str(e)}")
    finally:
        crawler.close()
        logger.info("크롤링 종료")

if __name__ == "__main__":
    main() 