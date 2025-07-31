#!/usr/bin/env python3
"""
메인 스케줄러 스크립트
아침/점심/저녁 세션별 파이프라인 실행
"""

import subprocess
import os
import sys
import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 스크립트 경로
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

def run_command(command, description):
    """명령어 실행"""
    logger.info(f"🚀 {description} 시작")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {description} 완료")
            if result.stdout:
                logger.info(f"📄 출력: {result.stdout.strip()}")
            return True
        else:
            logger.error(f"❌ {description} 실패")
            if result.stderr:
                logger.error(f"📄 오류: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        logger.error(f"❌ {description} 실행 중 오류: {e}")
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
    
    logger.info("✅ 아침 파이프라인 완료 (Threads만)")
    return True

def afternoon_pipeline():
    """점심 파이프라인 (15:35 실행)"""
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
    
    logger.info("✅ 점심 파이프라인 완료 (Threads만)")
    return True

def evening_pipeline():
    """저녁 파이프라인 (20:10 실행)"""
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
    
    logger.info("✅ 저녁 파이프라인 완료 (Threads만)")
    return True

def run_single_session(session_type):
    """단일 세션 실행"""
    if session_type == "morning":
        return morning_pipeline()
    elif session_type == "afternoon":
        return afternoon_pipeline()
    elif session_type == "evening":
        return evening_pipeline()
    else:
        logger.error(f"❌ 잘못된 세션 타입: {session_type}")
        return False

def start_scheduler():
    """스케줄러 시작"""
    scheduler = BlockingScheduler(timezone='Asia/Seoul')
    
    # 아침 파이프라인 (07:05)
    scheduler.add_job(
        morning_pipeline,
        CronTrigger(hour=7, minute=5),
        id='morning_pipeline',
        name='아침 파이프라인'
    )
    
    # 점심 파이프라인 (15:40)
    scheduler.add_job(
        afternoon_pipeline,
        CronTrigger(hour=15, minute=40),
        id='afternoon_pipeline',
        name='점심 파이프라인'
    )
    
    # 저녁 파이프라인 (20:00)
    scheduler.add_job(
        evening_pipeline,
        CronTrigger(hour=20, minute=0),
        id='evening_pipeline',
        name='저녁 파이프라인'
    )
    
    logger.info("⏰ 스케줄러 시작")
    logger.info("📅 예약된 작업:")
    logger.info("  - 아침 파이프라인: 매일 07:05")
    logger.info("  - 점심 파이프라인: 매일 15:40")
    logger.info("  - 저녁 파이프라인: 매일 20:00")
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("🛑 스케줄러 중지")
        scheduler.shutdown()

def main():
    """메인 함수"""
    if len(sys.argv) > 1:
        # 단일 세션 실행
        session_type = sys.argv[1]
        logger.info(f"🎯 단일 세션 실행: {session_type}")
        success = run_single_session(session_type)
        sys.exit(0 if success else 1)
    else:
        # 스케줄러 모드
        logger.info("🔄 스케줄러 모드로 시작")
        start_scheduler()

if __name__ == "__main__":
    main() 