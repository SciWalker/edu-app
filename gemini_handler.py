#!/usr/bin/env python3
"""
Gemini LLM handler for generating Google Classroom content.
This module handles all interactions with the Gemini API for the edu-app.
"""

import os
import json
import time
import yaml
from typing import TypedDict, Literal, Dict

import google.generativeai as genai
from langgraph.graph import StateGraph, END

# ─────────────────────────── Configuration ────────────────────────────
MODEL_NAME = "gemini-2.5-pro-exp-03-25"  # or 1.5‑flash etc.

# ─────────────────────────── Graph state type ─────────────────────────
class State(TypedDict):
    topic: str
    work_type: Literal["ASSIGNMENT", "MULTIPLE_CHOICE_QUESTION"]
    course_id: str
    coursework_payload: Dict  # gets filled by Gemini
    response: Dict  # API response goes here

# ─────────────────────── Gemini prompt builders ───────────────────────
def _prompt(topic: str, work_type: str) -> str:
    """Build a prompt for Gemini based on the work type."""
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
    """Generate content using Gemini API based on the topic and work type."""
    with open("config.yml", "r") as file:
        config = yaml.safe_load(file)
    
    genai.configure(api_key=config["google_ai_studio_api_key"])
    prompt = _prompt(state["topic"], state["work_type"])
    model = genai.GenerativeModel(MODEL_NAME)
    time.sleep(1)  # mild rate‑limit buffer
    resp = model.generate_content(prompt)
    state["coursework_payload"] = json.loads(resp.text)
    return state

# ───────────────────────── Build the graph ────────────────────────────
def build_graph():
    """Build and return a compiled LangGraph for the Gemini workflow."""
    g = StateGraph(State)
    g.add_node("generate", generate_node)
    g.add_node("create", None)  # This will be set in main.py
    g.add_edge("generate", "create")
    g.add_edge("create", END)
    g.set_entry_point("generate")
    return g

def get_compiled_graph(create_function):
    """Get a compiled graph with the create function set."""
    g = build_graph()
    g.set_node("create", create_function)
    return g.compile()
