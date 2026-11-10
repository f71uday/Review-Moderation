SIZE_CHARTS = {"HS-118": {"3-4Y": "98-104 cm", "4-5Y": "104-110 cm", "5-6Y": "110-116 cm"},
               "HS-201": {"2-3Y": "92-98 cm", "3-4Y": "98-104 cm", "4-5Y": "104-110 cm"}}
CARE = {"HS-118": "Machine wash cold. Do not tumble dry.",
        "HS-201": "Machine wash cold, inside out, with similar colours."}
STOCK = {"HS-118": {"3-4Y": 14, "4-5Y": 9, "5-6Y": 0},
         "HS-201": {"2-3Y": 6, "3-4Y": 0, "4-5Y": 12}}

AGENT_RULES = """You answer customers' questions in Hopscotch reviews.
Use the tools for facts; never guess. Ask for independent tools together.
When you have the facts, reply with the answer only: friendly, under 50 words."""
MAX_TRIPS = 4

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

from reviewer.config import get_model_with_tool
from reviewer.state import State

@tool
def get_size_chart(sku: str) -> dict:
    """The size chart of a product: each size label (like 4-5Y) and the height it fits."""
    return SIZE_CHARTS.get(sku, {})

@tool
def get_care_instructions(sku: str) -> str:
    """How to wash and dry a product."""
    return CARE.get(sku, "unknown")

@tool
def check_stock(sku: str, size: str) -> dict:
    """Check if a product size is in stock."""
    return {"size": size, "in_stock": STOCK.get(sku, {}).get(size)}


def answer_agent(state: State):
    question = HumanMessage(f"Product: {state['review']['sku']}\nReview: {state['text']}")
    history = [SystemMessage(AGENT_RULES), question] + state.get("messages", [])
    response = get_model_with_tool().invoke(history)

    update, trips = {"messages": [response]}, state.get("trips", 0)
    if response.tool_calls:
        update["trips"] = trips+1  
    else:                                            # 🛠️ Blank 1
        update["answer"] = response.content                                       # 🛠️ Blank 2
    
    return update

def after_agent(state: State):
       
    if state.get("answer"):
        return "publish_review"         # the cap: publish with an answer
    elif state.get("trips", 0) > MAX_TRIPS:
        return "publish_review"            # the cap: publish without an answer
    return "tools"