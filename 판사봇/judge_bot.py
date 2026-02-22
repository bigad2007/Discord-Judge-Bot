import discord
from discord.ext import commands
import groq
import base64
import json
import datetime
import asyncio
from pathlib import Path


DISCORD_TOKEN = "여기에_디스코드_봇_토큰_입력"
GROQ_API_KEY  = "여기에_GROQ_API_키_입력"

COURT_CHANNEL_NAME   = "재판소"
BASE_TIMEOUT_MINUTES = 30
OFFENDER_DATA_FILE   = "offenders.json"

ATTENDANCE_SECONDS = 30
EVIDENCE_SECONDS   = 120
DEFENSE_SECONDS    = 60
JURY_SECONDS       = 60   # 배심원 투표 시간
APPEAL_WINDOW      = 30   # 항소 가능 시간 (판결 후 30초)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
groq_client = groq.Groq(api_key=GROQ_API_KEY)

# =============================================
#  📁  누범 기록
# =============================================
def load_offenders():
    path = Path(OFFENDER_DATA_FILE)
    if path.exists():
        try:
            content = path.read_text(encoding="utf-8").strip()
            if content:
                return json.loads(content)
        except (json.JSONDecodeError, ValueError):
            pass
    return {}

def save_offenders(data):
    with open(OFFENDER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_timeout_minutes(user_id: str) -> int:
    offenders = load_offenders()
    count = offenders.get(user_id, {}).get("count", 0)
    return BASE_TIMEOUT_MINUTES * (2 ** count)

def record_offense(user_id: str, username: str):
    offenders = load_offenders()
    if user_id not in offenders:
        offenders[user_id] = {"username": username, "count": 0}
    offenders[user_id]["count"] += 1
    offenders[user_id]["last_offense"] = datetime.datetime.now().isoformat()
    save_offenders(offenders)
    return offenders[user_id]["count"]

def _get_case_number():
    data = load_offenders()
    total = sum(v.get("count", 0) for v in data.values())
    return f"{datetime.datetime.now().year}-형{total+1:04d}"

active_trials = {}

# =============================================
#  🤖  Groq AI
# =============================================
async def judge_with_groq(prompt: str, images: list = None) -> str:
    system_prompt = """당신은 대한민국 디스코드 서버의 공식 판사 '홍판사'입니다.

[판사 페르소나]
- 냉철하고 위엄 있으며, 절대 감정적이지 않습니다.
- 반말이나 친근한 표현 없이 오직 공식적이고 무거운 어투만 사용합니다.
- 판결문은 실제 대한민국 법원 판결문 형식을 따릅니다.

[판결 원칙]
- 원고의 증거(이미지)와 피고의 반론(텍스트/이미지)을 모두 종합하여 판단합니다.
- 피고가 유발·지시에 의한 것임을 주장하면 정상참작합니다.
- 맥락상 상대방이 먼저 유발하거나 동의한 상황이라면 무죄 또는 감경 선고할 수 있습니다.
- 명백한 증거가 있을 때만 유죄. 억울한 처벌은 절대 없습니다.
- 욕설·비속어·혐오표현·인신공격, 해킹, 불법사이트, 사기, 협박 등도 판단합니다.
- 유죄 시 반드시 대한민국 실제 법률 조항과 처벌 수위를 명시합니다.
- 원고 또는 피고가 불출석한 경우 그 사실도 판결문에 반영합니다.

[실제 법률 참고]
- 욕설/명예훼손: 정보통신망법 제70조 - 최대 징역 3년 또는 벌금 3000만원
- 욕설/모욕죄: 형법 제311조 - 최대 징역 1년 또는 벌금 200만원
- 협박: 형법 제283조 - 최대 징역 3년
- 해킹/개인정보침해: 정보통신망법 제49조 - 최대 징역 5년 또는 벌금 5000만원
- 불법 도박 사이트: 국민체육진흥법 위반 - 최대 징역 5년
- 사기: 형법 제347조 - 최대 징역 10년

[판결문 형식]
**주문:** 유죄 / 무죄

**사실관계:**
(증거와 반론에서 확인된 사실 2~3문장)

**판단:**
(법적 판단 근거, 정상참작 여부, 불출석 여부 포함 2~3문장)

**적용 법조:**
(해당 법률 조항과 실제 처벌 수위. 무죄 시 "해당 없음")

**선고:**
(최종 선고 내용을 엄숙하게 1~2문장으로)"""

    if images:
        content = [{"type": "text", "text": prompt}]
        for img_b64 in images:
            content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}})
        messages = [{"role": "user", "content": content}]
    else:
        messages = [{"role": "user", "content": prompt}]

    response = groq_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "system", "content": system_prompt}] + messages,
        max_tokens=900,
        temperature=0.2
    )
    return response.choices[0].message.content

# =============================================
#  🔍  신고 의도 감지 (AI)
# =============================================
async def detect_report(text: str) -> bool:
    """유저 메시지가 신고 의도인지 AI로 판단"""
    try:
        response = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": (
                    "당신은 디스코드 메시지를 분석하는 도우미입니다. "
                    "아래 메시지가 누군가를 신고하려는 의도인지 판단하세요. "
                    "욕설, 인종차별, 혐오발언, 협박, 사기, 해킹, 성희롱, 괴롭힘 등 "
                    "다양한 신고 유형을 모두 포함합니다. "
                    "신고 의도가 있으면 YES, 없으면 NO 만 답하세요."
                )},
                {"role": "user", "content": text}
            ],
            max_tokens=5,
            temperature=0.0
        )
        result = response.choices[0].message.content.strip().upper()
        return "YES" in result
    except Exception:
        return False


# =============================================
#  ⚖️  판결 실행 (타이머·명령어 공통)
# =============================================
async def do_final_verdict(channel, channel_id):
    trial = active_trials.get(channel_id)
    if not trial:
        return

    plaintiff          = trial["plaintiff"]
    defendant          = trial["defendant"]
    evidence_images    = trial["evidence_images"]
    defense_images     = trial["defense_images"]
    defense_text       = trial["defense_text"]
    plaintiff_attended = trial.get("plaintiff_attended", False)
    defendant_attended = trial.get("defendant_attended", False)

    await channel.send("```\n[ 최 종 심 리 중 ]\n원고 증거 및 피고 반론을 종합 검토하고 있습니다...\n```")

    offenders     = load_offenders()
    offense_count = offenders.get(str(defendant.id), {}).get("count", 0) if defendant else 0
    timeout_min   = get_timeout_minutes(str(defendant.id)) if defendant else 0
    all_images    = evidence_images + defense_images
    defense_summary = "\n".join(defense_text) if defense_text else "없음"

    prompt = (
        f"[사건 개요]\n"
        f"원고: {plaintiff.display_name} ({'출석' if plaintiff_attended else '불출석'})\n"
        f"피고: {defendant.display_name if defendant else '미지정'} ({'출석' if defendant_attended else '불출석'})\n"
        f"피고의 누범 횟수: {offense_count}회\n\n"
        f"[원고 제출 증거 이미지]: {len(evidence_images)}장\n"
        f"[피고 반론 진술]: {defense_summary}\n"
        f"[피고 반증 이미지]: {len(defense_images)}장\n\n"
        f"원고와 피고의 출석 여부, 제출된 증거, 반론을 모두 종합하여 판단하십시오.\n"
        f"피고가 상대방의 유발·지시에 의해 행동했다는 주장이 있으면 정상참작하십시오.\n"
        f"유죄 시 대한민국 실제 법률 조항과 처벌 수위를 반드시 명시하십시오."
    )

    ai_response = await judge_with_groq(prompt, all_images if all_images else None)
    is_guilty   = "유죄" in ai_response and "무죄" not in ai_response.split("유죄")[0]
    case_no     = _get_case_number()

    await channel.send(
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚖️　**최 종 판 결 문**　⚖️\n"
        f"**사건번호 제 {case_no}호**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{ai_response}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    # 항소 안내 (판결 당사자만)
    trial["last_verdict_guilty"] = is_guilty
    trial["last_verdict_text"]   = ai_response
    trial["last_case_no"]        = case_no
    trial["defendant_id"]        = str(defendant.id) if defendant else None
    trial["timeout_min"]         = timeout_min
    trial["state"]               = "appeal_window"

    appellant = defendant if is_guilty else plaintiff
    await channel.send(
        f"📢 **판결에 불복하는 경우 `!항소` 를 입력하십시오.**\n"
        f"{appellant.mention if appellant else ''} — {APPEAL_WINDOW}초 내에 항소하지 않으면 판결이 확정됩니다."
    )
    asyncio.create_task(appeal_window_timer(channel, channel_id, is_guilty, defendant, timeout_min))

# =============================================
#  ⏱️  항소 대기 타이머
# =============================================
async def appeal_window_timer(channel, channel_id, is_guilty, defendant, timeout_min):
    await asyncio.sleep(APPEAL_WINDOW)
    trial = active_trials.get(channel_id)
    if not trial or trial["state"] != "appeal_window":
        return
    # 항소 없으면 판결 확정 → 형 집행
    await channel.send("⏰ 항소 기간이 종료되었습니다. **판결이 확정됩니다.**")
    await execute_sentence(channel, channel_id, is_guilty, defendant, timeout_min)

async def execute_sentence(channel, channel_id, is_guilty, defendant, timeout_min):
    trial = active_trials.get(channel_id)
    if not trial:
        return

    if is_guilty and defendant:
        offense_times = record_offense(str(defendant.id), defendant.display_name)
        try:
            await defendant.timeout(datetime.timedelta(minutes=timeout_min), reason=f"판사봇 판결: 위반 {offense_times}회")
            await channel.send(
                f"🔨 **[ 형 집 행 ]**\n\n"
                f"{defendant.mention} 피고인에 대하여\n"
                f"**서버 내 {timeout_min}분 격리(타임아웃)** 를 즉시 집행합니다.\n"
                f"> 누범 횟수: **{offense_times}회** | 재범 시 2배 가중\n\n"
                f"본 법정은 이상으로 폐정합니다.\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
        except discord.Forbidden:
            await channel.send("⚠️ 봇에게 `Moderate Members` 권한이 없어 집행이 불가합니다.")
    else:
        mention = defendant.mention if defendant else "피고"
        await channel.send(
            f"✅ **[ 무 죄 확 정 ]**\n\n"
            f"{mention} 피고인은 **무죄**가 확정되었습니다.\n"
            f"본 법정은 억울한 처벌을 허용하지 않습니다.\n"
            f"본 법정은 이상으로 폐정합니다.\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )

    active_trials.pop(channel_id, None)

# =============================================
#  🗳️  배심원 투표 진행
# =============================================
async def run_jury(channel, channel_id):
    trial = active_trials.get(channel_id)
    if not trial:
        return

    plaintiff = trial["plaintiff"]
    defendant = trial["defendant"]
    case_no   = trial.get("last_case_no", "???")

    # 투표 메시지 생성
    vote_msg = await channel.send(
        f"@everyone\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎭 **[ 배 심 원 투 표 ]**\n"
        f"**사건번호 제 {case_no}호 항소심**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"원고: **{plaintiff.display_name}** vs 피고: **{defendant.display_name if defendant else '?'}**\n\n"
        f"서버 멤버 여러분께서 배심원으로서 의견을 표결하여 주십시오.\n"
        f"⚖️ = 유죄　　✅ = 무죄\n\n"
        f"⏰ **{JURY_SECONDS}초** 후 투표가 종료되고 과반수로 결정됩니다.\n"
        f"*(원고·피고는 투표할 수 없습니다)*"
    )
    await vote_msg.add_reaction("⚖️")
    await vote_msg.add_reaction("✅")

    trial["jury_msg_id"] = vote_msg.id
    trial["state"] = "jury"

    await asyncio.sleep(JURY_SECONDS)

    # 투표 결과 집계
    trial = active_trials.get(channel_id)
    if not trial or trial["state"] != "jury":
        return

    try:
        vote_msg = await channel.fetch_message(vote_msg.id)
    except Exception:
        return

    guilty_votes   = 0
    innocent_votes = 0
    exclude_ids    = {plaintiff.id, bot.user.id}
    if defendant:
        exclude_ids.add(defendant.id)

    for reaction in vote_msg.reactions:
        users = [u async for u in reaction.users()]
        valid = [u for u in users if u.id not in exclude_ids and not u.bot]
        if str(reaction.emoji) == "⚖️":
            guilty_votes = len(valid)
        elif str(reaction.emoji) == "✅":
            innocent_votes = len(valid)

    total = guilty_votes + innocent_votes
    is_guilty = guilty_votes > innocent_votes

    result_text = "**유죄**" if is_guilty else "**무죄**"
    await channel.send(
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎭 **[ 배 심 원 평 결 결 과 ]**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"총 투표: {total}표\n"
        f"⚖️ 유죄: {guilty_votes}표　　✅ 무죄: {innocent_votes}표\n\n"
        f"배심원단의 평결: {result_text}\n\n"
        f"본 법정은 배심원단의 평결을 수용하여 최종 판결을 확정합니다.\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    timeout_min = trial.get("timeout_min", BASE_TIMEOUT_MINUTES)
    await execute_sentence(channel, channel_id, is_guilty, defendant, timeout_min)

# =============================================
#  ⏱️  타이머들
# =============================================
async def run_evidence_timer(channel, channel_id):
    await asyncio.sleep(EVIDENCE_SECONDS)
    trial = active_trials.get(channel_id)
    if trial and trial["state"] == "waiting_for_evidence":
        trial["state"] = "defense_time"
        defendant = trial["defendant"]
        await channel.send(
            f"⏰ **[증거 제출 시간 종료]**\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚖️ **[ 피 고 반 론 시 간 — {DEFENSE_SECONDS}초 ]**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"**【피고】** {defendant.mention if defendant else '불출석'}\n"
            f"억울한 사정이 있다면 지금 반론을 진술하십시오.\n"
            f"> 예시: *\"상대방이 먼저 욕해보라고 시켜서 한 것입니다.\"*\n\n"
            f"`!최종판결` 입력 또는 {DEFENSE_SECONDS}초 후 자동 선고됩니다.\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        asyncio.create_task(run_defense_timer(channel, channel_id))

async def run_defense_timer(channel, channel_id):
    await asyncio.sleep(DEFENSE_SECONDS)
    trial = active_trials.get(channel_id)
    if trial and trial["state"] == "defense_time":
        await channel.send("⏰ **[반론 시간 종료]** 선고를 진행합니다.")
        await do_final_verdict(channel, channel_id)

async def attendance_timer(channel, channel_id):
    await asyncio.sleep(ATTENDANCE_SECONDS)
    trial = active_trials.get(channel_id)
    if not trial or trial["state"] != "attendance":
        return

    p_att = trial["plaintiff_attended"]
    d_att = trial["defendant_attended"]
    plaintiff = trial["plaintiff"]
    defendant = trial["defendant"]

    trial["state"] = "waiting_for_evidence"

    lines = ["⏰ **[출석 확인 종료]**\n"]
    lines.append(f"원고 {plaintiff.display_name}: {'✅ 출석' if p_att else '❌ 불출석'}")
    lines.append(f"피고 {defendant.display_name}: {'✅ 출석' if d_att else '❌ 불출석'}\n")
    lines.append(f"**【원고】** {plaintiff.mention if p_att else plaintiff.display_name + ' (불출석)'}")
    lines.append(f"증거 이미지를 제출하십시오. `!판결` 입력 또는 **{EVIDENCE_SECONDS}초** 후 자동 진행됩니다.")

    await channel.send("\n".join(lines))
    asyncio.create_task(run_evidence_timer(channel, channel_id))

# =============================================
#  🔔  이벤트
# =============================================
@bot.event
async def on_ready():
    print(f"⚖️  판사봇 '{bot.user}' 개정 준비 완료!")
    print(f"📢  재판 채널: #{COURT_CHANNEL_NAME}")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    await bot.process_commands(message)

    if message.channel.name != COURT_CHANNEL_NAME:
        return
    if message.content.startswith("!"):
        return

    channel_id = message.channel.id
    trial = active_trials.get(channel_id)

    if trial is None:
        # AI로 신고 의도 감지 (말투 상관없이 자동 인식)
        if len(message.content) >= 5:
            is_report = await detect_report(message.content)
            if is_report:
                active_trials[channel_id] = {
                    "state": "waiting_for_defendant",
                    "plaintiff": message.author,
                    "defendant": None,
                    "evidence_images": [],
                    "defense_text": [],
                    "defense_images": [],
                    "plaintiff_attended": False,
                    "defendant_attended": False,
                }
                await message.channel.send(
                    f"⚖️ **[신고 접수]**\n\n"
                    f"{message.author.mention}, 신고가 접수되었습니다.\n"
                    f"피고인을 **@멘션**으로 지정하여 주십시오."
                )
        return

    state = trial["state"]

    # 재판 중 타인 발언 차단
    if state in ("waiting_for_evidence", "defense_time", "attendance"):
        if message.author != trial["plaintiff"] and message.author != trial.get("defendant"):
            try:
                await message.delete()
                await message.channel.send(
                    f"⚠️ {message.author.mention} 재판 진행 중에는 원고·피고만 발언할 수 있습니다.",
                    delete_after=5
                )
            except discord.Forbidden:
                pass
            return

    if state == "waiting_for_defendant":
        if message.author != trial["plaintiff"]:
            return
        if not message.mentions:
            await message.channel.send("⚠️ 피고인을 @멘션으로 지정해 주십시오.")
            return
        defendant = message.mentions[0]
        if defendant == message.author:
            await message.channel.send("⚠️ 본인을 피고인으로 지정할 수 없습니다.")
            return
        if defendant.bot:
            await message.channel.send("⚠️ 봇을 피고인으로 지정할 수 없습니다.")
            return

        trial["defendant"] = defendant
        trial["state"] = "attendance"
        case_no = _get_case_number()

        await message.channel.send(
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔔🔔🔔　**재 판 을 시 작 하 겠 습 니 다**　🔔🔔🔔\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"**사건번호　제 {case_no}호**\n"
            f"```\n원  고 : {trial['plaintiff'].display_name}\n피  고 : {defendant.display_name}\n담당판사 : 홍판사\n```\n"
            f"📋 **[ 출 석 확 인 — {ATTENDANCE_SECONDS}초 ]**\n\n"
            f"{trial['plaintiff'].mention} **(원고)** — \"출석합니다\" 를 입력하십시오.\n"
            f"{defendant.mention} **(피고)** — \"출석합니다\" 를 입력하십시오.\n\n"
            f"⏰ {ATTENDANCE_SECONDS}초 내 미응답 시 불출석 처리 후 재판을 진행합니다.\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        asyncio.create_task(attendance_timer(message.channel, channel_id))
        return

    if state == "attendance":
        if "출석" in message.content:
            if message.author == trial["plaintiff"] and not trial["plaintiff_attended"]:
                trial["plaintiff_attended"] = True
                await message.channel.send(f"✅ 원고 **{message.author.display_name}** 출석 확인.", delete_after=8)
            elif message.author == trial.get("defendant") and not trial["defendant_attended"]:
                trial["defendant_attended"] = True
                await message.channel.send(f"✅ 피고 **{message.author.display_name}** 출석 확인.", delete_after=8)

            if trial["plaintiff_attended"] and trial["defendant_attended"]:
                trial["state"] = "waiting_for_evidence"
                await message.channel.send(
                    f"✅ **원고·피고 모두 출석 확인.**\n\n"
                    f"**【원고】** {trial['plaintiff'].mention}\n"
                    f"증거 이미지를 제출하십시오. `!판결` 입력 또는 **{EVIDENCE_SECONDS}초** 후 자동 진행됩니다.\n"
                    f"재판 중에는 원고·피고 외 발언이 금지됩니다."
                )
                asyncio.create_task(run_evidence_timer(message.channel, channel_id))
        return

    if state == "waiting_for_evidence":
        if message.author == trial["plaintiff"] and message.attachments:
            import aiohttp
            for att in message.attachments:
                if any(att.filename.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp", ".gif"]):
                    async with aiohttp.ClientSession() as session:
                        async with session.get(att.url) as resp:
                            img_bytes = await resp.read()
                            trial["evidence_images"].append(base64.b64encode(img_bytes).decode("utf-8"))
            await message.channel.send(
                f"📁 **증거 {len(trial['evidence_images'])}건 접수.** `!판결` 을 입력하거나 추가 첨부하십시오."
            )
        return

    if state == "defense_time":
        if message.author == trial.get("defendant"):
            if message.content:
                trial["defense_text"].append(message.content)
                await message.channel.send("📝 **피고 반론 접수.** `!최종판결` 로 선고를 요청할 수 있습니다.", delete_after=8)
            if message.attachments:
                import aiohttp
                for att in message.attachments:
                    if any(att.filename.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp", ".gif"]):
                        async with aiohttp.ClientSession() as session:
                            async with session.get(att.url) as resp:
                                img_bytes = await resp.read()
                                trial["defense_images"].append(base64.b64encode(img_bytes).decode("utf-8"))
                await message.channel.send(f"📁 **피고 반증 {len(trial['defense_images'])}건 접수.**", delete_after=8)
        return

# =============================================
#  명령어
# =============================================
@bot.command(name="판결")
async def request_verdict(ctx: commands.Context):
    if ctx.channel.name != COURT_CHANNEL_NAME:
        return
    channel_id = ctx.channel.id
    trial = active_trials.get(channel_id)
    if not trial or trial["state"] != "waiting_for_evidence":
        await ctx.send("⚠️ 현재 증거 제출 단계가 아닙니다.")
        return
    if ctx.author != trial["plaintiff"]:
        await ctx.send("⚠️ 원고만 이 명령어를 사용할 수 있습니다.")
        return
    trial["state"] = "defense_time"
    defendant = trial["defendant"]
    await ctx.send(
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚖️ **[ 피 고 반 론 시 간 — {DEFENSE_SECONDS}초 ]**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"**【피고】** {defendant.mention if defendant else '불출석'}\n"
        f"억울한 사정이 있다면 지금 반론을 진술하십시오.\n"
        f"> 예시: *\"상대방이 먼저 욕해보라고 시켜서 한 것입니다.\"*\n\n"
        f"`!최종판결` 입력 또는 {DEFENSE_SECONDS}초 후 자동 선고됩니다.\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    asyncio.create_task(run_defense_timer(ctx.channel, channel_id))

@bot.command(name="최종판결")
async def final_verdict_cmd(ctx: commands.Context):
    if ctx.channel.name != COURT_CHANNEL_NAME:
        return
    channel_id = ctx.channel.id
    trial = active_trials.get(channel_id)
    if not trial or trial["state"] != "defense_time":
        await ctx.send("⚠️ 현재 최종판결 단계가 아닙니다.")
        return
    if ctx.author != trial["plaintiff"] and ctx.author != trial.get("defendant"):
        await ctx.send("⚠️ 원고 또는 피고만 최종판결을 요청할 수 있습니다.")
        return
    await do_final_verdict(ctx.channel, channel_id)

@bot.command(name="항소")
async def appeal(ctx: commands.Context):
    if ctx.channel.name != COURT_CHANNEL_NAME:
        return
    channel_id = ctx.channel.id
    trial = active_trials.get(channel_id)
    if not trial or trial["state"] != "appeal_window":
        await ctx.send("⚠️ 현재 항소 가능한 판결이 없습니다.")
        return

    plaintiff = trial["plaintiff"]
    defendant = trial.get("defendant")

    # 원고 또는 피고만 항소 가능
    if ctx.author != plaintiff and ctx.author != defendant:
        await ctx.send("⚠️ 원고 또는 피고만 항소할 수 있습니다.")
        return

    trial["state"] = "jury_waiting"
    await ctx.send(
        f"⚖️ **[항소 접수]**\n\n"
        f"{ctx.author.mention} 이(가) 판결에 불복하여 항소를 제기하였습니다.\n\n"
        f"**배심원 재판으로 넘어갑니다.**\n"
        f"잠시 후 서버 멤버 전원이 배심원으로서 투표에 참여할 수 있습니다.\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    await asyncio.sleep(3)
    asyncio.create_task(run_jury(ctx.channel, channel_id))

@bot.command(name="재판취소")
@commands.has_permissions(administrator=True)
async def cancel_trial(ctx: commands.Context):
    if ctx.channel.name != COURT_CHANNEL_NAME:
        return
    channel_id = ctx.channel.id
    if channel_id in active_trials:
        del active_trials[channel_id]
        await ctx.send("⚖️ 관리자 권한으로 재판을 강제 종료하였습니다.")
    else:
        await ctx.send("⚠️ 진행 중인 재판이 없습니다.")

@bot.command(name="누범조회")
@commands.has_permissions(administrator=True)
async def check_offenders(ctx: commands.Context):
    data = load_offenders()
    if not data:
        await ctx.send("📋 현재 누범 기록이 없습니다.")
        return
    msg = "📋 **누범 기록**\n━━━━━━━━━━━━━━━\n"
    for uid, info in data.items():
        msg += f"• {info['username']} — {info['count']}회 처벌\n"
    await ctx.send(msg)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)