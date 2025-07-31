#!/bin/bash

# GitHub Actions 테스트 스크립트
# 로컬에서 GitHub Actions와 동일한 환경을 시뮬레이션

echo "🧪 GitHub Actions 테스트 시작"

# 환경 변수 확인
echo "📋 환경 변수 확인..."
required_vars=(
    "OPENAI_API_KEY"
    "NEWS_API_KEY"
    "BUFFER_ACCESS_TOKEN"
    "BUFFER_PROFILE_ID"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ $var 환경 변수가 설정되지 않았습니다"
        exit 1
    else
        echo "✅ $var 설정됨"
    fi
done

# 데이터 디렉토리 생성
echo "📁 데이터 디렉토리 생성..."
mkdir -p data/$(date +%Y-%m-%d)
mkdir -p logs

# GitHub Actions 스케줄러 테스트
echo "🚀 GitHub Actions 스케줄러 테스트..."

# 세션 타입 선택
if [ "$1" = "morning" ] || [ "$1" = "afternoon" ] || [ "$1" = "evening" ]; then
    session_type=$1
else
    echo "사용법: $0 [morning|afternoon|evening]"
    echo "예시: $0 morning"
    exit 1
fi

echo "🎯 세션 타입: $session_type"

# 스케줄러 실행
python scripts/github_scheduler.py $session_type

if [ $? -eq 0 ]; then
    echo "✅ 테스트 성공!"
    echo "📊 생성된 데이터 확인:"
    ls -la data/$(date +%Y-%m-%d)/
else
    echo "❌ 테스트 실패"
    exit 1
fi 