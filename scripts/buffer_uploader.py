#!/usr/bin/env python3
"""
Buffer 업로더 스크립트
Buffer Publish API v2를 사용하여 IG Carousel과 Threads 포스트 업로드
"""

import requests
import json
import os
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Buffer API 설정
BUFFER_ACCESS_TOKEN = os.getenv('BUFFER_ACCESS_TOKEN')
BUFFER_PROFILE_ID = os.getenv('BUFFER_PROFILE_ID')
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'

# Threads 자동 포스팅 설정
USE_THREADS_AUTO = os.getenv('USE_THREADS_AUTO', 'false').lower() == 'true'
USE_THREADS_API = os.getenv('USE_THREADS_API', 'true').lower() == 'true'  # API 방식 우선
THREADS_USERNAME = os.getenv('THREADS_USERNAME')
THREADS_PASSWORD = os.getenv('THREADS_PASSWORD')
FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')
IG_USER_ID = os.getenv('IG_USER_ID')

def get_scheduled_time(session_type):
    """세션별 예약 시간 계산"""
    now = datetime.now()
    
    if session_type == "morning":
        # 아침 7:30 KST
        scheduled_time = now.replace(hour=7, minute=30, second=0, microsecond=0)
        if scheduled_time <= now:
            scheduled_time += timedelta(days=1)
    elif session_type == "afternoon":
        # 점심 16:05 KST
        scheduled_time = now.replace(hour=16, minute=5, second=0, microsecond=0)
        if scheduled_time <= now:
            scheduled_time += timedelta(days=1)
    elif session_type == "evening":
        # 저녁 21:00 KST
        scheduled_time = now.replace(hour=21, minute=0, second=0, microsecond=0)
        if scheduled_time <= now:
            scheduled_time += timedelta(days=1)
    else:
        # 기본값: 1시간 후
        scheduled_time = now + timedelta(hours=1)
    
    return scheduled_time.isoformat()

def upload_instagram_carousel(image_paths, caption, scheduled_time):
    """Instagram Carousel 업로드"""
    if DRY_RUN:
        logger.info("🔍 DRY RUN 모드: Instagram Carousel 업로드 시뮬레이션")
        logger.info(f"📸 이미지 파일들: {image_paths}")
        logger.info(f"📝 캡션: {caption}")
        logger.info(f"⏰ 예약 시간: {scheduled_time}")
        return True
    
    try:
        # Buffer API v2 - Instagram Carousel 업로드
        url = "https://api.bufferapp.com/1/updates/create.json"
        
        headers = {
            'Authorization': f'Bearer {BUFFER_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # 이미지 파일들을 Base64로 인코딩
        import base64
        media_files = []
        
        for image_path in image_paths:
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                    base64_data = base64.b64encode(image_data).decode('utf-8')
                    media_files.append({
                        'photo': base64_data,
                        'description': ''
                    })
        
        if not media_files:
            logger.error("❌ 업로드할 이미지가 없습니다")
            return False
        
        payload = {
            'profile_ids[]': BUFFER_PROFILE_ID,
            'text': caption,
            'media': json.dumps(media_files),
            'scheduled_at': scheduled_time,
            'metadata': {
                'link': '',
                'description': caption
            }
        }
        
        response = requests.post(url, headers=headers, data=payload)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Instagram Carousel 업로드 성공: {result.get('id')}")
            return True
        else:
            logger.error(f"❌ Instagram Carousel 업로드 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Instagram Carousel 업로드 중 오류: {e}")
        return False

def upload_threads_post(thread_data, scheduled_time):
    """Threads 포스트 업로드"""
    if DRY_RUN:
        logger.info("🔍 DRY RUN 모드: Threads 포스트 업로드 시뮬레이션")
        logger.info(f"📝 메인 포스트: {thread_data.get('main', '')}")
        logger.info(f"💬 댓글: {thread_data.get('comment', '')}")
        logger.info(f"⏰ 예약 시간: {scheduled_time}")
        return True
    
    try:
        # Buffer API v2 - Threads 포스트 업로드
        url = "https://api.bufferapp.com/1/updates/create.json"
        
        headers = {
            'Authorization': f'Bearer {BUFFER_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # 메인 포스트
        main_text = thread_data.get('main', '')
        comment_text = thread_data.get('comment', '')
        
        payload = {
            'profile_ids[]': BUFFER_PROFILE_ID,
            'text': main_text,
            'scheduled_at': scheduled_time,
            'metadata': {
                'link': '',
                'description': main_text
            }
        }
        
        response = requests.post(url, headers=headers, data=payload)
        
        if response.status_code == 200:
            result = response.json()
            post_id = result.get('id')
            logger.info(f"✅ Threads 메인 포스트 업로드 성공: {post_id}")
            
            # 댓글 업로드 (첫 번째 댓글)
            if comment_text:
                comment_payload = {
                    'profile_ids[]': BUFFER_PROFILE_ID,
                    'text': comment_text,
                    'scheduled_at': scheduled_time,
                    'metadata': {
                        'link': '',
                        'description': comment_text
                    }
                }
                
                comment_response = requests.post(url, headers=headers, data=comment_payload)
                
                if comment_response.status_code == 200:
                    comment_result = comment_response.json()
                    logger.info(f"✅ Threads 댓글 업로드 성공: {comment_result.get('id')}")
                else:
                    logger.warning(f"⚠️ Threads 댓글 업로드 실패: {comment_response.status_code}")
            
            return True
        else:
            logger.error(f"❌ Threads 포스트 업로드 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Threads 포스트 업로드 중 오류: {e}")
        return False

def main():
    """메인 실행 함수"""
    import sys
    
    if len(sys.argv) != 3:
        logger.error("❌ 사용법: python buffer_uploader.py [session_type] [slides_json_file]")
        return None
    
    session_type = sys.argv[1]
    slides_file = sys.argv[2]
    
    if not os.path.exists(slides_file):
        logger.error(f"❌ 슬라이드 파일 없음: {slides_file}")
        return None
    
    # 슬라이드 데이터 로드
    with open(slides_file, 'r', encoding='utf-8') as f:
        slides_data = json.load(f)
    
    # Thread 데이터 로드
    date_str = slides_file.split('/')[-2] if '/' in slides_file else datetime.now().strftime('%Y-%m-%d')
    thread_file = f'data/{date_str}/thread_post.json'
    
    if not os.path.exists(thread_file):
        logger.error(f"❌ Thread 파일 없음: {thread_file}")
        return None
    
    with open(thread_file, 'r', encoding='utf-8') as f:
        thread_data = json.load(f)
    
    # 예약 시간 계산
    scheduled_time = get_scheduled_time(session_type)
    
    logger.info(f"📤 Buffer 업로드 시작: {session_type} 세션")
    logger.info(f"⏰ 예약 시간: {scheduled_time}")
    
    # 이미지 파일 경로들
    preview_dir = f'data/{date_str}/preview'
    image_paths = []
    
    for i in range(1, 7):
        image_path = os.path.join(preview_dir, f'slide_{i:02d}.png')
        if os.path.exists(image_path):
            image_paths.append(image_path)
    
    if not image_paths:
        logger.error("❌ 업로드할 이미지가 없습니다")
        return None
    
    # Instagram Carousel 업로드 (비활성화)
    logger.info("🚫 Instagram Carousel 업로드 비활성화됨")
    carousel_success = True  # 항상 성공으로 처리
    
    # Threads 포스트 업로드
    if USE_THREADS_API and FACEBOOK_ACCESS_TOKEN and IG_USER_ID:
        logger.info("🤖 Threads API 자동 포스팅 시작...")
        try:
            from threads_api_poster import ThreadsAPIPoster
            
            poster = ThreadsAPIPoster()
            threads_success = poster.post_thread(
                thread_data['thread']['main'], 
                thread_data['thread']['comment']
            )
        except Exception as e:
            logger.error(f"❌ Threads API 자동 포스팅 실패: {e}")
            threads_success = False
    elif USE_THREADS_AUTO:
        logger.info("🤖 Threads Selenium 자동 포스팅 시작...")
        try:
            from threads_poster import ThreadsPoster
            
            poster = ThreadsPoster(headless=True)
            if poster.setup_driver():
                if poster.login_to_threads():
                    threads_success = poster.post_thread(
                        thread_data['thread']['main'], 
                        thread_data['thread']['comment']
                    )
                    poster.close()
                else:
                    threads_success = False
                    poster.close()
            else:
                threads_success = False
        except Exception as e:
            logger.error(f"❌ Threads Selenium 자동 포스팅 실패: {e}")
            threads_success = False
    else:
        threads_success = upload_threads_post(thread_data['thread'], scheduled_time)
    
    if carousel_success and threads_success:
        logger.info("✅ Buffer 업로드 완료 (Threads만)")
        return True
    else:
        logger.error("❌ Buffer 업로드 실패")
        return False

if __name__ == "__main__":
    main() 