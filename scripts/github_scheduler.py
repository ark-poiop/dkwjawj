#!/usr/bin/env python3
"""
GitHub Actions용 스케줄러 스크립트
환경 변수와 로깅을 GitHub Actions에 최적화
"""

import subprocess
import os
import sys
import logging
from datetime import datetime
import time

# 로깅 설정 (GitHub Actions에 최적화)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 스크립트 경로
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

def run_command(command, description):
    """명령어 실행"""
    logger.info(f"🚀 {description} 시작")
    logger.info(f"📝 실행 명령: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding='utf-8',
            env=os.environ.copy()
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {description} 완료")
            if result.stdout:
                logger.info(f"📄 출력: {result.stdout.strip()}")
            return True
        else:
            logger.error(f"❌ {description} 실패 (종료 코드: {result.returncode})")
            if result.stdout:
                logger.error(f"📄 표준 출력: {result.stdout.strip()}")
            if result.stderr:
                logger.error(f"📄 오류 출력: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        logger.error(f"❌ {description} 실행 중 예외 발생: {e}")
        import traceback
        logger.error(f"📄 상세 오류: {traceback.format_exc()}")
        return False

def morning_pipeline():
    """아침 파이프라인 (07:05 실행)"""
    logger.info("🌅 아침 파이프라인 시작")
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 1. 미국 시장 데이터 수집
    if not run_command(
        f"python scripts/fetch_us_markets.py",
        "미국 시장 데이터 수집"
    ):
        return False
    
    # 2. GPT 요약
    if not run_command(
        f"python scripts/gpt_summarize.py morning",
        "GPT 요약 (아침)"
    ):
        return False
    
    # 3. Carousel 이미지 생성
    slides_file = f"data/{today}/slides_{today}.json"
    if not run_command(
        f"python scripts/local_carousel.py {slides_file}",
        "Carousel 이미지 생성"
    ):
        return False
    
    # 4. Buffer 업로드
    if not run_command(
        f"python scripts/buffer_uploader.py morning {slides_file}",
        "Buffer 업로드 (아침)"
    ):
        return False
    
    logger.info("✅ 아침 파이프라인 완료")
    return True

def afternoon_pipeline():
    """점심 파이프라인 (15:40 실행)"""
    logger.info("🇰🇷 점심 파이프라인 시작")
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 1. 한국 시장 종가 데이터 수집
    if not run_command(
        f"python scripts/fetch_kr_close.py",
        "한국 시장 종가 데이터 수집"
    ):
        return False
    
    # 2. GPT 요약
    if not run_command(
        f"python scripts/gpt_summarize.py afternoon",
        "GPT 요약 (점심)"
    ):
        return False
    
    # 3. Carousel 이미지 생성
    slides_file = f"data/{today}/slides_{today}.json"
    if not run_command(
        f"python scripts/local_carousel.py {slides_file}",
        "Carousel 이미지 생성"
    ):
        return False
    
    # 4. Buffer 업로드
    if not run_command(
        f"python scripts/buffer_uploader.py afternoon {slides_file}",
        "Buffer 업로드 (점심)"
    ):
        return False
    
    logger.info("✅ 점심 파이프라인 완료")
    return True

def evening_pipeline():
    """저녁 파이프라인 (20:00 실행)"""
    logger.info("🌙 저녁 파이프라인 시작")
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 1. Reddit 데이터 수집
    if not run_command(
        f"python scripts/fetch_reddit.py",
        "Reddit 데이터 수집"
    ):
        return False
    
    # 2. 뉴스 필터링
    if not run_command(
        f"python scripts/dedup_filter.py",
        "뉴스 필터링"
    ):
        return False
    
    # 3. GPT 요약
    if not run_command(
        f"python scripts/gpt_summarize.py evening",
        "GPT 요약 (저녁)"
    ):
        return False
    
    # 4. Carousel 이미지 생성
    slides_file = f"data/{today}/slides_{today}.json"
    if not run_command(
        f"python scripts/local_carousel.py {slides_file}",
        "Carousel 이미지 생성"
    ):
        return False
    
    # 5. Buffer 업로드
    if not run_command(
        f"python scripts/buffer_uploader.py evening {slides_file}",
        "Buffer 업로드 (저녁)"
    ):
        return False
    
    logger.info("✅ 저녁 파이프라인 완료")
    return True

def run_single_session(session_type):
    """단일 세션 실행"""
    logger.info(f"🎯 세션 타입: {session_type}")
    
    if session_type == "morning":
        return morning_pipeline()
    elif session_type == "afternoon":
        return afternoon_pipeline()
    elif session_type == "evening":
        return evening_pipeline()
    else:
        logger.error(f"❌ 잘못된 세션 타입: {session_type}")
        return False

def main():
    """메인 함수"""
    try:
        # 환경 변수 확인
        required_env_vars = [
            'OPENAI_API_KEY',
            'NEWS_API_KEY',
            'BUFFER_ACCESS_TOKEN',
            'BUFFER_PROFILE_ID'
        ]
        
        logger.info("🔍 환경 변수 검증 시작")
        missing_vars = []
        for var in required_env_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
                logger.error(f"❌ {var}: 설정되지 않음")
            else:
                logger.info(f"✅ {var}: {value[:10]}...")
        
        if missing_vars:
            logger.error(f"❌ 필수 환경 변수가 누락되었습니다: {', '.join(missing_vars)}")
            logger.error("GitHub Secrets에서 해당 변수들을 설정해주세요.")
            return 1
        
        logger.info("✅ 모든 필수 환경 변수가 설정되었습니다.")
        
        if len(sys.argv) > 1:
            # 단일 세션 실행
            session_type = sys.argv[1]
            logger.info(f"🎯 단일 세션 실행: {session_type}")
            success = run_single_session(session_type)
            return 0 if success else 1
        else:
            logger.error("❌ 세션 타입을 지정해주세요 (morning/afternoon/evening)")
            return 1
            
    except Exception as e:
        logger.error(f"❌ 메인 함수에서 예외 발생: {e}")
        import traceback
        logger.error(f"📄 상세 오류: {traceback.format_exc()}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 