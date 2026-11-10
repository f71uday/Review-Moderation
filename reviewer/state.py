import operator
from typing import Annotated, Literal,TypedDict
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

class State(TypedDict):
    messages: Annotated[list, operator.add]
    review: dict
    # the spine (Part 1)
    text: str             # the text, with phone numbers and emails hidden
    kind: str             # praise, question, complaint or abusive
    issue_type: str       # what a complaint is about
    status: str             # the final status of the review, e.g. published, hidden, etc.
    # the complaint lane (Parts 3 and 4)
    complaint_count: int
    return_rate: float
    vendor_alerts: int
    reply: str
    trips: int  # how many times the review has been processed
    answer: str  # the answer to a question, if any
class ReviewRead(BaseModel):
    kind: Literal["praise", "question", "complaint", "abusive"]
    issue_type: Literal["none", "size_fit", "quality_defect", "delivery", "other"] = Field(
        description="What a complaint is about; none for other kinds")

read_prompt = ChatPromptTemplate.from_messages([
    ("system", "You read product reviews for Hopscotch, a kids' clothing store."),
    ("human", "Rating: {rating} stars\nReview: {text}"),
])
