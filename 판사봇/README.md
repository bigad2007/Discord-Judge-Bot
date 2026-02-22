# ⚖️ Judge Bot (판사봇)

> **[한국어](#한국어) | [English](#english)**

---

## 한국어

### 소개

Discord 서버에서 유저 간 분쟁을 AI가 자동으로 심리하고 판결을 내려주는 봇입니다.  
Groq AI(LLaMA 4)를 기반으로 한 **홍판사**가 증거와 반론을 검토하여 실제 대한민국 법률을 적용한 판결문을 생성하고, 유죄 시 Discord 타임아웃을 자동 집행합니다.

### 주요 기능

- **자동 신고 감지** — 지정 채널에서 신고 의도의 메시지를 AI가 자동으로 인식하여 재판을 개시합니다.
- **단계별 재판 진행** — 출석 확인 → 증거 제출 → 피고 반론 → AI 판결 순서로 진행됩니다.
- **이미지 증거 지원** — 원고와 피고 모두 스크린샷 등 이미지를 증거로 제출할 수 있습니다.
- **배심원 항소 제도** — 판결에 불복 시 `!항소` 명령어로 서버 멤버 전원이 참여하는 배심원 투표로 넘어갑니다.
- **누범 기록 및 가중처벌** — 재범자는 타임아웃 시간이 2배씩 증가합니다.
- **자동 타임아웃 집행** — 유죄 판결 확정 시 피고인에게 Discord 타임아웃을 즉시 적용합니다.

### 설치 방법

#### 1. 필수 패키지 설치

```bash
pip install discord.py groq aiohttp
```

#### 2. 설정값 입력

`judge_bot.py` 상단의 설정 섹션을 수정합니다.

```python
DISCORD_TOKEN = "여기에_디스코드_봇_토큰_입력"
GROQ_API_KEY  = "여기에_GROQ_API_키_입력"

COURT_CHANNEL_NAME   = "재판소"   # 재판이 진행될 채널 이름
BASE_TIMEOUT_MINUTES = 30         # 기본 타임아웃 시간 (분)
```

#### 3. 봇 토큰 발급

1. [Discord Developer Portal](https://discord.com/developers/applications)에서 애플리케이션을 생성합니다.
2. **Bot** 탭에서 토큰을 복사합니다.
3. **Privileged Gateway Intents**에서 `MESSAGE CONTENT INTENT`와 `SERVER MEMBERS INTENT`를 활성화합니다.
4. **OAuth2 > URL Generator**에서 `bot` 스코프와 다음 권한을 선택하여 초대 링크를 생성합니다.
   - `Read Messages / View Channels`
   - `Send Messages`
   - `Manage Messages` (재판 중 타인 메시지 삭제용)
   - `Add Reactions`
   - `Moderate Members` ⚠️ **타임아웃 집행에 필수**

#### 4. Groq API 키 발급

1. [Groq Console](https://console.groq.com/)에 가입합니다.
2. **API Keys** 메뉴에서 새 키를 생성하여 복사합니다.

#### 5. 채널 생성

Discord 서버에 `COURT_CHANNEL_NAME`에 설정한 이름과 동일한 채널을 생성합니다. (기본값: `재판소`)

#### 6. 봇 실행

```bash
python judge_bot.py
```

### 사용 방법

| 상황 | 방법 |
|---|---|
| 신고 시작 | `재판소` 채널에서 신고 내용을 자유롭게 입력 (AI가 자동 인식) |
| 피고 지정 | `@유저명` 멘션 |
| 증거 제출 | 이미지 파일 첨부 |
| 증거 제출 완료 | `!판결` 입력 |
| 반론 후 즉시 판결 요청 | `!최종판결` 입력 |
| 판결에 불복 | `!항소` 입력 (판결 후 30초 이내) |

### 관리자 명령어

| 명령어 | 설명 |
|---|---|
| `!재판취소` | 진행 중인 재판을 강제 종료 |
| `!누범조회` | 모든 누범 기록 확인 |

### 타임 설정

```python
ATTENDANCE_SECONDS = 30   # 출석 확인 시간
EVIDENCE_SECONDS   = 120  # 증거 제출 시간
DEFENSE_SECONDS    = 60   # 피고 반론 시간
JURY_SECONDS       = 60   # 배심원 투표 시간
APPEAL_WINDOW      = 30   # 항소 가능 시간 (판결 후)
```

---

## English

### Overview

A Discord bot that automatically conducts hearings and delivers AI-powered verdicts for disputes between server members.  
**Judge Hong**, powered by Groq AI (LLaMA 4), reviews evidence and counterarguments and issues verdicts based on actual Korean law. Guilty verdicts result in automatic Discord timeouts.

### Features

- **Automatic report detection** — AI automatically detects reporting intent from messages in the designated channel and opens a trial.
- **Step-by-step trial flow** — Attendance check → Evidence submission → Defense → AI verdict.
- **Image evidence support** — Both plaintiff and defendant can submit screenshots and images as evidence.
- **Jury appeal system** — If a verdict is disputed, `!항소` (appeal) triggers a server-wide jury vote.
- **Repeat offense tracking** — Timeout duration doubles for each repeat offense.
- **Automatic timeout enforcement** — Guilty verdicts result in an immediate Discord timeout for the defendant.

### Installation

#### 1. Install required packages

```bash
pip install discord.py groq aiohttp
```

#### 2. Configure settings

Edit the configuration section at the top of `judge_bot.py`:

```python
DISCORD_TOKEN = "YOUR_DISCORD_BOT_TOKEN"
GROQ_API_KEY  = "YOUR_GROQ_API_KEY"

COURT_CHANNEL_NAME   = "재판소"  # Channel name where trials take place
BASE_TIMEOUT_MINUTES = 30        # Base timeout duration in minutes
```

#### 3. Get a Discord Bot Token

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and create an application.
2. Navigate to the **Bot** tab and copy your token.
3. Under **Privileged Gateway Intents**, enable `MESSAGE CONTENT INTENT` and `SERVER MEMBERS INTENT`.
4. Under **OAuth2 > URL Generator**, select the `bot` scope with the following permissions and use the generated link to invite the bot:
   - `Read Messages / View Channels`
   - `Send Messages`
   - `Manage Messages` (to delete messages from non-participants during trial)
   - `Add Reactions`
   - `Moderate Members` ⚠️ **Required for timeout enforcement**

#### 4. Get a Groq API Key

1. Sign up at [Groq Console](https://console.groq.com/).
2. Go to **API Keys** and generate a new key.

#### 5. Create the trial channel

Create a channel in your Discord server with the same name as `COURT_CHANNEL_NAME` (default: `재판소`).

#### 6. Run the bot

```bash
python judge_bot.py
```

### How to Use

| Situation | Action |
|---|---|
| Start a report | Type your complaint freely in the `재판소` channel (AI auto-detects) |
| Designate defendant | Mention the user with `@username` |
| Submit evidence | Attach image files |
| Finish submitting evidence | Type `!판결` |
| Request immediate verdict after defense | Type `!최종판결` |
| Appeal the verdict | Type `!항소` within 30 seconds of the verdict |

### Admin Commands

| Command | Description |
|---|---|
| `!재판취소` | Force-cancel an ongoing trial |
| `!누범조회` | View all repeat offense records |

### Timer Configuration

```python
ATTENDANCE_SECONDS = 30   # Time allowed for attendance check
EVIDENCE_SECONDS   = 120  # Time allowed for evidence submission
DEFENSE_SECONDS    = 60   # Time allowed for defense
JURY_SECONDS       = 60   # Duration of jury vote
APPEAL_WINDOW      = 30   # Time window to file an appeal after verdict
```

### Notes

- The bot only operates in the channel specified by `COURT_CHANNEL_NAME`.
- During an active trial, only the plaintiff and defendant can send messages in the channel.
- Offense records are saved locally in `offenders.json`.
- The bot must have a higher role than users it intends to timeout.
