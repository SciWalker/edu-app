#!/usr/bin/env python3
"""
Create a Google Classroom assignment or quiz with Gemini‑generated content.

Prerequisites
-------------
pip install google-auth google-api-python-client google-generativeai langgraph pyyaml google-auth-oauthlib

•  Enable the Classroom API and Generative AI API in the same Google Cloud project.
•  Create a service‑account JSON key *with Classroom scopes enabled*:
     https://www.googleapis.com/auth/classroom.coursework.students
•  Either:
      export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
  …or put the file somewhere and reference it below.

Optional:
  export CLASSROOM_TEACHER_EMAIL=teacher@example.com  # for domain‑wide delegation
  export GOOGLE_AI_STUDIO_API_KEY=<your‑Gemini‑key>
"""

import os, json, yaml
from typing import Dict

from google.oauth2 import service_account
from googleapiclient.discovery import build

# Import the gemini handler module
import gemini_handler
# Import the classroom handler module
import classroom_handler

# ─────────────────────────── Configuration ────────────────────────────
SCOPES = ["https://www.googleapis.com/auth/classroom.coursework.students"]

def load_config():
    """
    Load configuration from config.yml.
    """
    try:
        with open("config.yml", "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading config.yml: {e}")
        return None

def create_node(state: gemini_handler.State) -> gemini_handler.State:
    """Create a Google Classroom coursework item using the generated content."""
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

# ────────────────────────────── CLI ───────────────────────────────────
if __name__ == "__main__":
    import argparse, textwrap

    # Load configuration
    config = load_config()
    if config and 'google_classroom_api_key' in config:
        print(f"Google Classroom API key found in config.yml")
    
    # Display courses and count using the classroom_handler
    classroom_handler.display_courses()
    
    parser = argparse.ArgumentParser(
        description="Create Classroom coursework via Gemini + LangGraph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            EXAMPLES
            --------
            # Assignment on quantum tunnelling
            python create_coursework.py --course 123456 --topic "Quantum tunnelling" --type assignment

            # Multiple‑choice quiz on quantum tunnelling
            python create_coursework.py --course 123456 --topic "Quantum tunnelling" --type quiz
        """)
    )
    parser.add_argument("--course", required=True, help="Target Classroom courseId")
    parser.add_argument("--topic",  required=True, help="Short topic description")
    parser.add_argument("--type",   choices=["assignment", "quiz"], default="assignment")
    args = parser.parse_args()

    # Get the compiled graph with our create_node function
    graph = gemini_handler.get_compiled_graph(create_node)
    
    result = graph.invoke({
        "topic": args.topic,
        "work_type": "ASSIGNMENT" if args.type == "assignment" else "MULTIPLE_CHOICE_QUESTION",
        "course_id": args.course,
        "coursework_payload": {},
        "response": {}
    })
    print(json.dumps(result["response"], indent=2))
