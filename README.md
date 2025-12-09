# Nestudy   <img width="40" height="40" alt="logo" src="https://github.com/user-attachments/assets/6b99bf7b-6315-4694-9669-bd918f274a7b" />

> 그룹 스터디를 처음부터 끝까지 관리해주는 올인원 웹 서비스

스터디 일정, 공지, 시험, 개인 스케줄까지 한 번에 관리할 수 있는 그룹 스터디 관리 서비스입니다.  
Vue3 + TypeScript + Django + Bootstrap 5 조합으로 만든 풀스택 토이 프로젝트입니다.

---

## 👨‍👩‍👧‍👦 Team List

| 유주성 | 신종혁 |
| :---: | :---: |
| Frontend & AI | Backend & Discord Integration |
| <img src="https://avatars.githubusercontent.com/u/114473861?v=4" width="150px" /> | <img src="https://avatars.githubusercontent.com/u/깃허브ID?v=4" width="150px" /> |
| - Vue3 + TS 기반 프론트엔드 개발<br />- 스터디/공지/일정/시험 UI 개발<br />- AI 문제 생성 기능 구현<br />- 전체 UX/UI 설계 및 컴포넌트 구조 설계 | - Django REST API 개발<br />- 스터디/공지/일정/시험 백엔드 로직 구현<br />- Discord Webhook 연동<br />- DB 모델 설계 및 서버 운영 |



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
- ??
- ??
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
- **Framework**: Django
- **API**: Django REST Framework (DRF)
- **Auth**: Django 기본 인증 + 커스텀 User (예정/진행 상황에 맞게 수정)
- **DB**: SQLite (개발용, 운영 시 교체 가능)
- **기타**
  - Discord Webhook 연동 (`DiscordStudyMapping` 모델)

### Infra / 기타 
- Python venv
- 배포: ??

---

## 🗂 프로젝트 구조 

