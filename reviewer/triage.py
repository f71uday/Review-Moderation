from typing_extensions import Literal

from langchain_core.tools import tool

from reviewer.classifier_node import read_review
from reviewer.clean import LINK
from reviewer.state import State


def triage(state: State) -> Literal["hide_review", "publish_review", "answer_agent"]:
    
    if state["kind"] == "complaint":
        return "hide_review", "publish_review", "answer_agent"
    if state["kind"] == "abusive":
        return "hide_review"
   
    if state["kind"] == "question":
        return "answer_agent"
    else :
        return "publish_review"


MODERATION_QUEUE, PUBLISHED = [], []

def hide_review(state: State):
    reason = "spam link" if LINK.search(state["text"]) else "abuse"
    MODERATION_QUEUE.append(state["review"]["review_id"])
    return {"status": f"hidden: {reason}"}

def publish_review(state: State):
    entry = {"review_id": state["review"]["review_id"], "text": state["text"]}
    for k in ["reply", "answer"]:              
        if state.get(k):
            entry[k] = state[k]
    PUBLISHED.append(entry)
    return {"status": "published"}

def answer_agent(state: State):
    return {"status": "question lane (Part 6)"}

def look_up_facts(state: State):
    return {"status": "complaint lane (Part 3)"}
