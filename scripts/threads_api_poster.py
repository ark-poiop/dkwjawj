#!/usr/bin/env python3
"""
Threads API를 사용한 자동 포스팅 스크립트
Meta의 공식 Threads API를 활용하여 포스팅을 자동화합니다.
"""

import os
import json
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ThreadsAPIPoster:
    def __init__(self):
        """Threads API 포스터 초기화"""
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.ig_user_id = os.getenv('IG_USER_ID')
        self.threads_user_id = None
        
        if not self.access_token:
            raise ValueError("FACEBOOK_ACCESS_TOKEN 환경변수가 설정되지 않았습니다.")
        
        if not self.ig_user_id:
            raise ValueError("IG_USER_ID 환경변수가 설정되지 않았습니다.")
        
        logger.info("✅ Threads API 포스터 초기화 완료")
    
    def get_connected_threads_user(self):
        """Instagram 계정에 연결된 Threads 사용자 ID 가져오기"""
        try:
            # 토큰 유효성 검사
            if len(self.access_token) < 50:
                logger.warning("⚠️ 액세스 토큰이 너무 짧습니다. 올바른 Facebook 액세스 토큰을 설정해주세요.")
                logger.info("📋 Facebook Graph API Explorer에서 200자 이상의 토큰을 생성하세요.")
                logger.info("🔗 https://developers.facebook.com/tools/explorer/")
                
                # 더미 테스트용 ID 설정
                if self.ig_user_id:
                    self.threads_user_id = self.ig_user_id
                    logger.info(f"✅ 더미 테스트용 Threads 사용자 ID 설정: {self.threads_user_id}")
                    return True
                else:
                    return False
            
            # 토큰 형식 검사 (Threads 토큰은 THAAR로 시작할 수 있음)
            if not (self.access_token.startswith('EAAB') or self.access_token.startswith('THAAR')):
                logger.warning("⚠️ Threads 액세스 토큰 형식이 올바르지 않습니다.")
                logger.info("📋 Threads API에서 올바른 토큰을 생성하세요.")
                
                # 더미 테스트용 ID 설정
                if self.ig_user_id:
                    self.threads_user_id = self.ig_user_id
                    logger.info(f"✅ 더미 테스트용 Threads 사용자 ID 설정: {self.threads_user_id}")
                    return True
                else:
                    return False
            
            # Threads API 엔드포인트 (Meta Graph API v1.0 사용)
            url = "https://graph.threads.net/v1.0/me"
            params = {
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data:
                    self.threads_user_id = data['id']
                    logger.info(f"✅ Threads 사용자 ID 획득: {self.threads_user_id}")
                    return True
                elif 'data' in data and len(data['data']) > 0:
                    self.threads_user_id = data['data'][0]['id']
                    logger.info(f"✅ Threads 사용자 ID 획득: {self.threads_user_id}")
                    return True
                else:
                    logger.warning("⚠️ 연결된 Threads 계정이 없습니다.")
                    # Instagram User ID를 Threads User ID로 사용
                    if self.ig_user_id:
                        self.threads_user_id = self.ig_user_id
                        logger.info(f"✅ Instagram User ID를 Threads User ID로 사용: {self.threads_user_id}")
                        return True
                    return False
            else:
                logger.error(f"❌ Threads 사용자 ID 조회 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Threads 사용자 ID 조회 중 오류: {e}")
            return False
    
    def post_thread(self, main_text, comment_text=None):
        """Threads에 포스트 작성"""
        try:
            # Threads 사용자 ID 확인
            if not self.threads_user_id:
                if not self.get_connected_threads_user():
                    logger.error("❌ Threads 사용자 ID를 가져올 수 없습니다.")
                    return False
            
            # 메인 포스트 작성
            logger.info("📝 Threads 메인 포스트 작성 시작...")
            
            # 현재로서는 실제 포스팅 API가 공개되지 않았으므로
            # 연결된 Threads 계정 정보만 확인하고 시뮬레이션
            logger.info(f"✅ Threads 계정 연결 확인: {self.threads_user_id}")
            logger.info(f"📝 메인 포스트 내용: {main_text[:100]}...")
            
            if comment_text:
                logger.info(f"💬 댓글 내용: {comment_text[:100]}...")
            
            # Threads API 포스팅 엔드포인트
            url = f"https://graph.threads.net/v1.0/{self.threads_user_id}/threads"
            payload = {
                'access_token': self.access_token,
                'text': main_text,  # message 대신 text 사용
                'media_type': 'text'  # 텍스트 포스트 타입
            }
            response = requests.post(url, data=payload)
            
            if response.status_code == 200:
                result = response.json()
                creation_id = result.get('id')
                logger.info(f"✅ Threads 메인 포스트 컨테이너 생성 성공: {creation_id}")
                
                # 2단계: 메인 포스트 발행
                logger.info("🚀 메인 포스트 발행 중...")
                publish_url = f"https://graph.threads.net/v1.0/{self.threads_user_id}/threads_publish"
                publish_params = {
                    'creation_id': creation_id,
                    'access_token': self.access_token
                }
                
                publish_response = requests.post(publish_url, data=publish_params)
                
                if publish_response.status_code == 200:
                    publish_result = publish_response.json()
                    post_id = publish_result.get('id')
                    logger.info(f"✅ Threads 메인 포스트 발행 성공: {post_id}")
                else:
                    logger.error(f"❌ 메인 포스트 발행 실패: {publish_response.status_code} - {publish_response.text}")
                    return False
                
                # 댓글 작성 (있는 경우) - 공식 API 방식
                if comment_text and post_id:
                    logger.info("💬 Threads 댓글 작성 시작...")
                    
                    # 1단계: 댓글 컨테이너 생성 (다른 방법 시도)
                    comment_url = f"https://graph.threads.net/v1.0/{self.threads_user_id}/threads"
                    comment_payload = {
                        'access_token': self.access_token,
                        'text': comment_text,
                        'media_type': 'text',
                        'reply_to_id': post_id  # 메인 포스트에 댓글 달기
                    }
                    
                    comment_response = requests.post(comment_url, data=comment_payload)
                    
                    if comment_response.status_code == 200:
                        comment_result = comment_response.json()
                        creation_id = comment_result.get('id')
                        logger.info(f"✅ 댓글 컨테이너 생성 성공: {creation_id}")
                        
                        # 2단계: 댓글 발행 (즉시 발행)
                        logger.info("🚀 댓글 즉시 발행...")
                        
                        publish_url = f"https://graph.threads.net/v1.0/{self.threads_user_id}/threads_publish"
                        publish_params = {
                            'creation_id': creation_id,
                            'access_token': self.access_token
                        }
                        
                        publish_response = requests.post(publish_url, data=publish_params)
                        
                        if publish_response.status_code == 200:
                            publish_result = publish_response.json()
                            logger.info(f"✅ Threads 댓글 발행 성공: {publish_result.get('id')}")
                        else:
                            logger.warning(f"⚠️ 댓글 발행 실패: {publish_response.status_code}")
                    else:
                        logger.warning(f"⚠️ 댓글 컨테이너 생성 실패: {comment_response.status_code}")
                
                return True
            else:
                logger.error(f"❌ Threads 포스트 작성 실패: {response.status_code} - {response.text}")
                return False
            
            logger.info("🎉 Threads API 포스팅 시뮬레이션 완료!")
            logger.info("📋 실제 포스팅을 위해서는 Meta에서 공식 API 엔드포인트 발표 대기 필요")
            
            return True
                
        except Exception as e:
            logger.error(f"❌ Threads 포스트 작성 중 오류: {e}")
            return False
    
    def get_threads_insights(self):
        """Threads 인사이트 데이터 가져오기"""
        try:
            if not self.threads_user_id:
                if not self.get_connected_threads_user():
                    return None
            
            url = f"https://graph.facebook.com/v18.0/{self.threads_user_id}/insights"
            params = {
                'access_token': self.access_token,
                'metric': 'impressions,reach,profile_views'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Threads 인사이트 데이터 획득")
                return data
            else:
                logger.warning(f"⚠️ Threads 인사이트 조회 실패: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Threads 인사이트 조회 중 오류: {e}")
            return None

def main():
    """메인 실행 함수"""
    import sys
    
    if len(sys.argv) != 2:
        print("사용법: python threads_api_poster.py <slides_file.json>")
        sys.exit(1)
    
    slides_file = sys.argv[1]
    
    if not os.path.exists(slides_file):
        logger.error(f"❌ 파일을 찾을 수 없습니다: {slides_file}")
        sys.exit(1)
    
    try:
        # 슬라이드 파일 읽기
        with open(slides_file, 'r', encoding='utf-8') as f:
            slides_data = json.load(f)
        
        # Threads API 포스터 초기화
        poster = ThreadsAPIPoster()
        
        # 포스트 데이터 추출
        if 'thread' in slides_data:
            main_text = slides_data['thread'].get('main', '')
            comment_text = slides_data['thread'].get('comment', '')
        else:
            logger.error("❌ thread 섹션이 슬라이드 데이터에 없습니다.")
            sys.exit(1)
        
        if not main_text:
            logger.error("❌ 메인 포스트 텍스트가 없습니다.")
            sys.exit(1)
        
        logger.info(f"📝 메인 포스트 길이: {len(main_text)}자")
        if comment_text:
            logger.info(f"💬 댓글 길이: {len(comment_text)}자")
        
        # 포스트 작성
        success = poster.post_thread(main_text, comment_text)
        
        if success:
            logger.info("🎉 Threads API 포스팅 완료!")
            
            # 인사이트 데이터 가져오기 (선택사항)
            insights = poster.get_threads_insights()
            if insights:
                logger.info("📊 인사이트 데이터:")
                logger.info(json.dumps(insights, indent=2, ensure_ascii=False))
        else:
            logger.error("❌ Threads API 포스팅 실패")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ 실행 중 오류: {e}")
        import traceback
        logger.error(f"📄 상세 오류: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 