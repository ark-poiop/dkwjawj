#!/usr/bin/env python3
"""
뉴스 데이터 중복 제거 및 필터링 스크립트
기사 길이, 중복 제거, 스코어 계산
"""

import json
import os
from datetime import datetime
import logging
from difflib import SequenceMatcher
import re

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def calculate_similarity(text1, text2):
    """두 텍스트 간의 유사도 계산"""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def clean_text(text):
    """텍스트 정제"""
    if not text:
        return ""
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    # 특수문자 정리
    text = re.sub(r'[^\w\s가-힣]', ' ', text)
    # 연속 공백 제거
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def filter_articles(articles, min_length=200, similarity_threshold=0.8):
    """기사 필터링 및 중복 제거"""
    filtered_articles = []
    
    for article in articles:
        # 텍스트 정제
        title = clean_text(article.get('title', ''))
        content = clean_text(article.get('content', ''))
        
        # 길이 체크
        if len(title + content) < min_length:
            continue
        
        # 중복 체크
        is_duplicate = False
        for existing in filtered_articles:
            existing_title = clean_text(existing.get('title', ''))
            existing_content = clean_text(existing.get('content', ''))
            
            title_similarity = calculate_similarity(title, existing_title)
            content_similarity = calculate_similarity(content, existing_content)
            
            if title_similarity > similarity_threshold or content_similarity > similarity_threshold:
                is_duplicate = True
                break
        
        if not is_duplicate:
            # 스코어 계산
            score = calculate_article_score(article)
            article['cleaned_title'] = title
            article['cleaned_content'] = content
            article['filtered_score'] = score
            filtered_articles.append(article)
    
    return filtered_articles

def calculate_article_score(article):
    """기사 스코어 계산"""
    score = 0
    
    # 기본 점수
    score += 10
    
    # 제목 길이 가중치
    title_length = len(article.get('title', ''))
    if 20 <= title_length <= 100:
        score += 5
    elif title_length > 100:
        score += 2
    
    # 내용 길이 가중치
    content_length = len(article.get('content', ''))
    if 200 <= content_length <= 1000:
        score += 10
    elif content_length > 1000:
        score += 15
    
    # 키워드 가중치
    keywords = ['S&P500', 'KOSPI', 'FOMC', 'AI', 'Bitcoin', 'Tesla', 'Apple', 'NVIDIA']
    title_lower = article.get('title', '').lower()
    content_lower = article.get('content', '').lower()
    
    for keyword in keywords:
        if keyword.lower() in title_lower:
            score += 3
        if keyword.lower() in content_lower:
            score += 1
    
    # 시간 가중치 (최신 기사 우선)
    if 'published_at' in article:
        try:
            published_time = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00'))
            hours_ago = (datetime.now() - published_time).total_seconds() / 3600
            time_weight = max(0.1, 1 - (hours_ago / 24))  # 24시간 내 가중치
            score *= time_weight
        except:
            pass
    
    return round(score, 2)

def process_reddit_data(reddit_file):
    """Reddit 데이터를 뉴스 형태로 변환"""
    try:
        with open(reddit_file, 'r', encoding='utf-8') as f:
            reddit_data = json.load(f)
        
        articles = []
        for post in reddit_data.get('posts', []):
            article = {
                'title': post.get('title', ''),
                'content': post.get('selftext', ''),
                'source': f"Reddit r/{post.get('subreddit', '')}",
                'url': post.get('url', ''),
                'score': post.get('score', 0),
                'comments': post.get('num_comments', 0),
                'published_at': datetime.fromtimestamp(post.get('created_utc', 0)).isoformat(),
                'author': post.get('author', ''),
                'keyword': post.get('keyword', '')
            }
            articles.append(article)
        
        return articles
        
    except Exception as e:
        logger.error(f"❌ Reddit 데이터 처리 실패: {e}")
        return []

def save_clean_data(articles, date_str):
    """정제된 데이터 저장"""
    os.makedirs(f'data/{date_str}', exist_ok=True)
    filepath = f'data/{date_str}/clean_news.json'
    
    clean_data = {
        'timestamp': datetime.now().isoformat(),
        'articles': articles,
        'total_articles': len(articles)
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"💾 정제된 데이터 저장: {filepath}")
    return filepath

def main():
    """메인 실행 함수"""
    logger.info("🔍 뉴스 데이터 정제 및 필터링 시작")
    
    # 오늘 날짜
    today = datetime.now().strftime('%Y-%m-%d')
    reddit_file = f'data/{today}/reddit.json'
    
    if not os.path.exists(reddit_file):
        logger.error(f"❌ Reddit 데이터 파일 없음: {reddit_file}")
        return None
    
    # Reddit 데이터를 뉴스 형태로 변환
    articles = process_reddit_data(reddit_file)
    
    if not articles:
        logger.error("❌ 처리할 기사가 없습니다")
        return None
    
    logger.info(f"📰 총 {len(articles)}개 기사 처리 시작")
    
    # 필터링 및 중복 제거
    filtered_articles = filter_articles(articles)
    
    # 스코어 기준으로 정렬
    filtered_articles.sort(key=lambda x: x['filtered_score'], reverse=True)
    
    # 상위 5개만 선택
    top_articles = filtered_articles[:5]
    
    logger.info(f"✅ 필터링 완료: {len(top_articles)}개 기사 선택")
    
    # 정제된 데이터 저장
    filepath = save_clean_data(top_articles, today)
    
    return filepath

if __name__ == "__main__":
    main() 