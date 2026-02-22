# ⚖️ Discord Judge Bot — 판사봇

> **[한국어](#-한국어) | [English](#-english)**

---

## 🇰🇷 한국어

### 📌 프로젝트 소개

**Discord Judge Bot (판사봇)** 은 온라인 커뮤니티에서 발생하는 **사이버 폭력 문제의 심각성을 알리기 위한 교육 목적 프로젝트**입니다.

오늘날 온라인 공간에서는 욕설, 따돌림, 해킹, 성적 언어, 언어폭력과 같은 행위가 일상적으로 일어나고 있습니다. 이러한 행위들은 단순한 장난이 아니라 **실제 피해자에게 심각한 정신적 상처를 남기는 범죄 행위**입니다.

이 봇은 그 심각성을 직접 체험하게 하고자, 문제 행동을 감지하고 **AI 판사가 실제 대한민국 법률 조항을 적용하여 판결**을 내린 뒤, **Discord 타임아웃(격리) 처벌**을 자동으로 집행합니다.

> **이 프로젝트는 처벌 자체가 목적이 아닙니다.**  
> 온라인에서의 말과 행동이 얼마나 실질적인 결과를 낳을 수 있는지 **직접 경험하게 함으로써 경각심을 심어주는 것**이 목적입니다.

---

### ⚠️ 온라인 폭력의 심각성

| 유형 | 관련 법률 | 최대 처벌 |
|---|---|---|
| 욕설 / 모욕 | 형법 제311조 | 징역 1년 또는 벌금 200만원 |
| 명예훼손 | 정보통신망법 제70조 | 징역 3년 또는 벌금 3,000만원 |
| 협박 | 형법 제283조 | 징역 3년 |
| 해킹 / 개인정보 침해 | 정보통신망법 제49조 | 징역 5년 또는 벌금 5,000만원 |
| 사기 | 형법 제347조 | 징역 10년 |
| 불법 도박 | 국민체육진흥법 위반 | 징역 5년 |

온라인이라는 공간이 익명성을 보장하더라도, **법 앞에서는 동일하게 책임을 집니다.**  
이 봇은 그 사실을 잊지 않도록 하기 위해 만들어졌습니다.

---

### ✨ 주요 기능

- AI가 신고 의도를 자동으로 감지하여 재판을 개시
- 출석 확인 → 증거 제출 → 피고 반론 → AI 판결 순서로 단계적 심리 진행
- 이미지 스크린샷을 증거로 제출 가능
- 판결에 불복 시 서버 멤버 전원이 참여하는 배심원 투표
- 누범자에 대한 가중처벌 (타임아웃 2배 증가)
- 유죄 확정 시 Discord 타임아웃 자동 집행

---

### 📅 프로젝트 정보

- **최초 작성일:** 2026년 02월 22일
- **개발자:** bigad2007
- **유지보수 상태:** ⛔ **이 프로젝트는 현재 완성된 상태로 배포되었으며, 이후 추가 업데이트 및 코드 수정 계획이 없습니다.**

> 버그 수정, 기능 추가, Pull Request 등은 수락되지 않습니다.  
> 코드는 교육 및 참고 목적으로만 자유롭게 활용하실 수 있습니다.

---

### 🚀 설치 및 실행

#### 1. 패키지 설치
```bash
pip install discord.py groq aiohttp
```

#### 2. 설정 입력
`judge_bot.py` 상단의 설정 섹션을 수정합니다.
```python
DISCORD_TOKEN = "여기에_디스코드_봇_토큰_입력"
GROQ_API_KEY  = "여기에_GROQ_API_키_입력"
COURT_CHANNEL_NAME = "재판소"  # 재판 진행 채널 이름
```

#### 3. Discord 봇 토큰 발급
1. [Discord Developer Portal](https://discord.com/developers/applications)에서 애플리케이션 생성
2. **Bot** 탭에서 토큰 복사
3. **Privileged Gateway Intents** → `MESSAGE CONTENT INTENT` 및 `SERVER MEMBERS INTENT` 활성화
4. **OAuth2 > URL Generator**에서 아래 권한으로 초대 링크 생성:
   - `Read Messages / View Channels`
   - `Send Messages`
   - `Manage Messages`
   - `Add Reactions`
   - `Moderate Members` ⚠️ *(타임아웃 집행 필수)*

#### 4. Groq API 키 발급
1. [Groq Console](https://console.groq.com/)에서 회원가입
2. **API Keys** 메뉴에서 키 생성

#### 5. 실행
```bash
python judge_bot.py
```

---

### 📖 사용법

| 행동 | 방법 |
|---|---|
| 신고 시작 | `재판소` 채널에 신고 내용 자유롭게 입력 |
| 피고 지정 | `@유저명` 멘션 |
| 증거 제출 | 이미지 파일 첨부 |
| 증거 제출 완료 | `!판결` 입력 |
| 즉시 판결 요청 | `!최종판결` 입력 |
| 판결 불복 | `!항소` 입력 (판결 후 30초 이내) |
| 재판 강제 종료 *(관리자)* | `!재판취소` 입력 |
| 누범 기록 조회 *(관리자)* | `!누범조회` 입력 |

---

---

## 🇺🇸 English

### 📌 Project Overview

**Discord Judge Bot** is an **educational project designed to raise awareness of the seriousness of cyberbullying and online violence** within online communities.

In today's online spaces, behaviors such as verbal abuse, bullying, hacking, sexual language, and harassment occur on a daily basis. These are not mere jokes — they are **acts that cause real and lasting psychological harm to victims, and in many cases, constitute criminal offenses under the law.**

This bot is designed to make users experience the weight of these actions firsthand: it detects problematic behavior, has an **AI judge apply actual Korean law** to deliver a verdict, and then **automatically enforces a Discord timeout (isolation penalty).**

> **This project is not about punishment for its own sake.**  
> The goal is to **build awareness by letting users directly experience the real consequences** that words and actions online can carry.

---

### ⚠️ The Reality of Online Violence

| Type | Applicable Law | Maximum Penalty |
|---|---|---|
| Verbal abuse / Insult | Criminal Act Article 311 | 1 year imprisonment or ₩2,000,000 fine |
| Defamation | Act on Promotion of IT Network Article 70 | 3 years imprisonment or ₩30,000,000 fine |
| Threats | Criminal Act Article 283 | 3 years imprisonment |
| Hacking / Privacy violation | Act on Promotion of IT Network Article 49 | 5 years imprisonment or ₩50,000,000 fine |
| Fraud | Criminal Act Article 347 | 10 years imprisonment |
| Illegal gambling | National Sports Promotion Act | 5 years imprisonment |

Even if the internet provides anonymity, **you remain equally accountable under the law.**  
This bot exists as a reminder of that fact.

---

### ✨ Key Features

- AI automatically detects reporting intent and opens a trial session
- Step-by-step trial flow: attendance check → evidence submission → defense → AI verdict
- Screenshot images accepted as evidence
- Jury vote system for appeals, open to all server members
- Escalating penalties for repeat offenders (timeout doubles each time)
- Automatic Discord timeout enforcement upon guilty verdict

---

### 📅 Project Information

- **Created:** February 22, 2026
- **Developer:** bigad2007
- **Maintenance Status:** ⛔ **This project has been released in its final state. No further updates, bug fixes, or modifications are planned.**

> Pull requests, feature requests, and issue reports will not be accepted.  
> The code is free to use for educational and reference purposes.

---

### 🚀 Installation & Setup

#### 1. Install packages
```bash
pip install discord.py groq aiohttp
```

#### 2. Configure settings
Edit the configuration section at the top of `judge_bot.py`:
```python
DISCORD_TOKEN = "YOUR_DISCORD_BOT_TOKEN"
GROQ_API_KEY  = "YOUR_GROQ_API_KEY"
COURT_CHANNEL_NAME = "재판소"  # Name of the trial channel
```

#### 3. Get a Discord Bot Token
1. Create an application at [Discord Developer Portal](https://discord.com/developers/applications)
2. Copy your token from the **Bot** tab
3. Enable `MESSAGE CONTENT INTENT` and `SERVER MEMBERS INTENT` under **Privileged Gateway Intents**
4. Generate an invite link via **OAuth2 > URL Generator** with these permissions:
   - `Read Messages / View Channels`
   - `Send Messages`
   - `Manage Messages`
   - `Add Reactions`
   - `Moderate Members` ⚠️ *(Required for timeout enforcement)*

#### 4. Get a Groq API Key
1. Sign up at [Groq Console](https://console.groq.com/)
2. Generate a new key under **API Keys**

#### 5. Run
```bash
python judge_bot.py
```

---

### 📖 Usage

| Action | Command |
|---|---|
| Start a report | Type your complaint freely in the trial channel |
| Designate defendant | Mention with `@username` |
| Submit evidence | Attach image files |
| Finish submitting evidence | Type `!판결` |
| Request immediate verdict | Type `!최종판결` |
| Appeal the verdict | Type `!항소` within 30 seconds |
| Force-cancel trial *(Admin)* | Type `!재판취소` |
| View offense records *(Admin)* | Type `!누범조회` |

---

<div align="center">

**⚖️ 온라인에서의 당신의 말과 행동은 현실에서 책임을 집니다.**  
**⚖️ Your words and actions online carry real-world consequences.**

*Made with the hope that online spaces become safer and more respectful for everyone.*

</div>
