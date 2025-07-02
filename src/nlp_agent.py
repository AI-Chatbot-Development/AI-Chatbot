import spacy
from difflib import SequenceMatcher

try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    nlp = spacy.blank("en")

def preprocess(text):
    doc = nlp(text.lower())
    return " ".join([token.lemma_ for token in doc if not token.is_stop and token.is_alpha])

def token_overlap(a, b):
    set_a = set(a.lower().split())
    set_b = set(b.lower().split())
    return len(set_a & set_b) / max(1, len(set_a | set_b))

def get_best_match(user_query, questions, threshold=0.8):
    user_doc = nlp(preprocess(user_query))
    best_score = 0
    best_question = None
    for question in questions:
        faq_doc = nlp(preprocess(question))
        sim_score = user_doc.similarity(faq_doc)
        overlap_score = token_overlap(user_query, question)
        fuzzy_score = SequenceMatcher(None, user_query.lower(), question.lower()).ratio()
        score = (sim_score + overlap_score + fuzzy_score) / 3
        if score > best_score:
            best_score = score
            best_question = question
    if best_score >= threshold:
        return best_question, best_score
    return None, best_score

def get_all_matches(user_query, questions):
    user_doc = nlp(preprocess(user_query))
    matches = []
    for question in questions:
        faq_doc = nlp(preprocess(question))
        sim_score = user_doc.similarity(faq_doc)
        overlap_score = token_overlap(user_query, question)
        fuzzy_score = SequenceMatcher(None, user_query.lower(), question.lower()).ratio()
        score = (sim_score + overlap_score + fuzzy_score) / 3
        matches.append((question, score))
    
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches