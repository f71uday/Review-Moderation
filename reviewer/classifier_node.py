
from reviewer.state import ReviewRead, State, read_prompt
from reviewer.config import get_llm


def read_review(state: State) -> State:
    """Classifies a review using the ReviewRead structured output schema."""
    llm = get_llm().with_structured_output(ReviewRead)
    chain = read_prompt | llm
    result: ReviewRead = chain.invoke({
        "rating": state["review"]["rating"],
        "text": state["text"],
    })
    return {
        "kind": result.kind,
        "issue_type": result.issue_type,
    }
