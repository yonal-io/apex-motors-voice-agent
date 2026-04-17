# Apex Motors Voice AI Agent — Python Build

## About this project
Rebuilding a real-time voice AI agent in Python from scratch. Previously built on the Clerk Chat no-code platform across 3 major architecture versions. The agent answers phone calls as "Sam" from Apex Motors (a fictional luxury auto dealership in LA), qualifies callers as sales leads or service customers through natural conversation, answers FAQ from a knowledge base, handles escalation/emergency scenarios, and sends a structured lead email when the call ends.

## About me
- Python: intermediate (scripts, CLI apps, school projects). Never built a backend or API.
- Never used FastAPI, Twilio, Deepgram, ElevenLabs, WebSockets, or ChromaDB before.
- Mac M3 Pro, macOS Tahoe, zsh, Ghostty terminal.
- I learn by building. Explain concepts when they're relevant, not as lectures.

## Tech stack (locked in — do not suggest alternatives)
- Python 3.12+, FastAPI, uvicorn
- Twilio Voice (Media Streams WebSocket)
- Deepgram Nova-3 (real-time STT via WebSocket)
- ElevenLabs (TTS)
- OpenAI GPT-4.1-mini (brain + extraction + email generation)
- OpenAI text-embedding-3-small (KB embeddings)
- ChromaDB (local vector KB search)
- Resend (email dispatch)
- SQLite (call logging)
- ngrok (dev tunneling)
- Railway (deployment)

## Key reference files
- docs/MASTER_REFERENCE.md — every prompt, schema, edge map, model selection rationale, test results, and bug history from the Clerk Chat version. This is the spec.
- docs/BUILD_PLAN.md — tech stack, project structure, week-by-week build plan, account setup checklist, and definition of done.
- docs/reference/ — original Clerk Chat pipeline JSONs (V1, V2, V3) for architectural reference.
- data/knowledge_base.csv — 130-row FAQ knowledge base (Question, Answer columns).

## Architecture summary
- State machine with deterministic routing (no LLM decides mid-flow transitions)
- Brain fires twice: once after greeting (intent detection + routing to first question), once at end (full data extraction for email)
- SALES linear chain: stock → budget → trade_in → timeline → extraction → wrap_up
- SERVICE linear chain: job_type → logistics → loaner → extraction → wrap_up
- Each question node has skip-self logic: checks transcript, skips if already answered
- FAQ handled by brain on first message only (routes to KB search + answer)
- Escalation detected by brain on first message (routes to nudge handler)
- Post-call: extraction brain → email generation → Resend API → SQLite log

## How to help me
- For core logic (state machine, brain integration, audio streaming): explain what needs to happen and why, let me write the first attempt, then review and fix. I want to understand the code, not just run it.
- For boilerplate (config files, API client setup, dependency wiring): write it directly — no learning value in me guessing Twilio's SDK syntax.
- When I hit an error, I'll paste the full traceback — ask for it before guessing.
- Test each piece before moving to the next.
- Flag when I'm about to make an architectural mistake.
- Keep explanations short unless I ask for detail.
- Reference the MASTER_REFERENCE.md for prompts, schemas, and field values instead of recreating them from memory.


## Build order (follow this sequence)
1. Project setup, accounts, virtual env, dependencies
2. FastAPI + Twilio webhook — phone rings, plays hardcoded greeting
3. Deepgram WebSocket STT — caller speaks, transcript appears in terminal
4. ElevenLabs TTS — agent speaks with natural voice
5. Two-way voice conversation (greeting + one LLM response)
6. State machine + brain routing (full SALES flow)
7. SERVICE flow + loaner skip-self
8. SQLite call logging
9. ChromaDB knowledge base + FAQ on first message
10. Nudge/escalation handling
11. Post-call email (extraction brain → email generation → Resend)
12. Testing all 16 scenarios from test checklist
13. Railway deployment
14. README + GitHub polish