#!/bin/bash

# Threads 자동 포스팅 테스트 스크립트

echo "🤖 Threads 자동 포스팅 테스트 시작"
echo "=================================="

# 현재 날짜
TODAY=$(date +%Y-%m-%d)
echo "📅 테스트 날짜: $TODAY"

# 1. Thread 데이터 확인
echo ""
echo "1️⃣ Thread 데이터 확인..."
thread_file="data/$TODAY/thread_post.json"

if [ -f "$thread_file" ]; then
    echo "✅ Thread 데이터 존재: $thread_file"
else
    echo "❌ Thread 데이터 없음: $thread_file"
    echo "먼저 ./test_pipeline.sh를 실행하여 데이터를 생성해주세요."
    exit 1
fi

# 2. 환경 변수 확인
echo ""
echo "2️⃣ 환경 변수 확인..."
if [ -z "$THREADS_USERNAME" ] || [ -z "$THREADS_PASSWORD" ]; then
    echo "⚠️ Threads 로그인 정보가 설정되지 않았습니다."
    echo "다음 명령어로 환경 변수를 설정해주세요:"
    echo "export THREADS_USERNAME='your_username'"
    echo "export THREADS_PASSWORD='your_password'"
    echo ""
    echo "또는 .env 파일에 추가해주세요:"
    echo "THREADS_USERNAME=your_username"
    echo "THREADS_PASSWORD=your_password"
    exit 1
else
    echo "✅ Threads 로그인 정보 설정됨"
fi

# 3. Selenium 패키지 설치 확인
echo ""
echo "3️⃣ Selenium 패키지 설치 확인..."
python -c "import selenium; print('✅ Selenium 설치됨')" 2>/dev/null || {
    echo "❌ Selenium이 설치되지 않았습니다."
    echo "다음 명령어로 설치해주세요:"
    echo "pip install selenium webdriver-manager"
    exit 1
}

# 4. Threads 자동 포스팅 테스트
echo ""
echo "4️⃣ Threads 자동 포스팅 테스트..."
echo "🔐 브라우저가 열리고 로그인 과정이 시작됩니다."
echo "⚠️ 처음 실행 시 ChromeDriver 다운로드가 필요할 수 있습니다."

python scripts/threads_poster.py "$thread_file"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Threads 자동 포스팅 테스트 완료!"
    echo "✅ 포스팅이 성공적으로 완료되었습니다."
else
    echo ""
    echo "❌ Threads 자동 포스팅 테스트 실패"
    echo "로그를 확인하여 문제를 해결해주세요."
fi

echo ""
echo "📝 사용법:"
echo "  # 수동 실행"
echo "  python scripts/threads_poster.py data/$TODAY/thread_post.json"
echo ""
echo "  # 자동 모드 (Buffer 업로더와 함께)"
echo "  export USE_THREADS_AUTO=true"
echo "  python scripts/buffer_uploader.py morning data/$TODAY/slides_$TODAY.json" 