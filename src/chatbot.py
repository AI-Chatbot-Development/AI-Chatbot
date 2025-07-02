import json
import os

def load_faq(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(__file__), '../data/faq.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_answer(user_query, faq=None):
    if faq is None:
        faq = load_faq()
    for item in faq:
        patterns = item.get("patterns", [])
        response = item.get("response", "")
        if user_query.lower() in [pattern.lower() for pattern in patterns]:
            return response
    return "Sorry, I couldn't find an answer to your question."


