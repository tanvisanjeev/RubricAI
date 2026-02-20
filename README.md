# RubricAI
### AI-Powered Interview Skills Assessment Platform

**Built by Tanvi Kadam**

RubricAI is an AI-powered platform that evaluates student interview transcripts against research-backed behavioral rubrics. It provides consistent, evidence-based scoring across communication domains — replacing manual, subjective review with intelligent, scalable assessment.

---

## What It Does

RubricAI reads student interview transcripts and evaluates them against a structured rubric with 34 behavioral indicators across three domains. For each indicator, the AI identifies relevant behaviors, extracts evidence from the transcript, and assigns a score from Level 1 to Level 4 — with full justification.

---

## Evaluation Domains

| Domain | Indicators |
|--------|-----------|
| Communication | 10 |
| Critical Thinking | 12 |
| Professional Agency | 12 |
| **Total** | **34** |

---

## Scoring System

Scores are calculated at four levels of granularity:

```
Individual Indicator (Level 1–4)
           ↓
     Cluster Score (avg of related indicators)
           ↓
     Domain Score (avg of clusters)
           ↓
     Overall Student Score
```

This gives evaluators both a high-level snapshot and granular insight into specific skill areas.

---

## Key Features

- **AI-Driven Evaluation** — Claude AI reads the rubric document directly and evaluates transcripts without hardcoded prompts
- **Evidence-Based Scoring** — Every score includes actual quotes from the transcript as supporting evidence
- **Confidence Scores** — Low-confidence evaluations are automatically flagged for instructor review
- **Instructor Override** — Educators can review, validate, and override any AI score
- **Student Dashboard** — Visual profile showing scores across all indicators and domains
- **Export Reports** — Export individual or batch student reports as PDF or CSV
- **Uploadable Rubric** — Works with any rubric document — not hardcoded to a specific framework
- **Scalable** — Designed to process large volumes of transcripts consistently

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI |
| AI Engine | Claude AI (Anthropic) |
| Frontend | HTML, CSS, JavaScript |
| Database | SQLite / PostgreSQL |
| Deployment | Vercel |

---

## Project Structure

```
rubricai/
├── backend/
│   ├── evaluator.py        # Core AI evaluation engine
│   ├── main.py             # FastAPI server & API routes
│   ├── database.py         # Database models & queries
│   ├── requirements.txt    # Python dependencies
│   └── rubric.txt          # Rubric document (add your own)
├── frontend/
│   ├── demo.html           # Demo dashboard
│   └── index.html          # Main interface
├── LICENSE
└── README.md
```

---

## Getting Started

### Prerequisites
- Python 3.9+
- Anthropic API key

### Installation

```bash
# Clone the repository
git clone https://github.com/tanvisanjeev/RubricAI.git
cd RubricAI/backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "ANTHROPIC_API_KEY=your_key_here" >> .env

# Add your rubric document
cp your_rubric.txt backend/rubric.txt
```

### Running the App

```bash
# Terminal 1 — Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
python3 -m http.server 8080
```

Open `http://localhost:8080/demo.html` in your browser.

---

## How the AI Evaluation Works

1. **Rubric is loaded** from `rubric.txt` — no hardcoded criteria
2. **Transcript is passed** to Claude AI along with the rubric and indicator name
3. **AI identifies** relevant student behaviors directly from the transcript
4. **AI scores** against the rubric levels using its own interpretation
5. **Evidence is extracted** — actual quotes from the transcript support the score
6. **Confidence score** is generated — low scores are flagged for human review
7. **Results are stored** and displayed on the student dashboard

---

## Development Roadmap

| Phase | Timeline | Scope | Status |
|-------|----------|-------|--------|
| Phase 1 | Complete | Core architecture + Indicator 1 validated | ✅ Done |
| Phase 2 | March | Communication domain — 10 indicators | 🔄 In Progress |
| Phase 3 | April | Critical Thinking — 12 indicators | 📅 Planned |
| Phase 4 | May | Professional Agency + full export + deployment | 📅 Planned |

---

## Evaluation Approach

### Easy Indicators (Quantifiable)
Counted behaviors — e.g., number of open-ended questions, transitions, paraphrases — matched against rubric thresholds.

### Hard Indicators (Qualitative)
Observable behaviors defined per level — e.g., emotional acknowledgment, referencing prior statements, topic continuity. AI detects and counts these behaviors, with low-confidence scores flagged for instructor review.

---

## License

MIT License © 2025 Tanvi Kadam
