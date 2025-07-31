#!/usr/bin/env python3
"""
뉴스 데이터 수집 스크립트
NewsAPI에서 금융 관련 뉴스 수집
"""

import requests
import json
import os
from datetime import datetime
import logging
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_news_data():
    """뉴스 데이터 수집"""
    try:
        # API 키 확인
        api_key = os.getenv('NEWS_API_KEY')
        if not api_key:
            logger.warning("⚠️ NewsAPI 키가 설정되지 않았습니다. 더미 데이터를 사용합니다.")
            return generate_dummy_news_data()
        
        # NewsAPI 요청
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            'apiKey': api_key,
            'country': 'us',
            'category': 'business',
            'pageSize': 10
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                if articles:
                    # 뉴스 데이터 정리
                    news_data = []
                    for article in articles[:5]:  # 상위 5개만
                        news_item = {
                            'title': article.get('title', ''),
                            'description': article.get('description', ''),
                            'url': article.get('url', ''),
                            'publishedAt': article.get('publishedAt', ''),
                            'source': article.get('source', {}).get('name', '')
                        }
                        news_data.append(news_item)
                    
                    logger.info(f"✅ 뉴스 데이터 수집 완료: {len(news_data)}개 기사")
                    return news_data
                else:
                    logger.warning("⚠️ 뉴스 기사가 없습니다. 더미 데이터를 사용합니다.")
                    return generate_dummy_news_data()
            else:
                logger.warning(f"⚠️ NewsAPI 요청 실패: {response.status_code}. 더미 데이터를 사용합니다.")
                return generate_dummy_news_data()
        except Exception as e:
            logger.warning(f"⚠️ NewsAPI 요청 중 오류: {e}. 더미 데이터를 사용합니다.")
            return generate_dummy_news_data()
            
    except Exception as e:
        logger.error(f"❌ 뉴스 데이터 수집 실패: {e}")
        return generate_dummy_news_data()

def generate_dummy_news_data():
    """더미 뉴스 데이터 생성"""
    logger.info("📰 뉴스 더미 데이터 생성 중...")
    
    dummy_news = [
        {
            'title': 'Federal Reserve Signals Potential Rate Cut in September',
            'description': 'The Federal Reserve indicated a possible interest rate reduction in September, citing improved inflation data and economic stability.',
            'url': 'https://example.com/fed-rate-cut',
            'publishedAt': '2025-07-31T20:00:00Z',
            'source': 'Financial Times'
        },
        {
            'title': 'Tech Stocks Rally on Strong Earnings Reports',
            'description': 'Major technology companies reported better-than-expected earnings, driving a broad market rally in the tech sector.',
            'url': 'https://example.com/tech-earnings',
            'publishedAt': '2025-07-31T19:30:00Z',
            'source': 'Reuters'
        },
        {
            'title': 'Oil Prices Decline Amid Global Demand Concerns',
            'description': 'Crude oil prices fell as concerns about global economic growth and demand weighed on the energy market.',
            'url': 'https://example.com/oil-prices',
            'publishedAt': '2025-07-31T19:00:00Z',
            'source': 'Bloomberg'
        },
        {
            'title': 'Asian Markets Show Mixed Performance',
            'description': 'Asian markets displayed mixed performance with some indices gaining while others declined on regional economic data.',
            'url': 'https://example.com/asian-markets',
            'publishedAt': '2025-07-31T18:30:00Z',
            'source': 'CNBC'
        },
        {
            'title': 'Cryptocurrency Market Shows Volatility',
            'description': 'Bitcoin and other cryptocurrencies experienced significant volatility as regulatory developments continue to impact the market.',
            'url': 'https://example.com/crypto-volatility',
            'publishedAt': '2025-07-31T18:00:00Z',
            'source': 'CoinDesk'
        }
    ]
    
    logger.info(f"✅ 뉴스 더미 데이터 생성 완료: {len(dummy_news)}개 기사")
    return dummy_news

def save_data(data, date_str):
    """데이터를 JSON 파일로 저장"""
    os.makedirs(f'data/{date_str}', exist_ok=True)
    filepath = f'data/{date_str}/clean_news.json'
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"💾 데이터 저장: {filepath}")
    return filepath

def main():
    """메인 실행 함수"""
    logger.info("📰 뉴스 데이터 수집 시작")
    
    # 오늘 날짜
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 뉴스 데이터 수집
    news_data = fetch_news_data()
    
    # 데이터 저장
    filepath = save_data(news_data, today)
    
    logger.info("✅ 뉴스 데이터 수집 완료")
    return filepath

if __name__ == "__main__":
    main() 