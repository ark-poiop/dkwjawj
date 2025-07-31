#!/usr/bin/env python3
"""
GPT 요약 및 인사이트 생성 스크립트
데이터를 분석하여 Carousel 슬라이드와 Threads 포스트 생성
"""

import openai
import json
import os
from datetime import datetime
import logging
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# OpenAI 설정
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GPT_MODEL = 'gpt-4o'  # 고정 모델

def get_morning_prompt(data):
    """아침 프롬프트 생성"""
    return f"""
당신은 금융 전문가입니다. 미국 시장 데이터를 분석하여 인사이트를 제공해주세요.

## 요구사항
- 모두 한글로, 존댓말 사용
- 본문/댓글 각각 500자 이내
- 핵심 데이터는 줄바꿈 + 개조식(• 또는 ①②③ 등)으로 표기
- 본문 마지막에는 댓글 유도 문장(질문 or 행동 독려)
- 숫자·이모지 혼용(예: +1.2% 🔥)

## Threads 본문(500자 이내) 포맷
🌅 Overnight Market Brief

• S&P500 +0.9% 상승
• 나스닥 +1.2% 랠리
• 테슬라 +4.1% 강세, 엔비디아 +2.9% 상승

• 달러 인덱스 104.7 (-)
• WTI 유가 80달러 돌파
• 비트코인 1.5% 반등

오늘 한국장 포인트:
• 반도체·2차전지 주목
• 외국인 수급 동향 관찰

👇 오늘장 전망, 어떻게 보시나요? 댓글로 남겨주세요!

## Threads 댓글(500자 이내) 포맷
✔ 오늘 체크리스트
① 반도체·AI주 외국인 매수
② 나스닥 선물 추가 상승
③ 오늘 밤 美 CPI 발표

🔖 저장하고 퇴근길에도 시장 체크!
#오늘의인사이트 #아침브리핑

데이터:
{json.dumps(data, ensure_ascii=False, indent=2)}

다음 JSON 형식으로 응답해주세요:
{{
  "slides": [
    {{
      "heading": "🌅 오버나이트 마켓 브리프",
      "bullet1": "S&P 500: +1.2% | 나스닥: +0.8% | 달러: -0.3%",
      "bullet2": "BTC: +2.1% | WTI: -1.5% | 주요 변동 요인",
      "hot": "🔥 AI 관련주 상승세 지속"
    }},
    {{
      "heading": "📊 주요 지수 현황",
      "bullet1": "S&P 500: 4,850 (+1.2%)",
      "bullet2": "나스닥: 15,200 (+0.8%) | 다우: 38,500 (+0.9%)",
      "hot": "💡 기술주 중심 상승"
    }},
    {{
      "heading": "💱 환율 & 원자재",
      "bullet1": "달러인덱스: 102.5 (-0.3%)",
      "bullet2": "WTI: $78.5 (-1.5%) | BTC: $45,200 (+2.1%)",
      "hot": "⚡ 암호화폐 상승세"
    }},
    {{
      "heading": "🎯 투자자 관심사",
      "bullet1": "AI/반도체 주목받아",
      "bullet2": "FOMC 정책 기대감",
      "hot": "📈 성장주 선호"
    }},
    {{
      "heading": "🎯 투자자 관심사",
      "bullet1": "AI/반도체 주목받아",
      "bullet2": "FOMC 정책 기대감",
      "hot": "📈 성장주 선호"
    }},
    {{
      "heading": "🔖 내일 아침에도 인사이트!",
      "bullet1": "매일 아침 7:30 업데이트",
      "bullet2": "실시간 시장 동향 제공",
      "hot": "📱 팔로우하고 놓치지 마세요!"
    }}
  ],
  "thread": {{
    "main": "🌅 Overnight Market Brief\\n\\n• S&P500 +0.9% 상승\\n• 나스닥 +1.2% 랠리\\n• 테슬라 +4.1% 강세, 엔비디아 +2.9% 상승\\n\\n• 달러 인덱스 104.7 (-)\\n• WTI 유가 80달러 돌파\\n• 비트코인 1.5% 반등\\n\\n오늘 한국장 포인트:\\n• 반도체·2차전지 주목\\n• 외국인 수급 동향 관찰\\n\\n👇 오늘장 전망, 어떻게 보시나요? 댓글로 남겨주세요!",
    "comment": "✔ 오늘 체크리스트\\n① 반도체·AI주 외국인 매수\\n② 나스닥 선물 추가 상승\\n③ 오늘 밤 美 CPI 발표\\n\\n🔖 저장하고 퇴근길에도 시장 체크!\\n#오늘의인사이트 #아침브리핑"
  }}
}}
"""

def get_afternoon_prompt(data):
    """점심 프롬프트 생성"""
    return f"""
당신은 금융 전문가입니다. 한국 시장 종가 데이터를 분석하여 인사이트를 제공해주세요.

## 요구사항
- 모두 한글로, 존댓말 사용
- 본문/댓글 각각 500자 이내
- 핵심 데이터는 줄바꿈 + 개조식(• 또는 ①②③ 등)으로 표기
- 본문 마지막에는 댓글 유도 문장(질문 or 행동 독려)
- 숫자·이모지 혼용(예: +1.2% 🔥)

## Threads 본문(500자 이내) 포맷
📊 코스피 마감 요약

• 코스피 2,650선 돌파 (+1.0%)
• 외국인 순매수 +4,200억
• 삼성전자·LG에너지솔루션 강세

• 코스닥 소폭 하락, 2차전지 약세
• IT·자동차 업종 상승, 게임·엔터 약세

내일 주목 이벤트:
• 美CPI, 파월 발언 등 글로벌 변수

👉 내 포트폴리오 오늘 변동, 댓글로 공유해 주세요!

## Threads 댓글(500자 이내) 포맷
Top 3 이슈
① 삼성전자 목표가 상향
② 외인 순매수 Top: 하이브, 카카오
③ 내일 금리·환율 변수 주목

🔖 점심 브리핑 저장해서 내일 전략 세우기!
#코스피 #점심마감 #오늘의인사이트

데이터:
{json.dumps(data, ensure_ascii=False, indent=2)}

다음 JSON 형식으로 응답해주세요:
{{
  "slides": [
    {{
      "heading": "🇰🇷 K-Close 리캡",
      "bullet1": "KOSPI: 2,650 (+0.8%) | KOSDAQ: 850 (+1.2%)",
      "bullet2": "외국인 순매수: +1,200억 | 기관: -800억",
      "hot": "🔥 반도체주 강세"
    }},
    {{
      "heading": "📈 주요 지수 현황",
      "bullet1": "KOSPI: 2,650 (+0.8%)",
      "bullet2": "KOSDAQ: 850 (+1.2%) | 거래량: 8.5조원",
      "hot": "💡 기술주 중심 상승"
    }},
    {{
      "heading": "💰 투자자 수급",
      "bullet1": "외국인: +1,200억 (삼성전자, SK하이닉스)",
      "bullet2": "기관: -800억 | 개인: -400억",
      "hot": "🌍 외국인 매수세"
    }},
    {{
      "heading": "🏭 업종별 등락",
      "bullet1": "반도체: +2.5% | 자동차: +1.8%",
      "bullet2": "바이오: -0.5% | 금융: -1.2%",
      "hot": "📊 업종 분화"
    }},
    {{
      "heading": "🎯 투자자 관심사",
      "bullet1": "한국 반도체주 토론",
      "bullet2": "외국인 투자 동향",
      "hot": "💬 시장 관심 집중"
    }},
    {{
      "heading": "🔖 내일 아침에도 인사이트!",
      "bullet1": "매일 점심 4:05 업데이트",
      "bullet2": "실시간 시장 동향 제공",
      "hot": "📱 팔로우하고 놓치지 마세요!"
    }}
  ],
  "thread": {{
    "main": "📊 코스피 마감 요약\\n\\n• 코스피 2,650선 돌파 (+1.0%)\\n• 외국인 순매수 +4,200억\\n• 삼성전자·LG에너지솔루션 강세\\n\\n• 코스닥 소폭 하락, 2차전지 약세\\n• IT·자동차 업종 상승, 게임·엔터 약세\\n\\n내일 주목 이벤트:\\n• 美CPI, 파월 발언 등 글로벌 변수\\n\\n👉 내 포트폴리오 오늘 변동, 댓글로 공유해 주세요!",
    "comment": "Top 3 이슈\\n① 삼성전자 목표가 상향\\n② 외인 순매수 Top: 하이브, 카카오\\n③ 내일 금리·환율 변수 주목\\n\\n🔖 점심 브리핑 저장해서 내일 전략 세우기!\\n#코스피 #점심마감 #오늘의인사이트"
  }}
}}
"""

def get_evening_prompt(data):
    """저녁 프롬프트 생성"""
    return f"""
당신은 금융 전문가입니다. 오늘의 주요 뉴스와 이벤트를 분석하여 인사이트를 제공해주세요.

## 요구사항
- 모두 한글로, 존댓말 사용
- 본문/댓글 각각 500자 이내
- 핵심 데이터는 줄바꿈 + 개조식(• 또는 ①②③ 등)으로 표기
- 본문 마지막에는 댓글 유도 문장(질문 or 행동 독려)
- 숫자·이모지 혼용(예: +1.2% 🔥)

## Threads 본문(500자 이내) 포맷
🌙 Tonight's Watchlist

• 美 CPI, FOMC 등 빅 이벤트 대기
• 마이크로소프트·애플 실적 발표 예정
• 글로벌 투자자 이목 집중

• AI·반도체 관련주 변동성 주의
• 매크로 변수 체크 필수

👉 오늘 밤 주목 일정, 댓글로 남겨주세요!

## Threads 댓글(500자 이내) 포맷
Tonight Checklist
① 美 CPI (21:30 KST)
② FOMC 위원 발언
③ 애플 실적 콜

🔖 이 글 저장하고 내일 아침 시장 흐름 미리보기!
#오늘의일정 #저녁브리핑

데이터:
{json.dumps(data, ensure_ascii=False, indent=2)}

다음 JSON 형식으로 응답해주세요:
{{
  "slides": [
    {{
      "heading": "🌙 투나잇 워치리스트",
      "bullet1": "오늘 주요 뉴스 5개",
      "bullet2": "내일 주요 이벤트",
      "hot": "🔥 시장 영향도 높은 뉴스"
    }},
    {{
      "heading": "📰 핵심 뉴스 1",
      "bullet1": "뉴스 제목",
      "bullet2": "주요 내용 요약",
      "hot": "💡 시장 영향"
    }},
    {{
      "heading": "📰 핵심 뉴스 2",
      "bullet1": "뉴스 제목",
      "bullet2": "주요 내용 요약",
      "hot": "💡 시장 영향"
    }},
    {{
      "heading": "📰 핵심 뉴스 3",
      "bullet1": "뉴스 제목",
      "bullet2": "주요 내용 요약",
      "hot": "💡 시장 영향"
    }},
    {{
      "heading": "🎯 투자자 관심사",
      "bullet1": "오늘 가장 중요한 이슈",
      "bullet2": "시장 반응",
      "hot": "💬 투자자 관심사"
    }},
    {{
      "heading": "🔖 내일 아침에도 인사이트!",
      "bullet1": "매일 저녁 9:00 업데이트",
      "bullet2": "실시간 시장 동향 제공",
      "hot": "📱 팔로우하고 놓치지 마세요!"
    }}
  ],
  "thread": {{
    "main": "🌙 Tonight's Watchlist\\n\\n• 美 CPI, FOMC 등 빅 이벤트 대기\\n• 마이크로소프트·애플 실적 발표 예정\\n• 글로벌 투자자 이목 집중\\n\\n• AI·반도체 관련주 변동성 주의\\n• 매크로 변수 체크 필수\\n\\n👉 오늘 밤 주목 일정, 댓글로 남겨주세요!",
    "comment": "Tonight Checklist\\n① 美 CPI (21:30 KST)\\n② FOMC 위원 발언\\n③ 애플 실적 콜\\n\\n🔖 이 글 저장하고 내일 아침 시장 흐름 미리보기!\\n#오늘의일정 #저녁브리핑"
  }}
}}
"""

def call_gpt(prompt, max_retries=2):
    """GPT API 호출"""
    if not OPENAI_API_KEY or OPENAI_API_KEY == 'your_openai_api_key_here':
        logger.error("❌ OpenAI API 키가 설정되지 않았습니다. .env 파일에서 OPENAI_API_KEY를 설정해주세요.")
        return None
    
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    for attempt in range(max_retries + 1):
        try:
            logger.info(f"🤖 GPT 모델 사용: {GPT_MODEL}")
            response = client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": "당신은 금융 전문가입니다. 한국어로 응답하고, JSON 형식을 정확히 지켜주세요."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=2000,
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ JSON 파싱 실패 (시도 {attempt + 1}): {e}")
            if attempt == max_retries:
                raise
        except Exception as e:
            logger.error(f"❌ GPT API 호출 실패 (시도 {attempt + 1}): {e}")
            if attempt == max_retries:
                raise
    
    return None

def save_summary(summary, date_str, session_type):
    """요약 결과 저장"""
    os.makedirs(f'data/{date_str}', exist_ok=True)
    
    # 슬라이드 데이터 저장
    slides_file = f'data/{date_str}/slides_{date_str}.json'
    with open(slides_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    # Thread 데이터 저장
    thread_file = f'data/{date_str}/thread_post.json'
    thread_data = {
        'timestamp': datetime.now().isoformat(),
        'session_type': session_type,
        'thread': summary.get('thread', {})
    }
    with open(thread_file, 'w', encoding='utf-8') as f:
        json.dump(thread_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"💾 요약 결과 저장: {slides_file}, {thread_file}")
    return slides_file, thread_file

def main():
    """메인 실행 함수"""
    import sys
    
    if len(sys.argv) != 2:
        logger.error("❌ 사용법: python gpt_summarize.py [morning|afternoon|evening]")
        return None
    
    session_type = sys.argv[1]
    today = datetime.now().strftime('%Y-%m-%d')
    
    logger.info(f"🤖 GPT 요약 시작: {session_type} 세션")
    logger.info(f"📋 사용 모델: {GPT_MODEL}")
    logger.info(f"🔑 API 키 상태: {'✅ 설정됨' if OPENAI_API_KEY and OPENAI_API_KEY != 'your_openai_api_key_here' else '❌ 설정 필요'}")
    
    # 입력 파일 경로
    if session_type == "morning":
        input_file = f'data/{today}/raw_us.json'
        prompt_func = get_morning_prompt
    elif session_type == "afternoon":
        input_file = f'data/{today}/raw_kr.json'
        prompt_func = get_afternoon_prompt
    elif session_type == "evening":
        input_file = f'data/{today}/clean_news.json'
        prompt_func = get_evening_prompt
    else:
        logger.error("❌ 잘못된 세션 타입")
        return None
    
    # 입력 파일 확인
    if not os.path.exists(input_file):
        logger.error(f"❌ 입력 파일 없음: {input_file}")
        return None
    
    # 데이터 로드
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 지수 데이터 추가 (있는 경우)
    kr_index_file = f'data/{today}/kr_index.json'
    if os.path.exists(kr_index_file):
        with open(kr_index_file, 'r', encoding='utf-8') as f:
            kr_index_data = json.load(f)
            if isinstance(data, dict):
                data['kr_index'] = kr_index_data
            else:
                data = {'news': data, 'kr_index': kr_index_data}
    
    # 프롬프트 생성
    prompt = prompt_func(data)
    
    # GPT 호출
    try:
        summary = call_gpt(prompt)
        if summary:
            # 결과 저장
            slides_file, thread_file = save_summary(summary, today, session_type)
            logger.info("✅ GPT 요약 완료")
            return slides_file, thread_file
        else:
            logger.error("❌ GPT 요약 실패")
            return None
    except Exception as e:
        logger.error(f"❌ GPT 요약 중 오류: {e}")
        return None

if __name__ == "__main__":
    main() 