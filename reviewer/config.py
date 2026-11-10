import dotenv
import os
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

llm= ChatOpenAI(
    model_name="gpt-4o-mini",
    openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
    temperature=0.7,
    base_url="https://openrouter.ai/api/v1")

def get_llm():
    return llm
def review(review_id, sku, rating, text):
    return {"review_id": review_id, "sku": sku, "rating": rating, "text": text}


REVIEWS = [
    review("R-1", "HS-118", 5, "Lovely soft fabric, my son wears it every day."),
    review("R-2", "HS-201", 4, "Pretty frock! Machine washable? Is 4-5Y in stock?"),
    review("R-3", "HS-201", 2, "The colours bled into each other after the very first wash."),
    review("R-4", "HS-305", 2, "One strap button came off after a week. Otherwise good."),
    review("R-5", "HS-412", 1, "Worst shoes ever, you idiots. Call me on 98200 11223."),
    review("R-6", "HS-201", 5, "Great deals on kids wear at http://cheap-kids-wear.biz"),
    review("R-7", "HS-118", 4, "My daughter is 108 cm: which size, and is it in stock?"),
]

def check(name, ok, tip=""):
    print(f"✅ {name}" if ok else f"❌ {name}  {tip}")

def show(graph):
    """Saves a compiled graph as graph.png. Offline, prints the Mermaid code instead."""
    try:
        with open("graph.png", "wb") as image_file:
            image_file.write(graph.get_graph().draw_mermaid_png())
    except Exception:
        print(graph.get_graph().draw_mermaid())


def get_model_with_tool():
    from reviewer.tools import check_stock, get_care_instructions, get_size_chart

    return get_llm().bind_tools([get_size_chart, get_care_instructions, check_stock])