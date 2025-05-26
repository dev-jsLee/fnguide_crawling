import logging
from src.crawler.fnguide import FnGuideCrawler

def main(debug=False):
    """
    메인 실행 함수
    
    Args:
        debug (bool): 디버그 모드 실행 여부
    """
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # 크롤러 초기화 (headless=False로 설정하여 브라우저 표시)
        with FnGuideCrawler(headless=False, debug_mode=debug, skip_step=2) as crawler:
            # 로그인 시도
            if not crawler.login():
                logger.error("로그인 실패")
                return
            print("로그인 성공 in main.py")

            # 삼성전자 종목 정보 가져오기
            stock_code = "000660"  # SK하이닉스
            data = crawler.get_item_detail(stock_code)
            
            if data:
                logger.info(f"종목 {stock_code} 데이터 추출 성공")
            else:
                logger.error(f"종목 {stock_code} 데이터 추출 실패")
                
    except Exception as e:
        logger.error(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    # 디버그 모드로 실행 (각 단계에서 Enter 입력 대기)
    main(debug=True)
