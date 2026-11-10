import re
from reviewer.state import State
from reviewer.config import review

PHONE = re.compile(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?[\d\s]{7,10}')
EMAIL = re.compile(r'[\w\.-]+@[\w\.-]+')
LINK = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

def clean_review(state: State) -> State:
    """Cleans a review by removing phone numbers, emails, and links."""
    text = state["review"]["text"]
    text = PHONE.sub("[REDACTED PHONE]", text)
    text = EMAIL.sub("[REDACTED EMAIL]", text)
    text = LINK.sub("[REDACTED LINK]", text)
    return {"text": text}

