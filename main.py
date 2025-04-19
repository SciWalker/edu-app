#!/usr/bin/env python3
"""
Create a Google Classroom assignment or quiz with Gemini‑generated content.

Prerequisites
-------------
pip install google-auth google-api-python-client google-generativeai langgraph pyyaml

•  Enable the Classroom API and Generative AI API in the same Google Cloud project.
•  Create a service‑account JSON key *with Classroom scopes enabled*:
     https://www.googleapis.com/auth/classroom.coursework.students
•  Either:
      export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
  …or put the file somewhere and reference it below.

Optional:
  export CLASSROOM_TEACHER_EMAIL=teacher@example.com  # for domain‑wide delegation
  export GOOGLE_AI_STUDIO_API_KEY=<your‑Gemini‑key>
"""

import os, json, time
from typing import TypedDict, Literal, Dict

from langgraph.graph import StateGraph, END
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ─────────────────────────── Configuration ────────────────────────────
SCOPES = ["https://www.googleapis.com/auth/classroom.coursework.students"]
MODEL_NAME = "gemini-1.5-pro"          # or 1.5‑flash etc.

# ─────────────────────────── Graph state type ─────────────────────────
class State(TypedDict):
    topic: str
    work_type: Literal["ASSIGNMENT", "MULTIPLE_CHOICE_QUESTION"]
    course_id: str
    coursework_payload: Dict          # gets filled by Gemini
    response: Dict                    # API response goes here

# ─────────────────────── Gemini prompt builders ───────────────────────
def _prompt(topic: str, work_type: str) -> str:
    if work_type == "ASSIGNMENT":
        return f"""
Return ONLY valid JSON for a Google Classroom assignment.
Keys (exactly):
  "title"         : str
  "description"   : str
  "maxPoints"     : int
  "dueDate"       : {{ "year": int, "month": int, "day": int }}
  "workType"      : "ASSIGNMENT"
  "state"         : "PUBLISHED"

Generate an assignment about: "{topic}".
"""
    return f"""
Return ONLY valid JSON for a Google Classroom multiple‑choice quiz.
Keys (exactly):
  "title"                  : str
  "description"            : str
  "multipleChoiceQuestion" : {{ "choices": [str, str, str] }}
  "maxPoints"              : int
  "workType"               : "MULTIPLE_CHOICE_QUESTION"
  "state"                  : "PUBLISHED"

Generate a quiz about: "{topic}".
"""

# ────────────────────────── LangGraph nodes ───────────────────────────
def generate_node(state: State) -> State:
    genai.configure(api_key=os.environ["GOOGLE_AI_STUDIO_API_KEY"])
    prompt = _prompt(state["topic"], state["work_type"])
    model  = genai.GenerativeModel(MODEL_NAME)
    time.sleep(1)  # mild rate‑limit buffer
    resp = model.generate_content(prompt)
    state["coursework_payload"] = json.loads(resp.text)
    return state

def create_node(state: State) -> State:
    creds = service_account.Credentials.from_service_account_file(
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"], scopes=SCOPES
    )
    subj = os.getenv("CLASSROOM_TEACHER_EMAIL")
    if subj:
        creds = creds.with_subject(subj)

    service = build("classroom", "v1", credentials=creds)
    cw = (
        service.courses()
        .courseWork()
        .create(courseId=state["course_id"], body=state["coursework_payload"])
        .execute()
    )
    state["response"] = cw
    return state

# ───────────────────────── Build the graph ────────────────────────────
def build_graph():
    g = StateGraph(State)
    g.add_node("generate", generate_node)
    g.add_node("create",   create_node)
    g.add_edge("generate", "create")
    g.add_edge("create",   END)
    g.set_entry_point("generate")
    return g.compile()

# ────────────────────────────── CLI ───────────────────────────────────
if __name__ == "__main__":
    import argparse, textwrap
    parser = argparse.ArgumentParser(
        description="Create Classroom coursework via Gemini + LangGraph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            EXAMPLES
            --------
            # Assignment on natural selection
            python create_coursework.py --course 123456 --topic "Natural selection" --type assignment

            # Multiple‑choice quiz on cell organelles
            python create_coursework.py --course 123456 --topic "Cell organelles" --type quiz
        """)
    )
    parser.add_argument("--course", required=True, help="Target Classroom courseId")
    parser.add_argument("--topic",  required=True, help="Short topic description")
    parser.add_argument("--type",   choices=["assignment", "quiz"], default="assignment")
    args = parser.parse_args()

    graph = build_graph()
    result = graph.invoke({
        "topic": args.topic,
        "work_type": "ASSIGNMENT" if args.type == "assignment" else "MULTIPLE_CHOICE_QUESTION",
        "course_id": args.course,
        "coursework_payload": {},
        "response": {}
    })
    print(json.dumps(result["response"], indent=2))
