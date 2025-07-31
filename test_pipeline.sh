#!/bin/bash

# Daily "아·점·저" Insight Pipeline 테스트 스크립트

echo "🧪 Daily Insight Pipeline 테스트 시작"
echo "=================================="

# 현재 날짜
TODAY=$(date +%Y-%m-%d)
echo "📅 테스트 날짜: $TODAY"

# 1. 더미 데이터 확인
echo ""
echo "1️⃣ 더미 데이터 확인..."
if [ -f "data/2025-01-15/raw_us.json" ]; then
    echo "✅ 미국 시장 더미 데이터 존재"
else
    echo "❌ 미국 시장 더미 데이터 없음"
    exit 1
fi

if [ -f "data/2025-01-15/raw_kr.json" ]; then
    echo "✅ 한국 시장 더미 데이터 존재"
else
    echo "❌ 한국 시장 더미 데이터 없음"
    exit 1
fi

if [ -f "data/2025-01-15/clean_news.json" ]; then
    echo "✅ 뉴스 더미 데이터 존재"
else
    echo "❌ 뉴스 더미 데이터 없음"
    exit 1
fi

# 2. 아침 세션 테스트
echo ""
echo "2️⃣ 아침 세션 테스트..."
echo "🌅 GPT 요약 테스트 (아침)..."

# 더미 데이터를 오늘 날짜로 복사
mkdir -p "data/$TODAY"
cp "data/2025-01-15/raw_us.json" "data/$TODAY/"

# GPT 요약 테스트 (실제 API 키가 없으면 더미 응답 사용)
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️ OpenAI API 키가 없어 더미 응답을 생성합니다..."
    
    # 더미 슬라이드 데이터 생성
    cat > "data/$TODAY/slides_$TODAY.json" << 'EOF'
{
  "slides": [
    {
      "heading": "🌅 오버나이트 마켓 브리프",
      "bullet1": "S&P 500: +1.2% | 나스닥: +0.8% | 달러: -0.3%",
      "bullet2": "BTC: +2.1% | WTI: -1.5% | 주요 변동 요인",
      "hot": "🔥 AI 관련주 상승세 지속"
    },
    {
      "heading": "📊 주요 지수 현황",
      "bullet1": "S&P 500: 4,850 (+1.2%)",
      "bullet2": "나스닥: 15,200 (+0.8%) | 다우: 38,500 (+0.9%)",
      "hot": "💡 기술주 중심 상승"
    },
    {
      "heading": "💱 환율 & 원자재",
      "bullet1": "달러인덱스: 102.5 (-0.3%)",
      "bullet2": "WTI: $78.5 (-1.5%) | BTC: $45,200 (+2.1%)",
      "hot": "⚡ 암호화폐 상승세"
    },
    {
      "heading": "🎯 투자자 관심사",
      "bullet1": "AI/반도체 주목받아",
      "bullet2": "FOMC 정책 기대감",
      "hot": "📈 성장주 선호"
    },
    {
      "heading": "🔴 Reddit 핫토픽",
      "bullet1": "AI 관련주 토론 활발",
      "bullet2": "FOMC 정책 전망",
      "hot": "💬 커뮤니티 관심 집중"
    },
    {
      "heading": "🔖 내일 아침에도 인사이트!",
      "bullet1": "매일 아침 7:30 업데이트",
      "bullet2": "실시간 시장 동향 제공",
      "hot": "📱 팔로우하고 놓치지 마세요!"
    }
  ],
  "thread": {
    "main": "🌅 오늘 아침 미국 시장은 AI 관련주 중심으로 상승세를 보였습니다. S&P 500은 1.2% 상승했고, 나스닥도 0.8% 올랐네요. 특히 NVIDIA, AMD 등 AI 반도체주가 강세를 보이고 있어요. 오늘 한국 시장도 이어받을까요? 🤔",
    "comment": "💬 Reddit에서도 AI 관련주 토론이 활발합니다. 'AI는 이제 시작'이라는 의견이 많아요. 여러분은 어떤 종목에 관심이 있으신가요? 👇"
  }
}
EOF

    # 더미 Thread 데이터 생성
    cat > "data/$TODAY/thread_post.json" << 'EOF'
{
  "timestamp": "2025-01-15T07:30:00+09:00",
  "session_type": "morning",
  "thread": {
    "main": "🌅 오늘 아침 미국 시장은 AI 관련주 중심으로 상승세를 보였습니다. S&P 500은 1.2% 상승했고, 나스닥도 0.8% 올랐네요. 특히 NVIDIA, AMD 등 AI 반도체주가 강세를 보이고 있어요. 오늘 한국 시장도 이어받을까요? 🤔",
    "comment": "💬 Reddit에서도 AI 관련주 토론이 활발합니다. 'AI는 이제 시작'이라는 의견이 많아요. 여러분은 어떤 종목에 관심이 있으신가요? 👇"
  }
}
EOF

    echo "✅ 더미 슬라이드 데이터 생성 완료"
else
    echo "🤖 GPT 요약 실행 중..."
    python scripts/gpt_summarize.py morning
fi

# 3. Carousel 이미지 생성 테스트
echo ""
echo "3️⃣ Carousel 이미지 생성 테스트..."
echo "🎨 이미지 생성 중..."

python scripts/local_carousel.py "data/$TODAY/slides_$TODAY.json"

if [ -d "data/$TODAY/preview" ]; then
    echo "✅ Carousel 이미지 생성 완료"
    echo "📁 생성된 이미지들:"
    ls -la "data/$TODAY/preview/"
else
    echo "❌ Carousel 이미지 생성 실패"
    exit 1
fi

# 4. Buffer 업로드 테스트 (DRY RUN)
echo ""
echo "4️⃣ Buffer 업로드 테스트 (DRY RUN)..."
echo "📤 업로드 시뮬레이션 중..."

python scripts/buffer_uploader.py morning "data/$TODAY/slides_$TODAY.json"

echo ""
echo "🎉 테스트 완료!"
echo "=================================="
echo "📊 생성된 파일들:"
echo "  - 슬라이드 데이터: data/$TODAY/slides_$TODAY.json"
echo "  - Thread 데이터: data/$TODAY/thread_post.json"
echo "  - 이미지들: data/$TODAY/preview/"
echo ""
echo "🔍 미리보기 확인:"
echo "  open data/$TODAY/preview/  # macOS"
echo "  # 또는 파일 탐색기에서 data/$TODAY/preview/ 폴더 열기" 