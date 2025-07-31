#!/usr/bin/env python3
"""
Threads 자동 포스팅 스크립트
Selenium을 사용하여 Threads에 자동으로 포스팅
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import json
import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ThreadsPoster:
    def __init__(self, headless=True):
        """Threads 포스터 초기화"""
        self.driver = None
        self.headless = headless
        self.wait = None
        
        # Threads 로그인 정보
        self.username = os.getenv('THREADS_USERNAME')
        self.password = os.getenv('THREADS_PASSWORD')
        
        if not self.username or not self.password:
            logger.error("❌ Threads 로그인 정보가 설정되지 않았습니다.")
            logger.error("env.example 파일에서 THREADS_USERNAME과 THREADS_PASSWORD를 설정해주세요.")
            raise ValueError("Threads 로그인 정보 필요")
    
    def setup_driver(self):
        """Chrome 드라이버 설정"""
        try:
            chrome_options = Options()
            
            # headless 모드 비활성화 (자동화 감지 방지)
            # if self.headless:
            #     chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # 자동화 감지 방지 옵션들
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 자동 다운로드 ChromeDriver
            service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            
            # 자동화 감지 방지 스크립트 실행
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ Chrome 드라이버 설정 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ Chrome 드라이버 설정 실패: {e}")
            return False
    
    def login_to_threads(self):
        """Threads 로그인"""
        try:
            logger.info("🔐 Threads 로그인 시작...")
            
            # Threads 로그인 페이지로 이동
            self.driver.get("https://www.threads.net/login")
            time.sleep(3)
            
            # Instagram 로그인으로 리다이렉트되는 경우
            if "instagram.com" in self.driver.current_url:
                logger.info("📱 Instagram 로그인 페이지로 리다이렉트됨")
                
                # 사용자명 입력
                username_field = self.wait.until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )
                username_field.clear()
                username_field.send_keys(self.username)
                
                # 비밀번호 입력
                password_field = self.driver.find_element(By.NAME, "password")
                password_field.clear()
                password_field.send_keys(self.password)
                
                # 로그인 버튼 클릭
                login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                login_button.click()
                
                # 로그인 완료 대기
                time.sleep(5)
                
                # Threads로 다시 이동
                self.driver.get("https://www.threads.net")
                time.sleep(3)
            
            logger.info("✅ Threads 로그인 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ Threads 로그인 실패: {e}")
            return False
    
    def post_thread(self, main_text, comment_text=None):
        """Threads에 포스트 작성"""
        try:
            logger.info("📝 Threads 포스트 작성 시작...")
            
            # Threads 홈페이지로 이동 (여러 URL 시도)
            urls_to_try = [
                "https://www.threads.net",
                "https://threads.net",
                "https://www.instagram.com/threads",
                "https://www.instagram.com"
            ]
            
            for url in urls_to_try:
                try:
                    logger.info(f"🔗 {url} 접속 시도...")
                    self.driver.get(url)
                    time.sleep(5)
                    
                    # 현재 URL 확인
                    current_url = self.driver.current_url
                    logger.info(f"📍 현재 URL: {current_url}")
                    
                    # Threads 관련 페이지인지 확인
                    if "threads" in current_url or "instagram" in current_url:
                        break
                        
                except Exception as e:
                    logger.warning(f"⚠️ {url} 접속 실패: {e}")
                    continue
            
            # 더 정확한 선택자들로 포스트 입력 영역 찾기
            textarea_selectors = [
                "//textarea[@placeholder]",
                "//div[@contenteditable='true']",
                "//div[@role='textbox']",
                "//textarea",
                "//div[contains(@class, 'composer')]//textarea",
                "//div[contains(@class, 'post')]//textarea",
                "//div[contains(@class, 'input')]//textarea",
                "//div[contains(@class, 'editor')]//textarea",
                "//div[contains(@class, 'write')]//textarea",
                "//div[contains(@class, 'create')]//textarea",
                "//div[@data-testid='post-composer']//textarea",
                "//div[contains(@aria-label, 'post')]//textarea",
                "//div[contains(@aria-label, 'compose')]//textarea"
            ]
            
            textarea = None
            for selector in textarea_selectors:
                try:
                    textarea = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    logger.info(f"✅ 포스트 입력 영역 발견: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not textarea:
                logger.error("❌ 포스트 입력 영역을 찾을 수 없습니다")
                # 현재 페이지의 HTML 구조를 로그로 출력
                logger.info("🔍 현재 페이지 HTML 구조:")
                logger.info(self.driver.page_source[:1000])
                return False
            
            # 포스트 입력 (자연스러운 타이핑 시뮬레이션)
            textarea.click()
            time.sleep(2)
            textarea.clear()
            time.sleep(1)
            
            # 텍스트를 천천히 입력 (자연스러운 타이핑)
            for char in main_text:
                textarea.send_keys(char)
                time.sleep(0.01)  # 10ms 간격으로 타이핑
            
            time.sleep(3)  # 입력 완료 후 대기
            
            # 포스트 버튼 찾기
            post_button_selectors = [
                "//button[contains(text(), 'Post')]",
                "//div[@role='button' and contains(text(), 'Post')]",
                "//button[@type='submit']",
                "//div[contains(@class, 'post') and @role='button']",
                "//button[contains(@class, 'post')]"
            ]
            
            post_button = None
            for selector in post_button_selectors:
                try:
                    post_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    logger.info(f"✅ 포스트 버튼 발견: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if post_button:
                post_button.click()
                time.sleep(3)
                logger.info("✅ 메인 포스트 작성 완료")
            else:
                logger.error("❌ 포스트 버튼을 찾을 수 없습니다")
                return False
            
            # 댓글 작성 (있는 경우)
            if comment_text:
                logger.info("💬 댓글 작성 시작...")
                
                # 댓글 버튼 찾기
                comment_selectors = [
                    "//div[contains(text(), 'Reply')]",
                    "//button[contains(text(), 'Reply')]",
                    "//div[@role='button' and contains(text(), 'Reply')]"
                ]
                
                comment_button = None
                for selector in comment_selectors:
                    try:
                        comment_button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        break
                    except TimeoutException:
                        continue
                
                if comment_button:
                    comment_button.click()
                    time.sleep(2)
                    
                    # 댓글 텍스트 영역 찾기
                    comment_textarea = self.wait.until(
                        EC.presence_of_element_located((By.TAG_NAME, "textarea"))
                    )
                    comment_textarea.clear()
                    comment_textarea.send_keys(comment_text)
                    
                    # 댓글 포스트 버튼 클릭
                    reply_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Reply')]")
                    reply_button.click()
                    
                    logger.info("✅ 댓글 작성 완료")
                else:
                    logger.warning("⚠️ 댓글 버튼을 찾을 수 없어 댓글 작성 건너뜀")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Threads 포스트 작성 실패: {e}")
            return False
    
    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 브라우저 종료")

def load_thread_data(thread_file):
    """Thread 데이터 로드"""
    try:
        with open(thread_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        main_text = data['thread']['main']
        comment_text = data['thread']['comment']
        
        return main_text, comment_text
        
    except Exception as e:
        logger.error(f"❌ Thread 데이터 로드 실패: {e}")
        return None, None

def main():
    """메인 실행 함수"""
    import sys
    
    if len(sys.argv) != 2:
        logger.error("❌ 사용법: python threads_poster.py [thread_json_file]")
        return False
    
    thread_file = sys.argv[1]
    
    if not os.path.exists(thread_file):
        logger.error(f"❌ Thread 파일 없음: {thread_file}")
        return False
    
    # Thread 데이터 로드
    main_text, comment_text = load_thread_data(thread_file)
    
    if not main_text:
        logger.error("❌ Thread 데이터를 로드할 수 없습니다")
        return False
    
    # Threads 포스터 초기화
    poster = ThreadsPoster(headless=False)  # 디버깅을 위해 headless=False
    
    try:
        # 드라이버 설정
        if not poster.setup_driver():
            return False
        
        # 로그인
        if not poster.login_to_threads():
            return False
        
        # 포스트 작성
        if not poster.post_thread(main_text, comment_text):
            return False
        
        logger.info("🎉 Threads 포스팅 완료!")
        return True
        
    except Exception as e:
        logger.error(f"❌ 포스팅 중 오류: {e}")
        return False
    
    finally:
        poster.close()

if __name__ == "__main__":
    main() 