# Seafood AI Ops Demo

A demo-focused FastAPI app for an AI operations layer for seafood distributors.

## What this demo shows

- Messy seafood business emails become structured operational data
- The app keeps QuickBooks/Gmail as existing systems
- The app creates a reviewable action queue
- The technical API proof remains available at `/docs`

## Run

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/
```

API proof:

```text
http://127.0.0.1:8000/docs
```

## Demo Flow

1. Click a scenario card
2. Analyze the email
3. Review the business interpretation
4. See the suggested action
5. View the action queue and parsed history
6. Show raw JSON as technical proof

## AI Modes

Free local mode:

```env
AI_PROVIDER="mock"
```

Hybrid mode:

```env
AI_PROVIDER="hybrid"
AI_ESCALATION_THRESHOLD=0.85
GEMINI_API_KEY="your_key_here"
```
