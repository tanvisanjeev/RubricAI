import os
from groq import Groq
from dotenv import load_dotenv
import json
import re

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

RUBRIC_CRITERIA = """
Level 1: 
- Asks 0-1 open-ended questions per 10-minute interview segment
- Questions are vague or confusing (interviewee asks for clarification ≥3 times)
- Questions may be unclear, leading (e.g., "Don't you think that...?"), conflate multiple topics, NOT strategically phrased, do NOT invite storytelling

Level 2:
- Asks 2-3 open-ended questions per 10-minute segment
- Questions sometimes vague or confusing (interviewee asks clarification 2-3 times)
- Phrasings clear, no leading phrases
- Questions sometimes conflate multiple topics, NOT strategically phrased, do NOT invite storytelling

Level 3:
- Asks 4-5 open-ended questions per 10-minute segment (e.g., "Can you tell me about...?", "What was your experience with...?")
- Clearly phrased requiring minimal clarification (1-2 requests per 10 minutes)
- Clear phrasing, no leading language
- Questions focus on one topic at a time
- Questions NOT strategically phrased to elicit rich responses, do NOT invite storytelling

Level 4:
- Asks 6+ open-ended questions per 10-minute segment
- Clearly phrased requiring minimal clarification (<1 request per 10 minutes)
- Clear phrasing, no leading language, focus on one topic
- Demonstrates strategic phrasing 3-5 times using prompts like "Walk me through...", "Help me understand...", "What stood out to you...?"
- Invites storytelling 2-4 times (e.g., "Tell me about a time when..." vs. "What are your thoughts on...?")
"""

def extract_student_questions(transcript):
    """Extract only the student's questions from the transcript"""
    questions = []
    lines = transcript.split('\n')
    
    for line in lines:
        if '[User]:' in line:
            text = line.split('[User]:', 1)[1].strip()
            # Check if it's a question
            if '?' in text or any(text.lower().startswith(q) for q in ['what', 'how', 'why', 'can you', 'tell me', 'could you', 'would you']):
                questions.append(text)
    
    return questions

def evaluate_transcript(transcript, student_id, sim):
    """Evaluate a student's interview performance against the rubric"""
    
    # Extract student's questions
    student_questions = extract_student_questions(transcript)
    
    prompt = f"""You are an expert evaluator of interview skills. Evaluate this student's performance on the rubric criterion: "Asks clear, open-ended questions"

RUBRIC CRITERIA (Levels 1-4):
{RUBRIC_CRITERIA}

STUDENT'S QUESTIONS FROM TRANSCRIPT:
{chr(10).join([f"{i+1}. {q}" for i, q in enumerate(student_questions)])}

FULL TRANSCRIPT CONTEXT:
{transcript[:3000]}

Analyze the student's questioning technique and provide:

1. COUNT: How many open-ended vs closed questions
2. QUALITY ASSESSMENT: Are questions vague? Leading? Multi-topic? Strategic phrasing?
3. LEVEL DETERMINATION: Which level (1-4) does this performance match?
4. EVIDENCE: Specific examples from their questions
5. JUSTIFICATION: Why this level and not higher/lower

Respond in JSON format:
{{
  "level": 2,
  "open_ended_count": 3,
  "closed_count": 5,
  "total_questions": 8,
  "open_ended_examples": ["...", "..."],
  "closed_examples": ["...", "..."],
  "strategic_phrasing_count": 0,
  "storytelling_invitations": 0,
  "vague_or_confusing": true,
  "leading_questions": false,
  "multi_topic_questions": false,
  "justification": "Student asked 3 open-ended questions in approximately X-minute segment...",
  "strengths": "...",
  "improvements": "..."
}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert educational assessment evaluator. Provide detailed, evidence-based rubric evaluations in valid JSON format."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2000
    )
    
    result_text = response.choices[0].message.content
    
    # Extract JSON from response
    try:
        # Try to parse as JSON directly
        result = json.loads(result_text)
    except:
        # Extract JSON from markdown code blocks if present
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', result_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(1))
        else:
            # Fallback
            result = {"error": "Could not parse AI response", "raw": result_text}
    
    result['student_id'] = student_id
    result['simulation'] = sim
    result['indicator'] = "Asks clear, open-ended questions"
    
    return result

if __name__ == "__main__":
    # Test with sample
    sample = "[User]: What do you think about the service?"
    print(evaluate_transcript(sample, "TEST", "A"))
