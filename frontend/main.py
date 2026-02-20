from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from evaluator import evaluate_transcript
from database import get_db, Student, Evaluation
from datetime import datetime
import csv
import io

app = FastAPI(title="RubricAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "RubricAI API"}

@app.post("/api/evaluate")
async def evaluate_csv(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        text = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(text))
        
        results = []
        db = get_db()
        
        for row in csv_reader:
            student_id = str(row.get('Student', '')).strip()
            
            if not student_id:
                continue
            
            student = db.query(Student).filter_by(id=student_id).first()
            if not student:
                student = Student(id=student_id, name=f"Student {student_id}")
                db.add(student)
            
            if row.get('Sim A Script'):
                result_a = evaluate_transcript(row['Sim A Script'], student_id, 'A')
                results.append(result_a)
                
                eval_a = Evaluation(
                    student_id=student_id,
                    interview_number=1,
                    simulation='A',
                    indicator_id=1,
                    indicator_name="Asks clear, open-ended questions",
                    level=result_a.get('level'),
                    confidence=result_a.get('confidence', 0.9),
                    evidence=result_a.get('evidence', {}),
                    justification=result_a.get('justification'),
                    strengths=result_a.get('strengths'),
                    improvements=result_a.get('improvements')
                )
                db.add(eval_a)
            
            if row.get('Sim B Script'):
                result_b = evaluate_transcript(row['Sim B Script'], student_id, 'B')
                results.append(result_b)
                
                eval_b = Evaluation(
                    student_id=student_id,
                    interview_number=2,
                    simulation='B',
                    indicator_id=1,
                    indicator_name="Asks clear, open-ended questions",
                    level=result_b.get('level'),
                    confidence=result_b.get('confidence', 0.9),
                    evidence=result_b.get('evidence', {}),
                    justification=result_b.get('justification'),
                    strengths=result_b.get('strengths'),
                    improvements=result_b.get('improvements')
                )
                db.add(eval_b)
            
            all_evals = db.query(Evaluation).filter_by(student_id=student_id).all()
            if all_evals:
                levels = [e.level for e in all_evals]
                student.overall_avg = sum(levels) / len(levels)
                student.communication_avg = student.overall_avg
                student.interviews_completed = len(all_evals)
                student.status = "Complete"
                student.needs_review = any(e.confidence < 0.85 for e in all_evals)
                student.last_evaluated = datetime.utcnow()
        
        db.commit()
        db.close()
        
        return {
            "status": "success",
            "total_evaluations": len(results),
            "students_processed": len(set(r.get('student_id') for r in results)),
            "results": results
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/students")
async def get_students():
    db = get_db()
    students = db.query(Student).all()
    result = [{
        "id": s.id,
        "name": s.name,
        "cohort": s.cohort,
        "interviews_completed": s.interviews_completed,
        "overall_avg": s.overall_avg,
        "communication_avg": s.communication_avg,
        "status": s.status,
        "needs_review": s.needs_review
    } for s in students]
    db.close()
    return {"students": result}

@app.get("/api/students/{student_id}")
async def get_student(student_id: str):
    db = get_db()
    student = db.query(Student).filter_by(id=student_id).first()
    if not student:
        db.close()
        return {"error": "Student not found"}
    
    evaluations = db.query(Evaluation).filter_by(student_id=student_id).all()
    result = {
        "id": student.id,
        "name": student.name,
        "cohort": student.cohort,
        "interviews_completed": student.interviews_completed,
        "overall_avg": student.overall_avg,
        "communication_avg": student.communication_avg,
        "status": student.status,
        "needs_review": student.needs_review,
        "evaluations": [{
            "id": e.id,
            "interview_number": e.interview_number,
            "simulation": e.simulation,
            "indicator_name": e.indicator_name,
            "level": e.level,
            "confidence": e.confidence,
            "evidence": e.evidence,
            "justification": e.justification,
            "strengths": e.strengths,
            "improvements": e.improvements,
            "instructor_override": e.instructor_override,
            "instructor_notes": e.instructor_notes
        } for e in evaluations]
    }
    db.close()
    return result

@app.post("/api/students/{student_id}/override")
async def override_evaluation(student_id: str, data: dict):
    db = get_db()
    evaluation = db.query(Evaluation).filter_by(id=data.get('evaluation_id')).first()
    if evaluation:
        evaluation.instructor_override = data.get('new_level')
        evaluation.instructor_notes = data.get('notes', '')
        db.commit()
    db.close()
    return {"status": "success"}

@app.get("/api/health")
def health():
    return {"status": "healthy"}
