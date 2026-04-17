# Apex Motors Voice AI Agent — Python Build Plan

**Purpose:** Architecture and implementation plan for rebuilding the Apex Motors voice AI agent as a standalone Python application.
**Target Timeline:** 2-4 weeks, 4 hours/day
**Author:** Yonah
**Note:** See CLAUDE.md for learning approach and collaboration style.

---

## 1. What You're Building

A Python application that answers a real phone number, has a voice conversation with callers to qualify them as sales leads or service customers, answers dealership questions from a knowledge base, handles edge cases, and sends an email summary when the call ends. Same agent as Clerk Chat, but you own every line of code.

---

## 2. Tech Stack

| Component | Tool | Why | Cost |
|-----------|------|-----|------|
| **Language** | Python 3.12+ | Your strongest language, best SDK support | Free |
| **Web framework** | FastAPI | Handles Twilio webhooks, async-native, minimal boilerplate | Free |
| **Phone/voice** | Twilio Voice API | Industry standard, Python SDK, handles SIP/PSTN | ~$1/mo for number + $0.02/min |
| **Speech-to-text** | Deepgram | Faster and cheaper than Twilio STT, real-time WebSocket streaming | Free tier: 45,000 min/year |
| **Text-to-speech** | ElevenLabs | Natural voice quality, "Mark" voice matches your existing agent | Free tier: 10K chars/mo (~10 calls). $5/mo starter for more |
| **LLM (brain)** | OpenAI GPT-4.1-mini | Proven in your Clerk Chat tests, structured output mode | ~$0.01 per call |
| **LLM (voice nodes)** | OpenAI GPT-4.1-mini | Same model, simpler prompts, fast enough for classification | Same |
| **Knowledge base** | ChromaDB (local) | Lightweight vector DB, runs in-process, no server needed | Free |
| **Embeddings** | OpenAI text-embedding-3-small | For KB vector search | ~$0.00 per query |
| **Email** | Resend | Simple API, generous free tier, modern Python SDK | Free: 100 emails/day |
| **Database** | SQLite | Call logs, transcripts, extracted data. Zero setup | Free |
| **Tunneling (dev)** | ngrok | Exposes localhost to Twilio webhooks during development | Free tier |
| **Deployment** | Railway | Git push deploy, free tier, always-on for demo | Free tier or $5/mo |
| **Version control** | Git + GitHub | Portfolio visibility | Free |

**Estimated monthly cost during development:** $2-10 CAD (Twilio number + minutes). Everything else is free tier.

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    INBOUND CALL                      │
│              Twilio → Your Server                    │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│                  CALL HANDLER                         │
│         FastAPI WebSocket endpoint                    │
│                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────────┐   │
│  │ Deepgram │───▶│  State   │───▶│   OpenAI     │   │
│  │   STT    │    │ Machine  │    │  GPT-4.1-mini│   │
│  │(streaming│    │          │    │  (brain +     │   │
│  │  audio)  │    │          │    │   prompts)    │   │
│  └──────────┘    └──────────┘    └──────┬───────┘   │
│                       │                  │           │
│                       │                  ▼           │
│                       │          ┌──────────────┐   │
│                       │          │  ElevenLabs  │   │
│                       │          │     TTS      │   │
│                       │          │  (streaming  │   │
│                       │          │   audio back)│   │
│                       │          └──────────────┘   │
│                       │                              │
│                       ▼                              │
│               ┌──────────────┐                       │
│               │    SQLite    │                       │
│               │  (call log)  │                       │
│               └──────────────┘                       │
└──────────────────────────────────────────────────────┘
                       │
                       │ on call end
                       ▼
┌──────────────────────────────────────────────────────┐
│              POST-CALL PIPELINE                       │
│                                                      │
│  Final extraction (GPT-4.1-mini)                     │
│         → Email generation (GPT-4.1-mini)            │
│              → Resend API                            │
│                  → SQLite log                        │
└──────────────────────────────────────────────────────┘
```

---

## 4. State Machine (Core of the Application)

This replaces Clerk Chat's entire node/edge system. It's a Python class that tracks where the conversation is and what to do next.

```
States:
  GREETING          → speak greeting, wait for reply
  ROUTING           → brain analyzes first reply, picks path
  ASK_STOCK         → ask or skip-self
  ASK_BUDGET        → ask or skip-self
  ASK_TRADE_IN      → ask or skip-self
  ASK_TIMELINE      → ask or skip-self
  ASK_JOB_TYPE      → ask or skip-self
  ASK_LOGISTICS     → ask or skip-self
  ASK_LOANER        → ask or skip-self (+ wait detection)
  ASK_INTENT        → ask sales or service
  FAQ               → search KB, deliver answer, return to previous state
  NUDGE             → handle escalation/emergency/off-topic
  EXTRACTING        → final brain call to structure all data
  WRAP_UP           → deliver closing, hang up
  ENDED             → post-call: extract, email, log
```

Transitions are hardcoded in Python — no LLM decides routing mid-flow (except the initial brain call and escalation detection). This is the key architectural improvement over Clerk Chat: routing is deterministic code, not an LLM output parsed by edge filters.

---

## 5. Key Improvement Over Clerk Chat

**Real-time streaming.** Clerk Chat processes in steps: caller finishes speaking → STT → LLM → TTS → play audio. Each step waits for the previous one to complete. You can do better:

- **Deepgram streams STT** — you get partial transcripts as the caller speaks
- **OpenAI streams completions** — you get tokens as they generate
- **ElevenLabs streams TTS** — you can start playing audio before the full response is generated

This means the caller hears the first words of the response while the LLM is still generating the rest. The perceived latency drops dramatically — from "silence then full sentence" to "brief pause then words start flowing."

This is the single biggest UX improvement and it's architecturally impossible on Clerk Chat.

---

## 6. Project Structure

```
apex-motors-voice-agent/
├── CLAUDE.md                 # Claude Code instructions
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── docs/
│   ├── MASTER_REFERENCE.md   # Full spec from Clerk Chat version
│   ├── BUILD_PLAN.md         # This file
│   └── reference/
│       ├── apex-v1.JSON      # Clerk Chat V2.1 pipeline
│       ├── apex-v2.JSON      # Clerk Chat V2.2 pipeline
│       └── apex-v3.JSON      # Clerk Chat V2.3 pipeline
│
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, Twilio webhook endpoints
│   ├── config.py             # Environment variables, API keys
│   │
│   ├── call/
│   │   ├── __init__.py
│   │   ├── handler.py        # WebSocket call handler (audio streaming)
│   │   ├── state_machine.py  # Conversation state machine
│   │   └── session.py        # Per-call session (transcript, state, data)
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── brain.py          # Qualification brain (routing + extraction)
│   │   ├── prompts.py        # All prompt templates
│   │   └── voice.py          # Voice node logic (question + skip-self)
│   │
│   ├── speech/
│   │   ├── __init__.py
│   │   ├── stt.py            # Deepgram STT integration
│   │   └── tts.py            # ElevenLabs TTS integration
│   │
│   ├── knowledge/
│   │   ├── __init__.py
│   │   ├── kb.py             # ChromaDB vector search
│   │   └── load_kb.py        # Script to load CSV into ChromaDB
│   │
│   ├── email/
│   │   ├── __init__.py
│   │   └── dispatch.py       # Email generation + Resend API
│   │
│   └── db/
│       ├── __init__.py
│       └── logger.py         # SQLite call logging
│
├── data/
│   ├── knowledge_base.csv    # 130 Q&A rows
│   └── chroma/               # ChromaDB persistent storage
│
├── scripts/
│   ├── setup_twilio.py       # Helper to configure Twilio number
│   └── test_call.py          # CLI tool to test without calling
│
└── tests/
    ├── test_state_machine.py
    ├── test_brain.py
    └── test_prompts.py
```

---

## 7. Build Plan — Week by Week

### Week 1: Foundation (Voice Pipeline Working)

**Day 1-2: Setup and Hello World**
- Create GitHub repo, virtual environment, project structure
- Sign up: OpenAI API, Twilio, Deepgram, ElevenLabs
- Install ngrok, configure tunnel
- Build FastAPI app with single endpoint
- Twilio answers a call → plays hardcoded "Hello" via TTS → hangs up
- **Milestone: Phone rings, you hear a voice, call ends**

**Day 3-4: STT + LLM Integration**
- Connect Deepgram WebSocket for real-time STT
- Caller speaks → you see transcript in terminal
- Connect OpenAI API — send transcript, get response
- Hardcode the greeting prompt — Sam speaks, caller replies, LLM responds
- **Milestone: Two-way voice conversation (unstructured)**

**Day 5-6: State Machine + Linear Chain**
- Implement state_machine.py with all states
- Implement brain.py — initial routing call (same prompt as Clerk Chat brain)
- Wire up: greeting → brain → first question → next question → ... → wrap_up → hangup
- Skip-self logic in each question state
- **Milestone: Full SALES qualification flow works over the phone**

**Day 7: SERVICE Path + Logging**
- Add SERVICE states (job_type, logistics, loaner)
- Loaner skip-self for "wait" callers
- SQLite logging — save every call transcript and extracted data
- **Milestone: Both paths work, calls are logged**

### Week 2: Features and Polish

**Day 8-9: Knowledge Base**
- Load CSV into ChromaDB
- Implement KB search function
- Brain detects FAQ on first message → search → deliver answer → resume
- **Milestone: "What are your hours?" gets a correct KB answer**

**Day 10-11: Escalation + Email**
- Nudge state — brain detects anger/emergency/off-topic
- Emergency → deliver phone number → end call
- Soft escalation → acknowledge → return to flow
- Post-call email generation (same prompt as Clerk Chat email_copy)
- Resend API integration
- **Milestone: Escalation handled, emails sent on every completed call**

**Day 12-13: Testing + Edge Cases**
- Run through full test checklist (16 scenarios from master doc)
- Fix whatever breaks
- Handle double-speak (caller says two messages quickly)
- Handle silence (caller doesn't respond)
- **Milestone: All core test scenarios pass**

**Day 14: Deployment + Documentation**
- Deploy to Railway
- Configure Twilio to point at Railway URL
- Update README with setup instructions, architecture diagram, example transcript
- Record a demo call
- **Milestone: Anyone can call the number and talk to Sam**

### Week 3 (if needed): Improvements

- Streaming TTS (start playing before full response generates)
- Mid-flow FAQ (KB search in question states, not just initial brain)
- Mid-flow escalation detection
- Better silence handling
- Call recording (Twilio feature)
- Load testing (2 concurrent calls)

---

## 8. Account Setup Checklist

### OpenAI
- [ ] Create account at platform.openai.com
- [ ] Add payment method ($5 minimum)
- [ ] Generate API key
- [ ] Note: GPT-4.1-mini costs ~$0.40/M input tokens, $1.60/M output tokens

### Twilio
- [ ] Create account at twilio.com
- [ ] Get free trial ($15 credit)
- [ ] Buy a phone number ($1.15/month)
- [ ] Note: Voice costs $0.0085/min inbound + $0.014/min outbound

### Deepgram
- [ ] Create account at deepgram.com
- [ ] Free tier: $200 credit (plenty for development)
- [ ] Generate API key
- [ ] Use Nova-3 model for best accuracy

### ElevenLabs
- [ ] Create account at elevenlabs.io
- [ ] Free tier: 10,000 characters/month
- [ ] Find or clone a voice similar to "Mark" (professional male)
- [ ] Generate API key
- [ ] Note: Starter plan ($5/mo) gives 30,000 chars if free tier runs out

### Resend
- [ ] Create account at resend.com
- [ ] Free tier: 100 emails/day, 3,000/month
- [ ] Verify a sending domain or use onboarding@resend.dev for testing
- [ ] Generate API key

### ngrok
- [ ] Create account at ngrok.com
- [ ] Install: `brew install ngrok`
- [ ] Authenticate: `ngrok config add-authtoken YOUR_TOKEN`
- [ ] Free tier is sufficient for development

### Railway (deployment)
- [ ] Create account at railway.app
- [ ] Connect GitHub repo
- [ ] Free tier: 500 hours/month, $5/month after
- [ ] Deploy happens automatically on git push

---

## 9. Dependencies (requirements.txt)

```
fastapi>=0.104.0
uvicorn>=0.24.0
websockets>=12.0
python-dotenv>=1.0.0
openai>=1.50.0
twilio>=9.0.0
deepgram-sdk>=3.4.0
elevenlabs>=1.0.0
resend>=2.0.0
chromadb>=0.5.0
pydantic>=2.0.0
httpx>=0.27.0
```

---

## 10. Environment Variables (.env.example)

```
# OpenAI
OPENAI_API_KEY=sk-...

# Twilio
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...

# Deepgram
DEEPGRAM_API_KEY=...

# ElevenLabs
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=...

# Resend
RESEND_API_KEY=re_...
EMAIL_RECIPIENT=hello@yonal.io
EMAIL_FROM=sam@yourdomain.com

# App
APP_URL=https://your-ngrok-url.ngrok.io  # or Railway URL
```

---

## 11. Prompts Strategy

All prompts from the Clerk Chat agent transfer directly. The master reference document contains every prompt verbatim. Key adaptations for the Python version:

- **Remove Clerk Chat-specific syntax:** `{{{5.variable}}}` and `{{{30.variable}}}` become Python variables passed into prompt templates (f-strings or `.format()`)
- **Remove response function instructions:** No more "call submit_stock" or "execute the submit_budget function" — the state machine handles transitions. The LLM just returns the extracted answer.
- **Remove shouldLoop/waitForSpeech references:** Your code controls retry and silence behavior
- **Remove Clerk Chat node config references:** `responseToolName`, `responseToolDescription`, `allowInterruptions` are platform-specific and have no equivalent — your code handles these behaviors directly
- **Keep all SKIP CHECK logic** — still needed for the same reasons (linear chain, question nodes fire in sequence)
- **CRITICAL OVERRIDE is unnecessary** — each call gets a fresh session object in Python with its own transcript. No transcript accumulation across calls. Remove CRITICAL OVERRIDE blocks from all prompts.

---

## 12. What's Different From Clerk Chat

| Aspect | Clerk Chat | Python Version |
|--------|-----------|----------------|
| Routing | LLM output → edge filters | Python state machine (deterministic) |
| Latency | 6-10s brain calls between questions | ~0s (no brain between questions) |
| Voice streaming | Batch (full STT → full LLM → full TTS) | Streaming (partial → partial → partial) |
| Session isolation | Prompt-level CRITICAL OVERRIDE | Code-level: each call gets fresh session object |
| Transcript accumulation | Platform accumulates all calls per contact | Each call has its own transcript in memory |
| FAQ mid-flow | Lost in V3 linear chain | Can be added at code level (check if response is a question) |
| Escalation mid-flow | Lost in V3 linear chain | Can be added at code level (check for anger keywords) |
| Debugging | Pipeline execution logs in UI | Terminal output + SQLite logs |
| Deployment | Clerk Chat hosted | Railway (your infrastructure) |

---

## 13. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Twilio WebSocket audio format issues | High | Blocks all progress | Follow Twilio Media Streams docs exactly. Test with simple echo first |
| FastAPI async complexity | Medium | Slows development | Start synchronous, add async only where needed |
| ElevenLabs free tier runs out | Medium | Can't test voice | Switch to Twilio's built-in TTS (lower quality but free) |
| Deepgram latency spikes | Low | Caller hears delay | Deepgram is generally fast. Nova-3 model recommended |
| OpenAI API rate limits | Low | Calls fail | GPT-4.1-mini has generous limits. Not an issue at portfolio scale |
| Railway deployment issues | Low | Demo not accessible | Railway is straightforward for Python/FastAPI. Good docs |

---

## 14. Definition of Done

The project is complete when:
- [ ] Someone can call the Twilio number and have a full SALES qualification conversation
- [ ] Someone can call and have a full SERVICE qualification conversation
- [ ] FAQ question on first message gets a correct KB answer
- [ ] Emergency caller gets the emergency line number and call ends
- [ ] Email is sent after every completed call with correct data
- [ ] All calls are logged in SQLite with transcript and extracted fields
- [ ] Deployed on Railway with a live phone number
- [ ] GitHub repo has README with architecture diagram, setup instructions, and example transcript
- [ ] Can demonstrate to a hiring manager in under 3 minutes
