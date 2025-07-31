#!/bin/bash

echo "🚀 통합 파이프라인 테스트 시작 (Threads API 포함)"
echo "=================================================="
echo "📅 테스트 날짜: $(date +%Y-%m-%d)"
echo ""

# 1. 환경변수 확인
echo "1️⃣ 환경변수 확인..."
source .env 2>/dev/null || echo "⚠️ .env 파일을 찾을 수 없습니다."

# Threads API 환경변수 확인
if [ -z "$FACEBOOK_ACCESS_TOKEN" ]; then
    echo "⚠️ FACEBOOK_ACCESS_TOKEN 환경변수가 설정되지 않았습니다."
    echo "   Threads API 테스트를 건너뜁니다."
    USE_THREADS_API=false
else
    echo "✅ FACEBOOK_ACCESS_TOKEN 설정됨"
    USE_THREADS_API=true
fi

if [ -z "$IG_USER_ID" ]; then
    echo "⚠️ IG_USER_ID 환경변수가 설정되지 않았습니다."
    echo "   Threads API 테스트를 건너뜁니다."
    USE_THREADS_API=false
else
    echo "✅ IG_USER_ID 설정됨"
fi

echo ""

# 2. 더미 데이터 준비
echo "2️⃣ 더미 데이터 준비..."
if [ ! -d "data/2025-07-31" ]; then
    mkdir -p data/2025-07-31
    echo "✅ 테스트 디렉토리 생성: data/2025-07-31"
fi

# 더미 데이터 복사
if [ -d "data/2025-01-15" ]; then
    cp data/2025-01-15/raw_*.json data/2025-07-31/ 2>/dev/null || true
    cp data/2025-01-15/clean_news.json data/2025-07-31/ 2>/dev/null || true
    echo "✅ 더미 데이터 복사 완료"
fi

echo ""

# 3. GPT 요약 테스트
echo "3️⃣ GPT 요약 테스트..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️ OPENAI_API_KEY가 설정되지 않아 더미 응답을 생성합니다."
    # 더미 GPT 응답 생성
    cat > data/2025-07-31/slides_2025-07-31.json << 'EOF'
{
  "slides": [
    {
      "heading": "🌅 아침 브리핑",
      "bullet1": "• S&P500 +0.9% 상승",
      "bullet2": "• 나스닥 +1.2% 랠리",
      "hot": "🔥 테슬라 +4.1% 강세"
    },
    {
      "heading": "📊 주요 지표",
      "bullet1": "• 달러 인덱스 102.5",
      "bullet2": "• WTI 원유 $78.2",
      "hot": "🔥 BTC $43,200"
    },
    {
      "heading": "🇰🇷 한국 시장",
      "bullet1": "• KOSPI 2,450",
      "bullet2": "• 외국인 매수세",
      "hot": "🔥 반도체주 강세"
    },
    {
      "heading": "📈 섹터 동향",
      "bullet1": "• AI/반도체 +2.1%",
      "bullet2": "• 2차전지 +1.8%",
      "hot": "🔥 게임주 +3.2%"
    },
    {
      "heading": "🔥 핫이슈",
      "bullet1": "• \"테슬라, AI 로봇 기대감에 4% 상승\"",
      "bullet2": "• Reddit 'investorAI'",
      "hot": "🔥 AI 관련주 주목"
    },
    {
      "heading": "🔖 내일도 체크!",
      "bullet1": "• 아침 7:30 브리핑",
      "bullet2": "• 실시간 시장 모니터링",
      "hot": "🔥 인사이트 저장하기"
    }
  ]
}
EOF

    cat > data/2025-07-31/thread_post.json << 'EOF'
{
  "thread": {
    "main": "🌅 뉴욕 증시 요약\n• S&P500 +0.9% 상승\n• 나스닥 +1.2% 랠리\n• 테슬라 +4.1% 강세, 엔비디아 +2.9% 동반 상승\n\n오늘 한국장 포인트\n• 반도체·2차전지 주목\n• 외국인 수급 동향 관찰\n\n👉 궁금한 점, 댓글로 남겨주세요!",
    "comment": "\"테슬라, AI·로봇 기대감에 4% 상승\" – Reddit 'investorAI'\n\n✔ 오늘 체크리스트\n① 반도체·AI주 외국인 매수세\n② 나스닥 선물 추가 상승세\n③ 오늘 밤 美 CPI 발표\n\n🔖 이 글 저장하고 퇴근길에도 시장 체크! #오늘의인사이트 #아침브리핑"
  }
}
EOF
    echo "✅ 더미 GPT 응답 생성 완료"
else
    python scripts/gpt_summarize.py morning
    if [ $? -eq 0 ]; then
        echo "✅ GPT 요약 완료"
    else
        echo "❌ GPT 요약 실패"
        exit 1
    fi
fi

echo ""

# 4. Carousel 이미지 생성 테스트
echo "4️⃣ Carousel 이미지 생성 테스트..."
python scripts/local_carousel.py data/2025-07-31/slides_2025-07-31.json
if [ $? -eq 0 ]; then
    echo "✅ Carousel 이미지 생성 완료"
else
    echo "❌ Carousel 이미지 생성 실패"
    exit 1
fi

echo ""

# 5. Threads API 테스트
echo "5️⃣ Threads API 테스트..."
if [ "$USE_THREADS_API" = true ]; then
    python scripts/threads_api_poster.py data/2025-07-31/thread_post.json
    if [ $? -eq 0 ]; then
        echo "✅ Threads API 테스트 완료"
    else
        echo "⚠️ Threads API 테스트 실패 (예상됨 - API 엔드포인트 미공개)"
    fi
else
    echo "⚠️ Threads API 환경변수가 설정되지 않아 건너뜁니다."
fi

echo ""

# 6. 통합 파이프라인 테스트
echo "6️⃣ 통합 파이프라인 테스트..."
python scripts/buffer_uploader.py morning data/2025-07-31/slides_2025-07-31.json
if [ $? -eq 0 ]; then
    echo "✅ 통합 파이프라인 테스트 완료"
else
    echo "❌ 통합 파이프라인 테스트 실패"
    exit 1
fi

echo ""
echo "🎉 모든 테스트 완료!"
echo ""
echo "📋 생성된 파일들:"
echo "   📄 data/2025-07-31/slides_2025-07-31.json"
echo "   📄 data/2025-07-31/thread_post.json"
echo "   🖼️  data/2025-07-31/preview/slide_01.png ~ slide_06.png"
echo ""
echo "🔍 미리보기 확인:"
echo "   open data/2025-07-31/preview/"
echo ""
echo "📋 다음 단계:"
echo "   1. Facebook 앱 설정 및 권한 획득"
echo "   2. Threads API 환경변수 설정"
echo "   3. 실제 스케줄러 실행" 