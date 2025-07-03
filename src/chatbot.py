import json
import os
from nlp_agent import get_best_match

def load_faq(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(__file__), '../data/faq.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

from nlp_agent import get_best_match

def get_answer(user_query, faq=None):
    if faq is None:
        faq = load_faq()
    all_patterns = []
    pattern_to_response = {}
    for item in faq:
        for pattern in item.get("patterns", []):
            all_patterns.append(pattern)
            pattern_to_response[pattern] = item.get("response", "")
    
    # Check if we have any patterns to match against
    if not all_patterns:
        return None
        
    best_q, score = get_best_match(user_query, all_patterns)
    if best_q:
        return pattern_to_response[best_q]
    return None


