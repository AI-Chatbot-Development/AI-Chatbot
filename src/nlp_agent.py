import spacy
import streamlit as st
from sentence_transformers import SentenceTransformer, util
from difflib import SequenceMatcher
import re

@st.cache_resource
def load_sentence_transformer():
    """Loads the SentenceTransformer model and caches it."""
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_sentence_transformer()

try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    nlp = spacy.blank("en")

def preprocess(text):
    """Enhanced preprocessing with better text normalization"""
    text = re.sub(r'[^\w\s]', '', text.lower())
    text = re.sub(r'\s+', ' ', text).strip()
    
    if nlp.lang == "en":
        doc = nlp(text)
        return " ".join([token.lemma_ for token in doc if not token.is_stop and token.is_alpha])
    else:
        # Fallback for blank model
        return text

def fuzzy_match_score(a, b):
    """Calculate fuzzy matching score using SequenceMatcher"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def enhanced_similarity(query, pattern):
    """Enhanced similarity combining semantic and fuzzy matching"""
    # Semantic similarity using sentence transformers
    query_emb = model.encode(query, convert_to_tensor=True)
    pattern_emb = model.encode(pattern, convert_to_tensor=True)
    semantic_score = util.cos_sim(query_emb, pattern_emb)[0][0].item()
    
    # Fuzzy string matching for typos
    fuzzy_score = fuzzy_match_score(query, pattern)
    
    # Token overlap for keyword matching
    overlap_score = token_overlap(query, pattern)
    
    # Weighted combination - prioritize semantic similarity but boost fuzzy for typos
    final_score = (
        semantic_score * 0.6 +  # Primary: semantic understanding
        fuzzy_score * 0.25 +    # Secondary: typo tolerance
        overlap_score * 0.15    # Tertiary: keyword overlap
    )
    
    return final_score

def correct_common_typos(text):
    """Fix common typos and spelling mistakes"""
    corrections = {
        'attendce': 'attendance',
        'mandtory': 'mandatory',
        'compulsry': 'compulsory',
        'registrtion': 'registration',
        'pyment': 'payment',
        'instllments': 'installments',
        'transcrit': 'transcript',
        'collge': 'college',
        'univrsity': 'university',
        'stuent': 'student',
        'clas': 'class',
        'cours': 'course',
        'fee': 'fees',
        'requirment': 'requirement',
        'semster': 'semester',
        'graduat': 'graduation',
        'advisr': 'advisor',
        'exempton': 'exemption',
        'repetition': 'repeat'
    }
    
    words = text.split()
    corrected_words = []
    
    for word in words:
        word_lower = word.lower()
        corrected = corrections.get(word_lower, word)
        corrected_words.append(corrected)
    
    return ' '.join(corrected_words)

def token_overlap(a, b):
    set_a = set(a.lower().split())
    set_b = set(b.lower().split())
    return len(set_a & set_b) / max(1, len(set_a | set_b))

def get_best_match(user_query, questions, threshold=0.45):
    """Enhanced matching with typo correction and multiple scoring methods"""
    corrected_query = correct_common_typos(user_query)
    
    best_score = 0
    best_question = None
    best_idx = -1
    
    queries_to_try = [user_query, corrected_query] if corrected_query != user_query else [user_query]
    
    for query in queries_to_try:
        for i, question in enumerate(questions):
            score = enhanced_similarity(query, question)
            if score > best_score:
                best_score = score
                best_question = question
                best_idx = i
        
        query_embedding = model.encode(query, convert_to_tensor=True)
        question_embeddings = model.encode(questions, convert_to_tensor=True)
        cosine_scores = util.cos_sim(query_embedding, question_embeddings)
        max_score, max_idx = cosine_scores[0].max(dim=0)
        
        if max_score.item() > best_score:
            best_score = max_score.item()
            best_question = questions[max_idx]
            best_idx = max_idx
    
    if best_score >= threshold:
        return best_question, best_score
    
    return None, best_score

def get_all_matches(user_query, questions):
    """Enhanced matching that returns all matches with improved scoring"""
    corrected_query = correct_common_typos(user_query)
    
    matches = []
    
    queries_to_try = [user_query, corrected_query] if corrected_query != user_query else [user_query]
    
    for query in queries_to_try:
        for question in questions:
            score = enhanced_similarity(query, question)
            matches.append((question, score))
    
    unique_matches = {}
    for question, score in matches:
        if question not in unique_matches or score > unique_matches[question]:
            unique_matches[question] = score
    
    final_matches = [(q, s) for q, s in unique_matches.items()]
    final_matches.sort(key=lambda x: x[1], reverse=True)
    
    return final_matches
