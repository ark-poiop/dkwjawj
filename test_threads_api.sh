#!/bin/bash

echo "🤖 Threads API 테스트 시작"
echo "=================================="
echo "📅 테스트 날짜: $(date +%Y-%m-%d)"
echo ""

# 1. 환경변수 확인
echo "1️⃣ 환경변수 확인..."
if [ -z "$FACEBOOK_ACCESS_TOKEN" ]; then
    echo "⚠️ FACEBOOK_ACCESS_TOKEN 환경변수가 설정되지 않았습니다."
    echo "다음 명령어로 환경변수를 설정해주세요:"
    echo "export FACEBOOK_ACCESS_TOKEN='your_facebook_access_token'"
    echo ""
    echo "또는 .env 파일에 추가해주세요:"
    echo "FACEBOOK_ACCESS_TOKEN=your_facebook_access_token"
    exit 1
fi

if [ -z "$IG_USER_ID" ]; then
    echo "⚠️ IG_USER_ID 환경변수가 설정되지 않았습니다."
    echo "다음 명령어로 환경변수를 설정해주세요:"
    echo "export IG_USER_ID='your_instagram_user_id'"
    echo ""
    echo "또는 .env 파일에 추가해주세요:"
    echo "IG_USER_ID=your_instagram_user_id"
    exit 1
fi

echo "✅ 환경변수 설정 확인 완료"
echo ""

# 2. Thread 데이터 확인
echo "2️⃣ Thread 데이터 확인..."
if [ ! -f "data/2025-07-31/thread_post.json" ]; then
    echo "❌ Thread 데이터 파일이 없습니다: data/2025-07-31/thread_post.json"
    echo "먼저 파이프라인을 실행하여 데이터를 생성해주세요."
    exit 1
fi

echo "✅ Thread 데이터 존재: data/2025-07-31/thread_post.json"
echo ""

# 3. Python 패키지 확인
echo "3️⃣ Python 패키지 확인..."
python -c "import requests; print('✅ requests 설치됨:', requests.__version__)" 2>/dev/null || {
    echo "❌ requests 패키지가 설치되지 않았습니다."
    echo "다음 명령어로 설치해주세요:"
    echo "pip install requests"
    exit 1
}

python -c "import dotenv; print('✅ python-dotenv 설치됨:', dotenv.__version__)" 2>/dev/null || {
    echo "❌ python-dotenv 패키지가 설치되지 않았습니다."
    echo "다음 명령어로 설치해주세요:"
    echo "pip install python-dotenv"
    exit 1
}

echo "✅ 필요한 패키지 모두 설치됨"
echo ""

# 4. Threads API 테스트
echo "4️⃣ Threads API 테스트..."
echo "🔗 연결된 Threads 계정 조회 중..."

python scripts/threads_api_poster.py data/2025-07-31/thread_post.json

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Threads API 테스트 성공!"
    echo ""
    echo "📋 다음 단계:"
    echo "1. Facebook 앱에서 필요한 권한 확인"
    echo "   - instagram_basic"
    echo "   - threads_business_basic"
    echo "   - pages_read_engagement"
    echo ""
    echo "2. Instagram 계정이 Threads에 연결되어 있는지 확인"
    echo "3. 비즈니스 계정 역할 확인 (Advertiser, Manager, Content Creator)"
    echo ""
else
    echo ""
    echo "❌ Threads API 테스트 실패"
    echo ""
    echo "🔍 문제 해결 방법:"
    echo "1. Facebook 앱 권한 확인"
    echo "2. Instagram 계정과 Threads 연결 확인"
    echo "3. 액세스 토큰 유효성 확인"
    echo "4. API 엔드포인트 확인 (Meta에서 공식 발표 대기)"
    echo ""
fi 