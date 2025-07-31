# 🔐 Threads API 권한 설정 확장 가이드

## 📋 현재 상황
- **Threads API 연결**: ✅ 성공 (`graph.threads.net/v1.0/`)
- **메인 포스트 작성**: ✅ 성공
- **댓글 작성**: ⚠️ 권한 확장 필요

## 🚀 Threads API 권한 확장 방법

### 1. Meta 개발자 콘솔 접속
```
https://developers.facebook.com/
```

### 2. Threads API 앱 설정
1. **앱 선택**: Threads API를 사용할 앱 선택
2. **제품 추가**: "Threads API" 제품 추가
3. **권한 설정**: 필요한 권한들 추가

### 3. 필수 권한 목록

#### **기본 권한**
- `threads_basic` - 기본 Threads 접근 권한
- `threads_content_publish` - Threads 콘텐츠 발행 권한

#### **고급 권한**
- `threads_reply_management` - 댓글 관리 권한
- `threads_insights` - 인사이트 데이터 접근 권한
- `threads_webhooks` - 웹훅 설정 권한

### 4. 권한별 기능

| 권한 | 기능 | 필요성 |
|------|------|--------|
| `threads_basic` | 기본 읽기/쓰기 | 필수 |
| `threads_content_publish` | 포스트 발행 | 필수 |
| `threads_reply_management` | 댓글 작성/관리 | 댓글 기능용 |
| `threads_insights` | 인사이트 데이터 | 분석용 |
| `threads_webhooks` | 실시간 알림 | 모니터링용 |

### 5. 앱 검토 신청
1. **각 권한별로 검토 신청**
2. **사용 사례 설명**: 자동화된 금융 뉴스 포스팅
3. **데모 영상/스크린샷**: 실제 사용 예시 제공

## 🔧 현재 코드 개선사항

### 댓글 작성 API (공식 문서 기반)
```python
# 1단계: 댓글 컨테이너 생성
POST https://graph.threads.net/v1.0/me/threads
{
    "text": "댓글 내용",
    "media_type": "text",
    "reply_to_id": "메인포스트ID",
    "access_token": "토큰"
}

# 2단계: 댓글 발행 (30초 대기 후)
POST https://graph.threads.net/v1.0/{USER_ID}/threads_publish
{
    "creation_id": "컨테이너ID",
    "access_token": "토큰"
}
```

### 인사이트 API
```python
# Threads 인사이트 데이터 조회
GET https://graph.threads.net/v1.0/{USER_ID}/insights
{
    "metric": "impressions,reach,profile_views",
    "access_token": "토큰"
}
```

## 📊 권한 확장 후 기대 효과

### ✅ **완전한 자동화**
- 메인 포스트 자동 발행
- 댓글 자동 작성
- 인사이트 데이터 수집
- 실시간 모니터링

### 📈 **분석 기능**
- 포스트 성과 분석
- 최적 발행 시간 파악
- 콘텐츠 효과 측정

## 🎯 다음 단계

1. **Meta 개발자 콘솔에서 권한 확장**
2. **앱 검토 신청 및 승인 대기**
3. **확장된 권한으로 코드 테스트**
4. **완전한 자동화 시스템 구축**

## 📞 참고 자료

- [Threads API 공식 문서](https://developers.facebook.com/docs/threads/)
- [Create Replies API](https://developers.facebook.com/docs/threads/retrieve-and-manage-replies/create-replies)
- [Threads API 권한 가이드](https://developers.facebook.com/docs/threads/get-started)

## ⚠️ 주의사항

- **권한 승인**: 일부 권한은 Meta 검토 필요
- **사용 제한**: API 호출 제한 확인
- **개인정보**: 사용자 데이터 처리 시 개인정보 보호 준수 