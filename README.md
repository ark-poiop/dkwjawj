# 📊 Daily "아·점·저" Insight Pipeline

매일 아침·점심·저녁에 자동으로 생성되는 금융 시장 인사이트 파이프라인입니다.

## 🎯 목표

1. **🌅 아침 07:30 KST**: Overnight Market Brief (S&P500·NASDAQ·달러·유가·BTC 지표)
2. **🇰🇷 점심 16:05 KST**: K-Close Recap (KOSPI·KOSDAQ 종가, 외인/기관 수급, 업종 히트맵)
3. **🌙 저녁 21:00 KST**: Tonight's Watchlist (금일 주요 뉴스·실적·매크로 일정)

각 시간대별로 **IG Carousel 6장** PNG (1080×1350)와 **Threads** 본문 ≤500자 + 첫 댓글 ≤500자 텍스트를 생성하여 Buffer에 예약 업로드합니다.

## 🛠️ 기술 스택

- **Python 3.10+** with venv `insight_env`
- **무료/저비용 소스만 사용**
  - NewsAPI Free (500 req/일)
  - Yahoo Finance HTML parse → 야간·장마감 지수
  - KRX 일별 시세 CSV (data.go.kr)
  - Reddit OAuth Top·Day (100 req/분)
  - FRED 매크로 지표
- **GPT-4o** 모델 사용
- **Buffer Publish API v2** for scheduling
- **Selenium** for Threads auto-posting

## 📁 프로젝트 구조

```
dkwjawj/
├── scripts/
│   ├── scheduler.py          # 메인 스케줄러
│   ├── fetch_us_markets.py   # 미국 시장 데이터 수집
│   ├── fetch_kr_close.py     # 한국 시장 종가 데이터 수집
│   ├── fetch_reddit.py       # Reddit 데이터 수집
│   ├── dedup_filter.py       # 뉴스 필터링 및 중복 제거
│   ├── gpt_summarize.py      # GPT 요약 및 인사이트 생성
│   ├── local_carousel.py     # Carousel 이미지 생성
│   ├── buffer_uploader.py    # Buffer 업로드
│   └── threads_poster.py     # Threads 자동 포스팅
├── data/
│   └── YYYY-MM-DD/
│       ├── raw_us.json       # 미국 시장 원본 데이터
│       ├── raw_kr.json       # 한국 시장 원본 데이터
│       ├── reddit.json       # Reddit 원본 데이터
│       ├── clean_news.json   # 정제된 뉴스 데이터
│       ├── slides_YYYY-MM-DD.json  # 슬라이드 데이터
│       ├── thread_post.json  # Thread 포스트 데이터
│       └── preview/
│           ├── slide_01.png  # Carousel 이미지들
│           ├── slide_02.png
│           └── ...
├── requirements.txt          # Python 패키지 의존성
├── env.example              # 환경 변수 샘플
└── README.md               # 프로젝트 문서
```

## 🚀 설치 및 설정

### 1. 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv insight_env
source insight_env/bin/activate  # macOS/Linux
# 또는
insight_env\Scripts\activate     # Windows

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
# env.example을 .env로 복사
cp env.example .env

# .env 파일 편집하여 API 키들 설정
```

필요한 API 키들:
- `OPENAI_API_KEY`: OpenAI API 키
- `NEWS_API_KEY`: NewsAPI 키 (선택사항)
- `REDDIT_CLIENT_ID`: Reddit OAuth 클라이언트 ID
- `REDDIT_CLIENT_SECRET`: Reddit OAuth 클라이언트 시크릿
- `REDDIT_USER_AGENT`: Reddit 사용자 에이전트
- `BUFFER_ACCESS_TOKEN`: Buffer API 액세스 토큰
- `BUFFER_PROFILE_ID`: Buffer 프로필 ID
- `FRED_API_KEY`: FRED API 키 (선택사항)
- `THREADS_USERNAME`: Threads 사용자명
- `THREADS_PASSWORD`: Threads 비밀번호

### 3. 폰트 설정 (한글 지원)

시스템에 한글 폰트가 설치되어 있어야 합니다:
- **macOS**: AppleSDGothicNeo (기본 설치)
- **Windows**: Malgun Gothic (기본 설치)
- **Linux**: DejaVu Sans (기본 설치)

## 🎮 사용법

### 로컬 실행
```bash
# 전체 스케줄러 시작
python scripts/scheduler.py

# 단일 세션 실행
python scripts/scheduler.py morning    # 아침 파이프라인
python scripts/scheduler.py afternoon  # 점심 파이프라인
python scripts/scheduler.py evening    # 저녁 파이프라인
```

### GitHub Actions 자동 실행
이 프로젝트는 GitHub Actions를 통해 자동으로 스케줄링됩니다.

#### 스케줄 시간 (KST 기준)
- **아침**: 07:05 - 미국 시장 데이터 수집 및 요약
- **점심**: 15:40 - 한국 시장 종가 데이터 수집 및 요약  
- **저녁**: 20:00 - Reddit 데이터 수집 및 뉴스 필터링

#### 설정 방법
1. GitHub 저장소로 이동: https://github.com/ark-poiop/dkwjawj
2. Settings → Secrets and variables → Actions
3. 필요한 API 키들을 Secrets로 추가
4. 자세한 설정 방법은 [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) 참조

#### 수동 실행
GitHub Actions 페이지에서 "Run workflow" 버튼을 클릭하여 수동으로 실행할 수 있습니다.



### 개별 스크립트 실행

```bash
# 데이터 수집
python scripts/fetch_us_markets.py
python scripts/fetch_kr_close.py
python scripts/fetch_reddit.py

# 데이터 처리
python scripts/dedup_filter.py
python scripts/gpt_summarize.py morning

# 이미지 생성
python scripts/local_carousel.py data/2025-01-15/slides_2025-01-15.json

# 업로드
python scripts/buffer_uploader.py morning data/2025-01-15/slides_2025-01-15.json

# Threads 자동 포스팅
python scripts/threads_poster.py data/2025-01-15/thread_post.json
```

## 🧪 테스트

### 더미 데이터로 테스트

프로젝트에 포함된 더미 데이터를 사용하여 전체 파이프라인을 테스트할 수 있습니다:

```bash
# 1. 더미 데이터 확인
ls data/2025-01-15/

# 2. GPT 요약 테스트
python scripts/gpt_summarize.py morning

# 3. Carousel 이미지 생성 테스트
python scripts/local_carousel.py data/2025-01-15/slides_2025-01-15.json

# 4. Buffer 업로드 테스트 (DRY RUN)
python scripts/buffer_uploader.py morning data/2025-01-15/slides_2025-01-15.json
```

### 로컬 미리보기

생성된 이미지들은 `data/YYYY-MM-DD/preview/` 디렉토리에서 확인할 수 있습니다.

### Threads 자동 포스팅 테스트

```bash
# Threads 자동 포스팅 테스트
./test_threads_posting.sh

# 수동 실행
python scripts/threads_poster.py data/2025-07-31/thread_post.json

# 자동 모드 (Buffer 업로더와 함께)
export USE_THREADS_AUTO=true
python scripts/buffer_uploader.py morning data/2025-07-31/slides_2025-07-31.json
```

## 📊 출력 예시

### 슬라이드 구성 (6장)

1. **헤드라인 + 지수 그래프**
2. **핵심 데이터·리스트**
3. **핵심 데이터·리스트**
4. **핵심 데이터·리스트**
5. **Reddit Hot-Take 카드**
6. **🔖 저장 CTA "내일 아침에도 인사이트!"**

### Threads 포스트

- **본문**: ≤500자, 질문형 마무리
- **첫 댓글**: ≤500자, Reddit quote + CTA

## 🔧 설정 옵션

### 환경 변수

- `DRY_RUN=true`: 실제 업로드 대신 시뮬레이션만 실행
- `TIMEZONE=Asia/Seoul`: 시간대 설정

### 스케줄 시간 조정

`scheduler.py`에서 각 세션의 실행 시간을 조정할 수 있습니다:

```python
# 아침 파이프라인 (07:05)
scheduler.add_job(morning_pipeline, CronTrigger(hour=7, minute=5))

# 점심 파이프라인 (15:35)
scheduler.add_job(afternoon_pipeline, CronTrigger(hour=15, minute=35))

# 저녁 파이프라인 (20:10)
scheduler.add_job(evening_pipeline, CronTrigger(hour=20, minute=10))
```

## 🐛 문제 해결

### 일반적인 문제들

1. **폰트 오류**: 시스템에 한글 폰트가 설치되어 있는지 확인
2. **API 키 오류**: `.env` 파일의 API 키들이 올바르게 설정되었는지 확인
3. **권한 오류**: 스크립트 실행 권한 확인 (`chmod +x scripts/*.py`)

### 로그 확인

모든 스크립트는 상세한 로그를 출력합니다. 오류 발생 시 로그를 확인하여 문제를 진단할 수 있습니다.

## 📈 모니터링

### 성공적인 실행 로그 예시

```
🗓️ 07:30 Overnight Brief ▶️ IG/Threads scheduled (dry-run)
✅ 미국 시장 데이터 수집 완료
✅ GPT 요약 완료
✅ Carousel 생성 완료
✅ Buffer 업로드 완료
```

## 🤝 기여

프로젝트 개선을 위한 제안이나 버그 리포트는 언제든 환영합니다!

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 