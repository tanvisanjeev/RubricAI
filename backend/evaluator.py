import os
import json
import re
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def load_rubric(rubric_path="rubric.txt"):
    if os.path.exists(rubric_path):
        with open(rubric_path, "r") as f:
            return f.read()
    return None

def evaluate_transcript(transcript, student_id, sim, indicator_name="Asks clear, open-ended questions", rubric_text=None):
    if not rubric_text:
        rubric_text = load_rubric()
    if not rubric_text:
        return {"error": "No rubric found. Please provide a rubric.txt file."}

    prompt = f"""You are an expert educational evaluator.

RUBRIC DOCUMENT:
{rubric_text}

INDICATOR TO EVALUATE:
"{indicator_name}"

STUDENT INTERVIEW TRANSCRIPT:
{transcript[:4000]}

Read the rubric, find all relevant student behaviors in the transcript yourself, assign a level 1-4, and return ONLY valid JSON:
{{
  "level": 2,
  "open_ended_count": 3,
  "closed_count": 5,
  "total_questions": 8,
  "open_ended_examples": ["quote 1", "quote 2"],
  "closed_examples": ["quote 1"],
  "strategic_phrasing_count": 0,
  "storytelling_invitations": 0,
  "vague_or_confusing": true,
  "leading_questions": false,
  "multi_topic_questions": false,
  "confidence": 0.85,
  "justification": "...",
  "strengths": "...",
  "improvements": "..."
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    result_text = response.content[0].text
    try:
        result = json.loads(result_text)
    except:
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {"error": "Could not parse response", "raw": result_text}

    result['student_id'] = student_id
    result['simulation'] = sim
    result['indicator'] = indicator_name
    return result

if __name__ == "__main__":
    sample = "[User]: What do you think about the service?\n[Interviewer]: Can you elaborate?\n[User]: Tell me about a time when you struggled."
    print(json.dumps(evaluate_transcript(sample, "TEST", "A"), indent=2))
