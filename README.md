# Nestudy   <img width="40" height="40" alt="logo" src="https://github.com/user-attachments/assets/6b99bf7b-6315-4694-9669-bd918f274a7b" />

> 그룹 스터디를 처음부터 끝까지 관리해주는 올인원 웹 서비스

스터디 일정, 공지, 시험, 개인 스케줄까지 한 번에 관리할 수 있는 그룹 스터디 관리 서비스입니다.  
Vue3 + TypeScript + Django + Bootstrap 5 조합으로 만든 풀스택 토이 프로젝트입니다.

- [발표자료 다운로드](https://github.com/Juseong-Yu/SSAFY_GroupStudyPlanner/blob/main/발표.pptx?raw=true)
---

## 👨‍👩‍👧‍👦 Team List

| 유주성 | 신종혁 |
| :---: | :---: |
| Frontend & AI | Backend & Discord Integration |
| <a href="https://github.com/Juseong-Yu"><img src="https://github.com/Juseong-Yu.png" width="150px" /></a> | <a href="https://github.com/Rasit-NP"><img src="https://github.com/Rasit-NP.png" width="150px" /></a> |
| - Vue3 + TS 기반 프론트엔드 개발<br />- AI 문제 생성 기능<br />- UI/UX 설계   | - Django REST API 개발<br />- Discord API 통신<br />- 서버 및 DB 운영 |

---
### 🔀 시스템 아키텍처
<img width="4925" height="2475" alt="그림1" src="https://github.com/user-attachments/assets/2b38b3e2-026f-46f6-a65d-cbd5db3582c6" />


---

## 📌 주요 기능 (Features)

### 1. 스터디 관리
- 스터디 생성 / 가입 / 탈퇴
- **역할(Role) 기반 권한**
  - `leader`, `admin`, `member`
  - 리더 / 관리자만 공지 작성, 일정 생성, 시험 생성 가능
- 스터디 관리 모달에서
  - 스터디 기본 정보 조회
  - 내 역할, 참여 코드, 멤버 리스트 확인

### 2. 스터디 일정 관리
- FullCalendar 기반 스터디 일정 달력
- 일정 목록을 **진행 중 / 다가오는 / 지난 일정**으로 구분
- 일정 상세 모달
  - 일정 제목, 내용, 시간, 장소
  - 스터디 일정 / 개인 일정 타입 배지

### 3. 공지사항(Notice)
- 스터디별 공지 목록 / 상세 조회
- 공지 작성 / 수정 / 삭제
- Markdown 에디터(MdEditor)로 공지 본문 작성
  - 이미지 업로드 지원
  - 라이트 테마, 한국어 UI 설정
- 공지 상세 페이지
  - 작성자 정보, 작성일, 조회수
  - 반응형 포스트 카드 레이아웃

### 4. 시험(Exam) 시스템
- 스터디별 시험 생성 / 응시 / 결과 조회
- **AI 기반 자동 문제 생성**
  - 컨텍스트 텍스트 or 파일 기반 문제 생성
- 수동 문제 생성 모드
- 시험 응시 화면
  - 문제 목록 사이드바
  - 현재 선택한 문제, 답변 완료 표시
  - 남은 시간 배지 표시(타이머 영역 확보 아직 미구현)
- 시험 결과/점수 요약 및 문제별 채점 결과(구현 범위에 맞게 조정)

### 5. 개인 일정 (My Schedule)
- 내 개인 일정 + 스터디 일정을 한 화면에서 통합 조회
- 스터디 페이지 / 메인 페이지와 레이아웃 통일

### 6. 디스코드 연동 
- 스터디 $\leftrightarrow$ 디스코드 채널 연동, 봇 초대
- 디스코드 봇 자동 알림
  - 공지사항/일정 생성 시
  - 일정 알림 시각
---

## 🎬 시연

### 1) 스터디 생성 & 참여
<img src="https://github.com/user-attachments/assets/cdf78d3d-a906-4a12-baa9-99a54cb90ede" width="80%" />

### 2) 시험 생성 & 응시 흐름
<img src="https://github.com/user-attachments/assets/bcbe387e-778a-4aed-8202-b0671a909846" width="80%" />


---

## 🏗 기술 스택 (Tech Stack)

### Frontend
- **Framework**: Vue 3 (Composition API) + TypeScript
- **State Management**: Pinia
- **Router**: Vue Router
- **UI / 스타일**:
  - Bootstrap 5
  - 커스텀 유틸 클래스 
- **HTTP 클라이언트**: Axios  
- **빌드 도구**: Vite

### Backend
- **Framework**: Django 5.2
- **API**: Django REST Framework (DRF)
- **DB**: PostgreSQL
- **Asynchronous Processing**: Celery + Redis(Message Broker)
- **Authentication**: JWT (django-simplejwt), Discord OAuth2

### Discord Bot
- **Framework**: discord.py 2.6.4
- **API**: FastAPI
- **Async Server**: Uvicorn (ASGI)

### Infra / 기타 
- **OS** : Ubuntu 22.04 LTS
- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx
- **WSGI**: Gunicorn
- **Runtime Environment**:
  - **Backend**: Docker Compose (Django, Celery, PostgreSQL, Redis)
  - **Discord Bot**: Python venv (Native Execution)
  - **Frontend**: Node.js / npm (Vite)
---

## ERD
<img src="https://cdn.discordapp.com/attachments/1421025527615197196/1453194724650520737/Nestudy_ERD_3.png?ex=695916cd&is=6957c54d&hm=aae0dc36adf15f72628427db2114c014b1255deb415c726d60805971eeb5d4f1&">

## 🗂 프로젝트 구조 
### Backend
```
Backend/
├── core/
│   ├── __init__.py
│   ├── celery.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── accounts/
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── studies/
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── posts/
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   ├── tasks.py
│   └── views.py
├── schedules/
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   ├── tasks.py
│   └── views.py
├── discord_bot/
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── exams/
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── nginx/
│   └── default.conf
├── manage.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── .dockerignore
└── .gitignore
```
### Bot
```
bot/
├── api.py
├── bot.py
├── config.py
├── main.py
├── utils.py
├── worker.py
├── requirements.txt
└── .gitignore
```

## Frontend 
```
Frontend/
└── Front/
    ├── public/
    │   ├── favicon.ico
    │   └── icons/
    │       ├── web_dark_rd_na@3x.png
    │       ├── web_light_rd_na@3x.png
    │       └── web_neutral_rd_na@3x.png
    ├── src/
    │   ├── api/
    │   │   ├── client.ts
    │   │   └── setupInterceptors.ts
    │   ├── assets/
    │   │   ├── background.png
    │   │   ├── base.css
    │   │   ├── kakao_icon.png
    │   │   ├── login.png
    │   │   ├── logo.png
    │   │   ├── logo.svg
    │   │   ├── main.css
    │   │   ├── oauth.png
    │   │   ├── signup.png
    │   │   └── wait.png
    │   ├── components/
    │   │   ├── __tests__/
    │   │   │   └── HelloWorld.spec.ts
    │   │   ├── icons/
    │   │   │   ├── IconCommunity.vue
    │   │   │   ├── IconDocumentation.vue
    │   │   │   ├── IconEcosystem.vue
    │   │   │   ├── IconSupport.vue
    │   │   │   └── IconTooling.vue
    │   │   ├── layout/
    │   │   │   ├── Navbar.vue
    │   │   │   ├── SettingNavBar.vue
    │   │   │   └── TopNavBar.vue
    │   │   ├── BaseScheduleCalendar.vue
    │   │   └── ScheduleDetailModal.vue
    │   ├── composables/
    │   │   └── useModalAutoClose.ts
    │   ├── layouts/
    │   │   └── AppShell.vue
    │   ├── legal/
    │   │   └── terms_ko.md
    │   ├── router/
    │   │   └── index.ts
    │   ├── stores/
    │   │   ├── authStore.ts
    │   │   ├── counter.ts
    │   │   ├── fetchAllStores.ts
    │   │   ├── resetAllStores.ts
    │   │   ├── studies.ts
    │   │   ├── studyRoleStore.ts
    │   │   ├── ui.ts
    │   │   └── user.ts
    │   ├── utils/
    │   │   └── csrf_cors.ts
    │   ├── views/
    │   │   ├── accounts/
    │   │   │   ├── LoginPage.vue
    │   │   │   ├── LoginPageold.vue
    │   │   │   ├── OauthExtraInfoView.vue
    │   │   │   ├── PasswordCheckPage.vue
    │   │   │   └── SignUpPage.vue
    │   │   ├── auth/
    │   │   │   ├── DiscordCallbackView.vue
    │   │   │   ├── DiscordConnectView.vue
    │   │   │   └── DiscordLoginView.vue
    │   │   ├── settings/
    │   │   │   ├── ConnectPage.vue
    │   │   │   ├── ProfilePage.vue
    │   │   │   └── ProfileUpdatePage.vue
    │   │   ├── studies/
    │   │   │   ├── components/
    │   │   │   │   └── StudyManageModal.vue
    │   │   │   ├── exams/
    │   │   │   │   ├── components/
    │   │   │   │   │   ├── ExamCreateModal.vue
    │   │   │   │   │   ├── ExamResultModal.vue
    │   │   │   │   │   ├── ProblemView.vue
    │   │   │   │   │   └── QuestionList.vue
    │   │   │   │   ├── ExamEditorPage.vue
    │   │   │   │   ├── ExamTakePage.vue
    │   │   │   │   └── StudyExamsPage.vue
    │   │   │   ├── notice/
    │   │   │   │   ├── NoticeCreatePage.vue
    │   │   │   │   ├── NoticeDetailPage.vue
    │   │   │   │   ├── NoticeEditPage.vue
    │   │   │   │   └── StudyNoticePage.vue
    │   │   │   ├── schedule/
    │   │   │   │   └── SchedulePage.vue
    │   │   │   └── StudyPage.vue
    │   │   ├── AboutView.vue
    │   │   ├── LandingPage.vue
    │   │   └── MainPage.vue
    │   ├── App.vue
    │   └── main.ts
    ├── .gitignore
    ├── .prettierrc.json
    ├── env.d.ts
    ├── eslint.config.ts
    ├── index.html
    ├── package-lock.json
    ├── package.json

```
