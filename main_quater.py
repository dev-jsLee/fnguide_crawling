"""
분기별 데이터 크롤링 메인 스크립트 (리팩토링 버전)
새로운 모듈 구조를 사용하여 중복 코드 제거 및 구조 개선
"""
from src.core.crawler_service import CrawlerService, CrawlingMode
from src.utils.file_utils import read_stock_codes
from config.config import (
    CRAWLER_CONFIG, 
    FILE_PATHS, 
    CSV_CONFIG,
    LOGIN_URL,
    ITEM_DETAIL_URL
)


def main():
    """분기별 데이터 크롤링 메인 함수"""
    # 크롤러 서비스 초기화
    service = CrawlerService(
        headless=CRAWLER_CONFIG['headless'],
        debug_mode=CRAWLER_CONFIG['debug_mode'],
        skip_step=CRAWLER_CONFIG['skip_step'],
        log_dir=FILE_PATHS['log_dir']
    )
    
    # 로거 설정
    logger = service.setup_logger("crawler_quarterly")
    logger.info("분기별 데이터 크롤링 시작")
    
    try:
        # 종목코드 읽기
        stock_codes = read_stock_codes(FILE_PATHS['stock_codes'])
        if not stock_codes:
            logger.error("종목코드가 없습니다.")
            return
        
        # 사용자 입력 받기 (연도, 분기)
        year, quarter = service.get_user_input_quarterly()
        if year is None or quarter is None:
            return
        
        # 크롤러 초기화
        if not service.initialize_crawler(year, quarter):
            logger.error("크롤러 초기화 실패")
            return
        
        # 로그인
        if not service.login(LOGIN_URL):
            logger.error("로그인 실패")
            return
        
        # 데이터 크롤링
        file_name, success_count, failure_count = service.crawl_stock_data(
            stock_codes=stock_codes,
            mode=CrawlingMode.QUARTERLY,
            csv_columns=CSV_CONFIG['columns'],
            item_detail_url=ITEM_DETAIL_URL
        )
        
        logger.info(f"크롤링 완료 - 파일: {file_name}, 성공: {success_count}, 실패: {failure_count}")
        
    except Exception as e:
        logger.error(f"크롤링 중 오류 발생: {str(e)}")
    finally:
        service.close()


if __name__ == "__main__":
    main() 