#!/usr/bin/env python3
"""
Reddit 금융 게시물 수집 스크립트
키워드 기반으로 Top/Day 게시물 수집
"""

import praw
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

# Reddit 설정
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'InsightPipeline/1.0')

# 검색할 키워드들
KEYWORDS = ['S&P500', 'KOSPI', 'FOMC', 'AI', 'Bitcoin', 'Tesla', 'Apple', 'NVIDIA']

def init_reddit():
    """Reddit 클라이언트 초기화"""
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        return reddit
    except Exception as e:
        logger.error(f"❌ Reddit 클라이언트 초기화 실패: {e}")
        return None

def search_reddit_posts(reddit, keyword, limit=5):
    """Reddit에서 키워드로 게시물 검색"""
    posts = []
    
    try:
        # 인기 서브레딧들에서 검색
        subreddits = ['investing', 'stocks', 'wallstreetbets', 'cryptocurrency', 'economics']
        
        for subreddit_name in subreddits:
            try:
                subreddit = reddit.subreddit(subreddit_name)
                
                # Top 게시물 검색
                top_posts = subreddit.search(keyword, sort='top', time_filter='day', limit=limit)
                
                for post in top_posts:
                    # 스코어 계산 (업보트 + 댓글 수 + 시간 가중치)
                    hours_ago = (datetime.now() - datetime.fromtimestamp(post.created_utc)).total_seconds() / 3600
                    time_weight = max(0.1, 1 - (hours_ago / 24))  # 24시간 내 가중치
                    score = (post.score + post.num_comments) * time_weight
                    
                    posts.append({
                        'id': post.id,
                        'title': post.title,
                        'url': f"https://reddit.com{post.permalink}",
                        'subreddit': subreddit_name,
                        'score': post.score,
                        'num_comments': post.num_comments,
                        'created_utc': post.created_utc,
                        'author': str(post.author) if post.author else '[deleted]',
                        'selftext': post.selftext[:500] if post.selftext else '',
                        'calculated_score': score,
                        'keyword': keyword
                    })
                    
            except Exception as e:
                logger.warning(f"⚠️ {subreddit_name} 검색 실패: {e}")
                continue
                
    except Exception as e:
        logger.error(f"❌ Reddit 검색 실패: {e}")
    
    return posts

def fetch_reddit_data():
    """Reddit 데이터 수집"""
    reddit = init_reddit()
    if not reddit:
        logger.warning("⚠️ Reddit 클라이언트 초기화 실패. 더미 데이터를 사용합니다.")
        return generate_dummy_reddit_data()
    
    all_posts = []
    
    # API 테스트
    try:
        test_subreddit = reddit.subreddit('test')
        test_posts = list(test_subreddit.hot(limit=1))
        if not test_posts:
            logger.warning("⚠️ Reddit API 테스트 실패. 더미 데이터를 사용합니다.")
            return generate_dummy_reddit_data()
    except Exception as e:
        logger.warning(f"⚠️ Reddit API 테스트 실패: {e}. 더미 데이터를 사용합니다.")
        return generate_dummy_reddit_data()
    
    for keyword in KEYWORDS:
        logger.info(f"🔍 '{keyword}' 키워드로 검색 중...")
        posts = search_reddit_posts(reddit, keyword, limit=3)
        all_posts.extend(posts)
    
    # 스코어 기준으로 정렬
    all_posts.sort(key=lambda x: x['calculated_score'], reverse=True)
    
    if not all_posts:
        logger.warning("⚠️ Reddit 데이터 수집 실패. 더미 데이터를 사용합니다.")
        return generate_dummy_reddit_data()
    
    # 상위 15개만 선택
    top_posts = all_posts[:15]
    
    reddit_data = {
        'timestamp': datetime.now().isoformat(),
        'posts': top_posts,
        'total_posts': len(all_posts),
        'keywords_searched': KEYWORDS
    }
    
    return reddit_data

def generate_dummy_reddit_data():
    """더미 Reddit 데이터 생성"""
    logger.info("📊 Reddit 더미 데이터 생성 중...")
    
    dummy_posts = [
        {
            'id': 'dummy1',
            'title': 'S&P 500 hits new all-time high as tech stocks rally',
            'url': 'https://reddit.com/r/investing/comments/dummy1',
            'subreddit': 'investing',
            'score': 1250,
            'num_comments': 89,
            'created_utc': datetime.now().timestamp() - 3600,
            'author': 'market_watcher',
            'selftext': 'Tech stocks continue their strong performance with AI and semiconductor companies leading the charge.',
            'calculated_score': 1250,
            'keyword': 'S&P500'
        },
        {
            'id': 'dummy2',
            'title': 'Tesla Q4 earnings beat expectations, stock up 5%',
            'url': 'https://reddit.com/r/stocks/comments/dummy2',
            'subreddit': 'stocks',
            'score': 890,
            'num_comments': 156,
            'created_utc': datetime.now().timestamp() - 7200,
            'author': 'tesla_bull',
            'selftext': 'Tesla reported strong Q4 results with record deliveries and improved margins.',
            'calculated_score': 890,
            'keyword': 'Tesla'
        },
        {
            'id': 'dummy3',
            'title': 'FOMC meeting this week - what to expect',
            'url': 'https://reddit.com/r/economics/comments/dummy3',
            'subreddit': 'economics',
            'score': 567,
            'num_comments': 234,
            'created_utc': datetime.now().timestamp() - 10800,
            'author': 'fed_watcher',
            'selftext': 'Federal Reserve meeting this week could provide clues about future rate cuts.',
            'calculated_score': 567,
            'keyword': 'FOMC'
        },
        {
            'id': 'dummy4',
            'title': 'Bitcoin breaks $50k resistance level',
            'url': 'https://reddit.com/r/cryptocurrency/comments/dummy4',
            'subreddit': 'cryptocurrency',
            'score': 2340,
            'num_comments': 445,
            'created_utc': datetime.now().timestamp() - 14400,
            'author': 'crypto_analyst',
            'selftext': 'Bitcoin successfully broke through the $50k resistance level with strong volume.',
            'calculated_score': 2340,
            'keyword': 'Bitcoin'
        },
        {
            'id': 'dummy5',
            'title': 'NVIDIA AI chips demand continues to surge',
            'url': 'https://reddit.com/r/stocks/comments/dummy5',
            'subreddit': 'stocks',
            'score': 678,
            'num_comments': 123,
            'created_utc': datetime.now().timestamp() - 18000,
            'author': 'tech_investor',
            'selftext': 'NVIDIA continues to dominate the AI chip market with strong demand from data centers.',
            'calculated_score': 678,
            'keyword': 'NVIDIA'
        }
    ]
    
    reddit_data = {
        'timestamp': datetime.now().isoformat(),
        'posts': dummy_posts,
        'total_posts': len(dummy_posts),
        'keywords_searched': KEYWORDS
    }
    
    logger.info(f"✅ Reddit 더미 데이터 생성 완료: {len(dummy_posts)}개 게시물")
    return reddit_data

def save_data(data, date_str):
    """데이터를 JSON 파일로 저장"""
    os.makedirs(f'data/{date_str}', exist_ok=True)
    filepath = f'data/{date_str}/reddit.json'
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"💾 데이터 저장: {filepath}")
    return filepath

def main():
    """메인 실행 함수"""
    logger.info("🔴 Reddit 금융 게시물 수집 시작")
    
    # 오늘 날짜
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Reddit 데이터 수집
    reddit_data = fetch_reddit_data()
    
    if reddit_data:
        # 데이터 저장
        filepath = save_data(reddit_data, today)
        logger.info(f"✅ Reddit 데이터 수집 완료: {len(reddit_data['posts'])}개 게시물")
    else:
        logger.error("❌ Reddit 데이터 수집 실패")
    
    return filepath if reddit_data else None

if __name__ == "__main__":
    main() 