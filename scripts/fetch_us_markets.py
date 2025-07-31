#!/usr/bin/env python3
"""
미국 시장 데이터 수집 스크립트
Yahoo Finance에서 S&P 500, Nasdaq, Dow, Dollar Index, WTI, BTC 데이터 수집
"""

import yfinance as yf
import json
import os
from datetime import datetime, timezone, timedelta
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 추적할 심볼들
SYMBOLS = {
    'S&P 500': '^GSPC',
    'NASDAQ': '^IXIC', 
    'DOW': '^DJI',
    'Dollar Index': 'DX-Y.NYB',
    'WTI': 'CL=F',
    'BTC': 'BTC-USD'
}

def fetch_market_data():
    """Yahoo Finance에서 시장 데이터 수집"""
    market_data = {
        'timestamp': datetime.now(timezone(timedelta(hours=9))).isoformat(),
        'data': {}
    }
    
    for name, symbol in SYMBOLS.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='2d')
            
            if len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change_pct = ((current_price - prev_price) / prev_price) * 100
                
                market_data['data'][name] = {
                    'symbol': symbol,
                    'current_price': round(current_price, 2),
                    'change_pct': round(change_pct, 2),
                    'change_amount': round(current_price - prev_price, 2)
                }
                
                logger.info(f"✅ {name}: {current_price:.2f} ({change_pct:+.2f}%)")
            else:
                logger.warning(f"⚠️ {name}: 데이터 부족")
                
        except Exception as e:
            logger.error(f"❌ {name} 데이터 수집 실패: {e}")
    
    return market_data

def save_data(data, date_str):
    """데이터를 JSON 파일로 저장"""
    os.makedirs(f'data/{date_str}', exist_ok=True)
    filepath = f'data/{date_str}/raw_us.json'
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"💾 데이터 저장: {filepath}")
    return filepath

def main():
    """메인 실행 함수"""
    logger.info("🌅 미국 시장 데이터 수집 시작")
    
    # 오늘 날짜
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 데이터 수집
    market_data = fetch_market_data()
    
    # 데이터 저장
    filepath = save_data(market_data, today)
    
    logger.info("✅ 미국 시장 데이터 수집 완료")
    return filepath

if __name__ == "__main__":
    main() 