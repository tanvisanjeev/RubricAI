from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from evaluator import evaluate_transcript
from pdf_exporter import generate_pdf
import csv
import io
import json
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="RubricAI API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

@app.get("/")
def root():
    return {"message": "RubricAI API", "version": "1.0", "status": "operational"}

@app.get("/api/health")
def health():
    return {"status": "healthy", "ai_engine": "Anthropic API", "indicators_active": 1, "indicators_total": 34}


@app.post("/api/evaluate")
async def evaluate_csv(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        text = contents.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)

        if not rows:
            return {"status": "error", "message": "CSV file is empty."}

        required = {"Student", "Sim A Script", "Sim B Script"}
        if not required.issubset(set(rows[0].keys())):
            return {"status": "error", "message": f"Missing columns. Required: {required}"}

        students = []
        for row in rows:
            sid = str(row.get("Student", "Unknown")).strip()
            sim_a = row.get("Sim A Script", "").strip()
            sim_b = row.get("Sim B Script", "").strip()

            results = []
            levels = []

            if sim_a:
                r = evaluate_transcript(sim_a, sid, "A")
                results.append(r)
                levels.append(r["level"])

            if sim_b:
                r = evaluate_transcript(sim_b, sid, "B")
                results.append(r)
                levels.append(r["level"])

            avg = round(sum(levels) / len(levels), 1) if levels else None
            scores = {
                "overall": avg,
                "domains": {
                    "Communication": {
                        "score": avg,
                        "clusters": {"Interview Communication": avg}
                    },
                    "Critical Thinking": {"score": None, "clusters": {}},
                    "Professional Agency": {"score": None, "clusters": {}}
                }
            }

            students.append({
                "student_id": sid,
                "results": results,
                "scores": scores
            })

        return {"status": "success", "students": students, "total": len(students)}

    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/chat")
async def chat(data: dict):
    """AI Assistant endpoint — proxies chat to Anthropic API"""
    try:
        system_prompt = data.get("system", "You are a helpful AI assistant for RubricAI.")
        messages = data.get("messages", [])

        if not messages:
            return {"status": "error", "message": "No messages provided."}

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1000,
            system=system_prompt,
            messages=messages
        )

        reply = response.content[0].text
        return {"status": "success", "reply": reply}

    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/export/pdf")
async def export_pdf(data: dict):
    try:
        students = data.get("students", [])
        pdf_bytes = generate_pdf(students)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=rubricai_report.pdf"}
        )
    except Exception as e:
        return {"status": "error", "message": str(e)}
