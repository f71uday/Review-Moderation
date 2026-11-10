from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from reviewer.config import get_llm
from reviewer.state import State

REPLY_RULES = """Say sorry and thank them. Say it is passed on to the quality team.
Never promise a refund or discount: returns go through the Orders page. Under 50 words."""

reply_prompt = ChatPromptTemplate.from_messages([
    ("system", "You write Hopscotch's public replies to complaints. Rules:\n" + REPLY_RULES),
    ("human", "Review ({rating} stars): {text}"),
])
reply_writer = reply_prompt | get_llm() | StrOutputParser()

ALERT_INSTRUCTION =  """Turn the review and evidence into a clear, actionable quality escalation for the product team.
State the issue and its customer impact; be factual, concise, and do not infer missing details."""                            

alert_prompt = ChatPromptTemplate.from_messages([
    ("system", ALERT_INSTRUCTION),
    ("human", "Product: {sku}\nReview: {text}\nEvidence: {evidence}"),
])
alert_writer = alert_prompt | get_llm() | StrOutputParser()
QUALITY_ALERTS = []


def reply_and_alert(state: State):
    reply = reply_writer.invoke({"rating": state["review"]["rating"], "text": state["text"]})

    evidence = state["complaint_count"] + state["return_rate"] + state["vendor_alerts"]     # 🛠️ Blank 1
    alert = alert_writer.invoke({"sku": state["review"]["sku"], "text": state["text"],
                                 "evidence": evidence})
    QUALITY_ALERTS.append({"sku": state["review"]["sku"], "alert": alert})

    return {"reply": reply}