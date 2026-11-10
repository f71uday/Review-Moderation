import time

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from reviewer.config import REVIEWS, check, get_model_with_tool, review, show
from reviewer.reply_and_alert import QUALITY_ALERTS, reply_and_alert
from reviewer.state import State
from reviewer.clean import clean_review
from reviewer.classifier_node import read_review
from reviewer.tools import after_agent, check_stock, get_care_instructions, get_size_chart, answer_agent as answer_agent_tool
from reviewer.triage import MODERATION_QUEUE, PUBLISHED, answer_agent, hide_review, look_up_facts, publish_review, triage as basic_triage
from reviewer.vendor import  count_complaints, get_return_rate, vendor_record


graph = StateGraph(State)
#Add nodes to the graph
graph.add_node("clean", clean_review)
graph.add_node("read", read_review)
graph.add_node("hide_review", hide_review)
graph.add_node("publish_review", publish_review)
graph.add_node("answer_agent",  answer_agent)
graph.add_node("look_up_facts", look_up_facts)

#define edges between nodes
graph.add_edge(START, "clean")
graph.add_edge("clean", "read")
graph.add_conditional_edges("read", basic_triage)
LANES = ["hide_review", "publish_review", "answer_agent", "look_up_facts"]
for lane in LANES:
    graph.add_edge(lane, END)


app = graph.compile()





...

LOOKUPS = ["count_complaints", "get_return_rate", "vendor_record"]
LOOKUP_NODES = {"count_complaints": count_complaints, "get_return_rate": get_return_rate,
                "vendor_record": vendor_record}

def triage(state: State):
    if state["kind"] == "complaint":
        return LOOKUPS
    return basic_triage(state)

in_a_row = StateGraph(State)
for name, fn in LOOKUP_NODES.items():
    in_a_row.add_node(name, fn)
in_a_row.add_edge(START, "count_complaints")
in_a_row.add_edge("count_complaints", "get_return_rate")
in_a_row.add_edge("get_return_rate", "vendor_record")
in_a_row.add_edge("vendor_record", END)
slow_lane = in_a_row.compile()

complaint = {"review": REVIEWS[2], "issue_type": "quality_defect"}
start = time.time(); slow_lane.invoke(complaint)
print(f"in a row: {time.time() - start:.1f} s")

...

at_once = StateGraph(State)
for name, fn in LOOKUP_NODES.items():
    at_once.add_node(name, fn)
at_once.add_edge(START, "count_complaints")
at_once.add_edge(START, "get_return_rate")
at_once.add_edge(START, "vendor_record")
at_once.add_edge("count_complaints", END)
at_once.add_edge("get_return_rate", END)
at_once.add_edge("vendor_record", END)
fast_lane = at_once.compile()

start = time.time(); facts = fast_lane.invoke(complaint)
print(f"at once: {time.time() - start:.1f} s")

found = [facts.get(k) for k in ["complaint_count", "return_rate", "vendor_alerts"]]
check("R-3: 6 complaints, 16% returns, 2 vendor alerts", found == [6, 16.0, 2], found)
start = time.time(); fast_lane.invoke(complaint)
check("At once takes about 0.5 s, not 1.5 s", time.time() - start < 1.2)

r3 = {"review": REVIEWS[2], "text": REVIEWS[2]["text"], "kind": "complaint"}
check("A complaint starts all 3 lookups", triage(r3) == LOOKUPS)

...

lane = StateGraph(State)
for name, fn in LOOKUP_NODES.items():
    lane.add_node(name, fn)
    lane.add_edge(START, name)

lane.add_node("reply_and_alert", reply_and_alert)
lane.add_node("publish_review", publish_review)

lane.add_edge("count_complaints", "reply_and_alert")
lane.add_edge("get_return_rate", "reply_and_alert")
lane.add_edge("vendor_record", "reply_and_alert")
lane.add_edge("reply_and_alert", "publish_review")
lane.add_edge("publish_review", END)

complaint_lane = lane.compile()

QUALITY_ALERTS.clear(); PUBLISHED.clear()
for r in [REVIEWS[2], REVIEWS[3]]:
    start_state = {"review": r, "text": r["text"], "issue_type": "quality_defect"}
    final = complaint_lane.invoke(start_state)
    print(r["review_id"], "| reply:", final["reply"])
print("alerts for:", [a["sku"] for a in QUALITY_ALERTS])



for r in [REVIEWS[1], REVIEWS[6]]:
    ai = get_model_with_tool().invoke((f"Product {r['sku']}: {r['text']}"))
    print(r["review_id"], "asks for:", [(c["name"], c["args"]) for c in ai.tool_calls])


loop = StateGraph(State)
loop.add_node("answer_agent", answer_agent_tool)
loop.add_node("tools", ToolNode([get_size_chart, get_care_instructions, check_stock]))                           # 🛠️ Blank 1
loop.add_node("publish_review", publish_review)
loop.add_edge(START, "answer_agent")
loop.add_conditional_edges("answer_agent", after_agent, ["tools", "publish_review"])
loop.add_edge("tools", "answer_agent")
loop.add_edge("publish_review", END)
question_lane = loop.compile()

show(question_lane) 
#TODO Review & would need 2 trips as per collab and as per my understanding as well , but its getting the answer in a Single Trip  How 
for r in [ REVIEWS[6]]:
    f = question_lane.invoke({"review": r, "text": r["text"]})
    print(r["review_id"], "| trips:", f["trips"], "|", f.get("answer"))


TOOLS = [get_size_chart, get_care_instructions, check_stock]
full = StateGraph(State)
full.add_node("clean_review", clean_review)
full.add_node("read_review", read_review)
full.add_node("hide_review", hide_review)
full.add_node("publish_review", publish_review)
for name, fn in LOOKUP_NODES.items():
    full.add_node(name, fn)
full.add_node("reply_and_alert", reply_and_alert)
full.add_node("answer_agent", answer_agent_tool)
full.add_node("tools", ToolNode(TOOLS))
LANES = ["hide_review", "publish_review", "answer_agent"] + LOOKUPS

full.add_edge(START, "clean_review")
full.add_edge("clean_review", "read_review")
full.add_conditional_edges(
    "read_review",
    triage,
    LANES,
)
full.add_edge("hide_review", END)
full.add_edge("publish_review", END)
for name in LOOKUPS:
    full.add_edge(name, "reply_and_alert")                                                  # 🛠️ Blank 2
full.add_edge("reply_and_alert", "publish_review")

full.add_conditional_edges("answer_agent", after_agent, ["tools", "publish_review"])
full.add_edge("tools", "answer_agent")
full.add_edge("publish_review", END)                                                  # 🛠️ Blank 3

review_system = full.compile()

show(review_system)


def run_all(graph, reviews=REVIEWS):
    MODERATION_QUEUE.clear(); PUBLISHED.clear(); QUALITY_ALERTS.clear()
    finals = {}
    for r in reviews:
        path = []
        for mode, chunk in graph.stream({"review": r}, stream_mode=["updates", "values"]):
            if mode == "updates":
                path += list(chunk)                # the node(s) that just ran
            else:
                finals[r["review_id"]] = chunk     # the state so far
        print(r["review_id"], "->", " -> ".join(path))
    return finals

#finals = run_all(review_system)



#response = review_system.invoke({"review": REVIEWS[6], "text": REVIEWS[6]["text"]})


NEW_REVIEWS = [
    review("N-1", "HS-305", 5, "Great fit, my daughter loves the dungaree."),
    review("N-2", "HS-201", 3, "Does it fit a 95 cm toddler, and is it in stock?"),
    review("N-3", "HS-118", 2, "The print started peeling after two washes."),
    review("N-4", "HS-412", 1, "You idiots sent the wrong pair. Email me at riya.k@gmail.com"),
]
new = run_all(review_system, NEW_REVIEWS)
for rid, f in new.items():
    print(rid, "|", f["status"], "|", f.get("answer") or f.get("reply") or f["text"])