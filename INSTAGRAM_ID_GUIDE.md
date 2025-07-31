# 🔍 Instagram User ID 찾기 가이드

## 📋 현재 상황
- Facebook 액세스 토큰: 설정됨
- Instagram User ID: `1238360997607491` (현재 설정)
- Buffer Profile ID: `your_buffer_profile_id` (설정 필요)

## 🚀 Instagram User ID 찾는 방법

### 방법 1: Facebook Graph API Explorer 사용

1. **Graph API Explorer 접속**
   ```
   https://developers.facebook.com/tools/explorer/
   ```

2. **앱 선택 및 토큰 설정**
   - 생성한 Facebook 앱 선택
   - 액세스 토큰 설정

3. **Instagram 계정 정보 조회**
   ```
   GET /me/accounts?fields=instagram_business_account
   ```

4. **응답 예시**
   ```json
   {
     "data": [
       {
         "id": "123456789",
         "name": "My Page",
         "instagram_business_account": {
           "id": "987654321",
           "username": "my_instagram"
         }
       }
     ]
   }
   ```

### 방법 2: Instagram Business Account ID 직접 조회

1. **Instagram 계정이 Professional 계정인지 확인**
   - Instagram 앱 → 설정 → 계정 → Professional 계정으로 전환

2. **Facebook Business Manager 연결**
   - Facebook Business Manager에서 Instagram 계정 연결

3. **Graph API로 조회**
   ```
   GET /me/accounts?fields=instagram_business_account,instagram_basic
   ```

### 방법 3: 온라인 도구 사용

1. **Instagram User ID Finder**
   ```
   https://codeofaninja.com/tools/find-instagram-user-id/
   ```

2. **사용법**
   - Instagram 사용자명 입력
   - User ID 확인

## 🔧 환경변수 설정

### .env 파일 업데이트
```bash
# Instagram User ID (실제 ID로 교체)
IG_USER_ID=987654321

# Buffer Profile ID (실제 ID로 교체)
BUFFER_PROFILE_ID=123456789

# Facebook 액세스 토큰
FACEBOOK_ACCESS_TOKEN=EAABwzLixnjYBO... (200자 이상)

# Threads API 사용 설정
USE_THREADS_API=true
```

## 🧪 ID 유효성 테스트

### 1. Instagram User ID 테스트
```bash
curl "https://graph.facebook.com/v18.0/IG_USER_ID?access_token=FACEBOOK_ACCESS_TOKEN"
```

### 2. Buffer Profile ID 테스트
```bash
curl "https://api.bufferapp.com/1/profiles.json?access_token=BUFFER_ACCESS_TOKEN"
```

## ⚠️ 주의사항

### Instagram User ID vs Buffer Profile ID
- **Instagram User ID**: Instagram 계정의 고유 식별자
- **Buffer Profile ID**: Buffer에서 연결된 Instagram 계정의 ID

### Professional 계정 요구사항
- Instagram 계정이 Professional 계정이어야 함
- Creator 또는 Business 계정 선택
- Facebook Business Manager 연결 필요

## 🔍 문제 해결

### "Invalid OAuth access token" 오류
1. **토큰 형식 확인**: `EAAB...`로 시작하는지 확인
2. **토큰 길이 확인**: 200자 이상인지 확인
3. **권한 확인**: 필요한 권한이 모두 추가되었는지 확인

### Instagram 계정 연결 문제
1. **Professional 계정 확인**
2. **Facebook Business Manager 연결 확인**
3. **권한 승인 확인**

## 📞 지원 리소스

- **Facebook 개발자 문서**: https://developers.facebook.com/docs/
- **Instagram Graph API**: https://developers.facebook.com/docs/instagram-api/
- **Buffer API 문서**: https://buffer.com/developers/api

## 🎯 다음 단계

1. **Facebook Graph API Explorer에서 Instagram 계정 ID 확인**
2. **Buffer Profile ID 확인**
3. **.env 파일 업데이트**
4. **Threads API 테스트 실행** 