# 🔍 Threads API 연구 결과

## 📋 현재 상황

### ✅ 확인된 정보
- **Threads 토큰**: `THAARmSGNd...` (202자)
- **Instagram User ID**: `24521613984110254`
- **Meta에서 공식 Threads API 지원**: 확인됨

### ❌ 발견된 문제들
1. **토큰 파싱 오류**: "Invalid OAuth access token - Cannot parse access token"
2. **API 엔드포인트 불확실**: Threads API의 정확한 엔드포인트 미확인
3. **인증 방식 차이**: Threads API가 Facebook Graph API와 다른 인증 방식 사용 가능

## 🚀 시도한 방법들

### 1. Facebook Graph API 엔드포인트
```
GET https://graph.facebook.com/v18.0/me
GET https://graph.facebook.com/v18.0/{IG_USER_ID}/connected_threads_user
GET https://graph.facebook.com/v18.0/{IG_USER_ID}/threads
GET https://graph.facebook.com/v18.0/me/threads
```
**결과**: 토큰 파싱 오류

### 2. Threads 전용 API 엔드포인트
```
GET https://www.threads.net/api/v1/threads
```
**결과**: 404 오류 (페이지 없음)

## 🔍 다음 연구 방향

### 1. Meta 공식 Threads API 문서 확인
- Meta 개발자 콘솔에서 Threads API 문서 검색
- Threads 전용 API 엔드포인트 확인
- 인증 방식 및 토큰 형식 확인

### 2. Threads API 토큰 생성 방법
- Threads 전용 앱 생성
- Threads API 권한 설정
- 올바른 토큰 형식 확인

### 3. 대안 방법들
- **Selenium 자동화**: 브라우저 자동화로 포스팅
- **Buffer API**: Buffer를 통해 Threads 포스팅
- **Meta 공식 API 발표 대기**: Threads API가 완전히 공개될 때까지 대기

## 📞 지원 리소스

- **Meta 개발자 콘솔**: https://developers.facebook.com/
- **Threads API 문서**: (아직 공개되지 않음)
- **Instagram Graph API**: https://developers.facebook.com/docs/instagram-api/

## 🎯 권장사항

1. **Meta 개발자 콘솔에서 Threads API 문서 확인**
2. **Threads 전용 앱 생성 및 권한 설정**
3. **올바른 Threads API 토큰 생성**
4. **Threads 전용 API 엔드포인트 확인**

## 📝 참고사항

- Threads API는 아직 베타 단계일 수 있음
- Meta에서 점진적으로 API 기능을 공개할 가능성
- 현재로서는 Selenium 자동화가 가장 안정적인 방법 