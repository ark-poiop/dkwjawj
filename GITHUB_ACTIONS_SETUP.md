# GitHub Actions 설정 가이드

## 개요
이 프로젝트는 GitHub Actions를 통해 자동으로 스케줄링된 시장 데이터 파이프라인을 실행합니다.

## 스케줄 시간 (KST 기준)
- **아침**: 07:05 - 미국 시장 데이터 수집 및 요약
- **점심**: 15:40 - 한국 시장 종가 데이터 수집 및 요약  
- **저녁**: 20:00 - Reddit 데이터 수집 및 뉴스 필터링

## GitHub Secrets 설정

### 1. 저장소 설정
1. GitHub 저장소로 이동: https://github.com/ark-poiop/dkwjawj
2. Settings → Secrets and variables → Actions 클릭
3. "New repository secret" 버튼 클릭

### 2. 필수 Secrets 추가

#### API Keys
```
OPENAI_API_KEY=your_openai_api_key_here
NEWS_API_KEY=your_newsapi_key_here
FRED_API_KEY=your_fred_api_key
```

#### Reddit API (선택사항)
```
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_reddit_user_agent
```

#### Buffer API
```
BUFFER_ACCESS_TOKEN=your_buffer_access_token
BUFFER_PROFILE_ID=your_buffer_profile_id
```

#### Threads API (직접 포스팅)
```
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token
IG_USER_ID=your_instagram_user_id
USE_THREADS_API=true
THREADS_USERNAME=your_threads_username
THREADS_PASSWORD=your_threads_password
USE_THREADS_AUTO=false
```

**Threads API 설정 방법:**
1. Facebook 개발자 계정 생성: https://developers.facebook.com/
2. 새 앱 생성 → Threads API 선택
3. Graph API Explorer에서 액세스 토큰 생성
4. Instagram User ID 확인 (Instagram API 또는 온라인 도구 사용)

## 워크플로우 파일 구조

### `.github/workflows/scheduler.yml`
- 스케줄링 설정
- 환경 변수 설정
- 파이프라인 실행
- 아티팩트 업로드

### `scripts/github_scheduler.py`
- GitHub Actions 최적화된 스케줄러
- 환경 변수 검증
- 로깅 개선
- Threads API 직접 포스팅 통합

### `scripts/threads_api_poster.py`
- Threads API를 통한 직접 포스팅
- 메인 포스트 및 댓글 자동 작성
- 인사이트 데이터 수집

## 수동 실행
GitHub Actions 페이지에서 "Run workflow" 버튼을 클릭하여 수동으로 실행할 수 있습니다:
- 세션 타입 선택: morning, afternoon, evening

## 모니터링
- Actions 탭에서 실행 상태 확인
- 로그에서 상세한 실행 정보 확인
- 아티팩트에서 생성된 데이터 다운로드

## 문제 해결

### 일반적인 문제들
1. **환경 변수 누락**: 모든 필수 Secrets가 설정되었는지 확인
2. **API 키 만료**: API 키가 유효한지 확인
3. **의존성 문제**: requirements.txt의 패키지들이 올바른지 확인

### 로그 확인
- GitHub Actions 실행 로그에서 오류 메시지 확인
- 각 단계별 실행 상태 확인

## 보안 고려사항
- API 키는 절대 코드에 하드코딩하지 마세요
- GitHub Secrets를 통해서만 민감한 정보 관리
- 정기적으로 API 키를 로테이션하세요

## 로컬 테스트
로컬에서 테스트하려면:
```bash
# 환경 변수 설정
export OPENAI_API_KEY=your_key
export NEWS_API_KEY=your_key
# ... 기타 환경 변수

# 스케줄러 실행
python scripts/github_scheduler.py morning
``` 