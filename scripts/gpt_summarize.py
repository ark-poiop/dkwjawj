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

• [실제 S&P500 지수와 변동률]
• [실제 나스닥 지수와 변동률]
• [실제 주요 종목 등락 현황]

• [실제 달러 인덱스 수치]
• [실제 WTI 유가 수치]
• [실제 비트코인 변동률]

오늘 한국장 포인트:
• [실제 주목할 업종/종목]
• [실제 주요 변수]

👇 오늘장 전망, 어떻게 보시나요? 댓글로 남겨주세요!

## Threads 댓글(500자 이내) 포맷
✔ 오늘 체크리스트
① [실제 주요 이슈 1]
② [실제 주요 이슈 2]
③ [실제 주요 이슈 3]

🔖 저장하고 퇴근길에도 시장 체크!
#오늘의인사이트 #아침브리핑

데이터:
{json.dumps(data, ensure_ascii=False, indent=2)}

다음 JSON 형식으로 응답해주세요:
{{
  "slides": [
    {{
      "heading": "🌅 오버나이트 마켓 브리프",
      "bullet1": "S&P 500: [실제 변동률]% | 나스닥: [실제 변동률]% | 달러: [실제 변동률]%",
      "bullet2": "BTC: [실제 변동률]% | WTI: [실제 변동률]% | 주요 변동 요인",
      "hot": "🔥 [실제 주요 이슈]"
    }},
    {{
      "heading": "📊 주요 지수 현황",
      "bullet1": "S&P 500: [실제 지수] ([실제 변동률]%)",
      "bullet2": "나스닥: [실제 지수] ([실제 변동률]%) | 다우: [실제 지수] ([실제 변동률]%)",
      "hot": "💡 [실제 시장 동향]"
    }},
    {{
      "heading": "💱 환율 & 원자재",
      "bullet1": "달러인덱스: [실제 수치] ([실제 변동률]%)",
      "bullet2": "WTI: $[실제 가격] ([실제 변동률]%) | BTC: $[실제 가격] ([실제 변동률]%)",
      "hot": "⚡ [실제 원자재 동향]"
    }},
    {{
      "heading": "🎯 투자자 관심사",
      "bullet1": "[실제 관심사 1]",
      "bullet2": "[실제 관심사 2]",
      "hot": "📈 [실제 시장 관심사]"
    }},
    {{
      "heading": "🎯 투자자 관심사",
      "bullet1": "[실제 관심사 1]",
      "bullet2": "[실제 관심사 2]",
      "hot": "📈 [실제 시장 관심사]"
    }},
    {{
      "heading": "🔖 내일 아침에도 인사이트!",
      "bullet1": "매일 아침 7:30 업데이트",
      "bullet2": "실시간 시장 동향 제공",
      "hot": "📱 팔로우하고 놓치지 마세요!"
    }}
  ],
  "thread": {{
    "main": "🌅 Overnight Market Brief\\n\\n• [실제 S&P500 지수와 변동률]\\n• [실제 나스닥 지수와 변동률]\\n• [실제 주요 종목 등락 현황]\\n\\n• [실제 달러 인덱스 수치]\\n• [실제 WTI 유가 수치]\\n• [실제 비트코인 변동률]\\n\\n오늘 한국장 포인트:\\n• [실제 주목할 업종/종목]\\n• [실제 주요 변수]\\n\\n👇 오늘장 전망, 어떻게 보시나요? 댓글로 남겨주세요!",
    "comment": "✔ 오늘 체크리스트\\n① [실제 주요 이슈 1]\\n② [실제 주요 이슈 2]\\n③ [실제 주요 이슈 3]\\n\\n🔖 저장하고 퇴근길에도 시장 체크!\\n#오늘의인사이트 #아침브리핑"
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

• [실제 코스피 지수와 변동률]
• [실제 외국인 순매수/매도 금액]
• [실제 주요 종목 등락 현황]

• [실제 코스닥 지수와 변동률]
• [실제 업종별 등락 현황]

내일 주목 이벤트:
• [실제 글로벌 이벤트나 변수]

👉 오늘의 이슈, 댓글에!

## Threads 댓글(500자 이내) 포맷
Top 3 이슈
① [실제 주요 이슈 1]
② [실제 주요 이슈 2] 
③ [실제 주요 이슈 3]

🔖 장마감 이슈 저장해서 내일 전략 세우기!
#코스피 #점심마감 #오늘의인사이트

데이터:
{json.dumps(data, ensure_ascii=False, indent=2)}

다음 JSON 형식으로 응답해주세요:
{{
  "slides": [
    {{
      "heading": "🇰🇷 K-Close 리캡",
      "bullet1": "KOSPI: [실제 지수] ([실제 변동률]%) | KOSDAQ: [실제 지수] ([실제 변동률]%)",
      "bullet2": "외국인: [실제 순매수/매도] | 기관: [실제 순매수/매도]",
      "hot": "🔥 [실제 주요 이슈]"
    }},
    {{
      "heading": "📈 주요 지수 현황",
      "bullet1": "KOSPI: [실제 지수] ([실제 변동률]%)",
      "bullet2": "KOSDAQ: [실제 지수] ([실제 변동률]%) | 거래량: [실제 거래량]",
      "hot": "💡 [실제 시장 동향]"
    }},
    {{
      "heading": "💰 투자자 수급",
      "bullet1": "외국인: [실제 순매수/매도] ([실제 주요 종목])",
      "bullet2": "기관: [실제 순매수/매도] | 개인: [실제 순매수/매도]",
      "hot": "🌍 [실제 투자자 동향]"
    }},
    {{
      "heading": "🏭 업종별 등락",
      "bullet1": "[실제 업종1]: [실제 변동률]% | [실제 업종2]: [실제 변동률]%",
      "bullet2": "[실제 업종3]: [실제 변동률]% | [실제 업종4]: [실제 변동률]%",
      "hot": "📊 [실제 업종 동향]"
    }},
    {{
      "heading": "🎯 투자자 관심사",
      "bullet1": "[실제 관심사 1]",
      "bullet2": "[실제 관심사 2]",
      "hot": "💬 [실제 시장 관심사]"
    }},
    {{
      "heading": "🔖 내일 아침에도 인사이트!",
      "bullet1": "매일 점심 4:05 업데이트",
      "bullet2": "실시간 시장 동향 제공",
      "hot": "📱 팔로우하고 놓치지 마세요!"
    }}
  ],
      "thread": {{
    "main": "📊 코스피 마감 요약\\n\\n• [실제 코스피 지수와 변동률]\\n• [실제 외국인 순매수/매도 금액]\\n• [실제 주요 종목 등락 현황]\\n\\n• [실제 코스닥 지수와 변동률]\\n• [실제 업종별 등락 현황]\\n\\n내일 주목 이벤트:\\n• [실제 글로벌 이벤트나 변수]\\n\\n👉 내 포트폴리오 오늘 변동, 댓글로 공유해 주세요!",
    "comment": "Top 3 이슈\\n① [실제 주요 이슈 1]\\n② [실제 주요 이슈 2]\\n③ [실제 주요 이슈 3]\\n\\n🔖 점심 브리핑 저장해서 내일 전략 세우기!\\n#코스피 #점심마감 #오늘의인사이트"
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

• [실제 주요 이벤트 1]
• [실제 주요 이벤트 2]
• [실제 주요 이벤트 3]

• [실제 주목할 업종/종목]
• [실제 주요 변수]

👉 오늘 밤 주목 일정, 댓글에서 확인하세요!

## Threads 댓글(500자 이내) 포맷
Tonight Checklist
① [실제 이벤트 1]
② [실제 이벤트 2]
③ [실제 이벤트 3]

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
    "main": "🌙 Tonight's Watchlist\\n\\n• [실제 주요 이벤트 1]\\n• [실제 주요 이벤트 2]\\n• [실제 주요 이벤트 3]\\n\\n• [실제 주목할 업종/종목]\\n• [실제 주요 변수]\\n\\n👉 오늘 밤 주목 일정, 댓글로 남겨주세요!",
    "comment": "Tonight Checklist\\n① [실제 이벤트 1]\\n② [실제 이벤트 2]\\n③ [실제 이벤트 3]\\n\\n🔖 이 글 저장하고 내일 아침 시장 흐름 미리보기!\\n#오늘의일정 #저녁브리핑"
  }}
}}
"""

def call_gpt(prompt, max_retries=2):
    """GPT API 호출"""
    if not OPENAI_API_KEY or OPENAI_API_KEY == 'your_openai_api_key_here':
        logger.error("❌ OpenAI API 키가 설정되지 않았습니다. .env 파일에서 OPENAI_API_KEY를 설정해주세요.")
        return None
    
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        logger.error(f"❌ OpenAI 클라이언트 초기화 실패: {e}")
        return None
    
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
    
    try:
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
            
    except Exception as e:
        logger.error(f"❌ 메인 함수에서 예외 발생: {e}")
        import traceback
        logger.error(f"📄 상세 오류: {traceback.format_exc()}")
        return None

if __name__ == "__main__":
    main() 