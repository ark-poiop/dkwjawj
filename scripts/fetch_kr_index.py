#!/usr/bin/env python3
"""
한국 지수 데이터 수집 스크립트
한국 금융위 API에서 KOSPI, KOSDAQ 등 주요 지수 데이터 수집
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

def fetch_index_data(date_str):
    """한국 지수 API에서 지수 데이터 수집"""
    try:
        # API 키 확인
        api_key = os.getenv('KOREA_FINANCE_API_KEY')
        if not api_key:
            logger.error("❌ 한국 금융위 API 키가 설정되지 않았습니다.")
            return None
        
        # 지수 API URL
        url = "https://apis.data.go.kr/1160100/service/GetMarketIndexInfoService/getMarketIndexInfo"
        
        # 수집할 지수들
        indices = ['KOSPI', 'KOSDAQ', 'KOSPI200']
        
        all_data = []
        
        for index_name in indices:
            params = {
                'serviceKey': api_key,
                'numOfRows': 1,
                'pageNo': 1,
                'resultType': 'xml',
                'basDt': date_str.replace('-', ''),
                'idxNm': index_name
            }
            
            try:
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    # XML 응답 파싱
                    response_text = response.text
                    if 'NORMAL SERVICE' in response_text:
                        # XML 데이터 파싱
                        lines = response_text.strip().split('\n')
                        if len(lines) >= 2:
                            data_line = lines[1].strip()
                            fields = data_line.split()
                            if len(fields) >= 10:
                                index_data = {
                                    'idxNm': fields[3],  # 지수명
                                    'clpr': fields[4],   # 종가
                                    'vs': fields[5],     # 전일대비
                                    'fltRt': fields[6],  # 등락률
                                    'oprc': fields[7],   # 시가
                                    'hgpr': fields[8],   # 고가
                                    'lwpr': fields[9],   # 저가
                                    'trqu': fields[10],  # 거래량
                                    'basDt': fields[2]   # 기준일자
                                }
                                all_data.append(index_data)
                                logger.info(f"✅ {index_name} 지수 데이터 수집 완료")
                            else:
                                logger.warning(f"⚠️ {index_name} 데이터 형식 오류")
                        else:
                            logger.warning(f"⚠️ {index_name} 데이터 없음")
                    else:
                        logger.warning(f"⚠️ {index_name} 서비스 오류")
                else:
                    logger.warning(f"⚠️ {index_name} 요청 실패: {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ {index_name} 수집 중 오류: {e}")
        
        if not all_data:
            logger.warning("⚠️ 지수 데이터 수집 실패. 더미 데이터를 사용합니다.")
            return generate_dummy_index_data(date_str)
        
        logger.info(f"✅ 한국 지수 API 요청 완료: {date_str} (총 {len(all_data)}개 지수)")
        return all_data
        
    except Exception as e:
        logger.error(f"❌ 한국 지수 API 데이터 수집 실패: {e}")
        return generate_dummy_index_data(date_str)

def generate_dummy_index_data(date_str):
    """더미 지수 데이터 생성"""
    logger.info("📊 지수 더미 데이터 생성 중...")
    
    dummy_data = [
        {
            'idxNm': 'KOSPI',
            'clpr': '2650.50',
            'vs': '25.30',
            'fltRt': '0.96',
            'oprc': '2625.20',
            'hgpr': '2660.80',
            'lwpr': '2620.10',
            'trqu': '850000000',
            'basDt': date_str.replace('-', '')
        },
        {
            'idxNm': 'KOSDAQ',
            'clpr': '850.20',
            'vs': '8.50',
            'fltRt': '1.01',
            'oprc': '841.70',
            'hgpr': '855.30',
            'lwpr': '840.50',
            'trqu': '450000000',
            'basDt': date_str.replace('-', '')
        },
        {
            'idxNm': 'KOSPI200',
            'clpr': '350.80',
            'vs': '3.20',
            'fltRt': '0.92',
            'oprc': '347.60',
            'hgpr': '352.40',
            'lwpr': '346.80',
            'trqu': '380000000',
            'basDt': date_str.replace('-', '')
        }
    ]
    
    logger.info(f"✅ 지수 더미 데이터 생성 완료: {date_str} (총 {len(dummy_data)}개 지수)")
    return dummy_data

def parse_index_data(index_data_list):
    """지수 데이터 파싱"""
    index_data = {
        'timestamp': datetime.now().isoformat(),
        'kospi': {},
        'kosdaq': {},
        'kospi200': {},
        'summary': {}
    }
    
    try:
        if not index_data_list:
            logger.warning("⚠️ 수집된 지수 데이터가 없습니다.")
            return index_data
        
        for data in index_data_list:
            try:
                index_info = {
                    'name': data.get('idxNm', ''),
                    'close': float(data.get('clpr', 0)),
                    'change': float(data.get('vs', 0)),
                    'change_pct': float(data.get('fltRt', 0)),
                    'open': float(data.get('oprc', 0)),
                    'high': float(data.get('hgpr', 0)),
                    'low': float(data.get('lwpr', 0)),
                    'volume': int(data.get('trqu', 0)),
                    'date': data.get('basDt', '')
                }
                
                if data.get('idxNm') == 'KOSPI':
                    index_data['kospi'] = index_info
                elif data.get('idxNm') == 'KOSDAQ':
                    index_data['kosdaq'] = index_info
                elif data.get('idxNm') == 'KOSPI200':
                    index_data['kospi200'] = index_info
                    
            except (ValueError, TypeError) as e:
                logger.warning(f"⚠️ 지수 데이터 파싱 오류: {e}")
                continue
        
        # 요약 정보 생성
        if index_data['kospi'] and index_data['kosdaq']:
            index_data['summary'] = {
                'kospi_close': index_data['kospi']['close'],
                'kospi_change_pct': index_data['kospi']['change_pct'],
                'kosdaq_close': index_data['kosdaq']['close'],
                'kosdaq_change_pct': index_data['kosdaq']['change_pct'],
                'market_trend': '상승' if index_data['kospi']['change_pct'] > 0 else '하락'
            }
        
        logger.info(f"✅ 지수 데이터 파싱 완료: {len(index_data_list)}개 지수")
        
    except Exception as e:
        logger.error(f"❌ 지수 데이터 파싱 실패: {e}")
    
    return index_data

def save_data(data, date_str):
    """데이터를 JSON 파일로 저장"""
    os.makedirs(f'data/{date_str}', exist_ok=True)
    filepath = f'data/{date_str}/kr_index.json'
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"💾 데이터 저장: {filepath}")
    return filepath

def main():
    """메인 실행 함수"""
    logger.info("📈 한국 지수 데이터 수집 시작")
    
    # 오늘 날짜
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 지수 데이터 수집
    index_data_list = fetch_index_data(today)
    
    # 데이터 파싱
    parsed_data = parse_index_data(index_data_list)
    
    # 데이터 저장
    filepath = save_data(parsed_data, today)
    
    logger.info("✅ 한국 지수 데이터 수집 완료")
    return filepath

if __name__ == "__main__":
    main() 