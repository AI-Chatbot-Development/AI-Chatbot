import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import numpy as np

# Add the src directory to the path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from nlp_agent import (
    preprocess,
    fuzzy_match_score,
    enhanced_similarity,
    correct_common_typos,
    token_overlap,
    get_best_match,
    get_all_matches
)

class TestNLPAgent(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Sample questions for testing
        self.sample_questions = [
            "What are the admission requirements?",
            "How much are the tuition fees?",
            "When is the registration deadline?",
            "How do I apply for financial aid?",
            "What courses are offered?",
            "Where is the campus located?"
        ]

    def test_preprocess_basic_text(self):
        """Test basic text preprocessing."""
        text = "Hello World! How are you?"
        result = preprocess(text)
        
        # Should remove punctuation and convert to lowercase
        self.assertNotIn("!", result)
        self.assertNotIn("?", result)
        self.assertEqual(result.lower(), result)
    
    def test_preprocess_special_characters(self):
        """Test preprocessing with special characters."""
        text = "What's the cost? (Including fees & taxes)"
        result = preprocess(text)
        
        # Should handle special characters
        self.assertNotIn("'", result)
        self.assertNotIn("(", result)
        self.assertNotIn(")", result)
        self.assertNotIn("&", result)
    
    def test_preprocess_multiple_spaces(self):
        """Test preprocessing with multiple spaces."""
        text = "Hello    world     test"
        result = preprocess(text)
        
        # Should normalize spaces
        self.assertNotIn("    ", result)
        self.assertNotIn("     ", result)
    
    def test_preprocess_empty_string(self):
        """Test preprocessing with empty string."""
        result = preprocess("")
        self.assertEqual(result, "")
    
    def test_preprocess_numbers_and_text(self):
        """Test preprocessing with numbers and text."""
        text = "The cost is $1000 per semester"
        result = preprocess(text)
        
        # Should handle numbers appropriately
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) >= 0)
    
    def test_fuzzy_match_score_identical(self):
        """Test fuzzy matching with identical strings."""
        score = fuzzy_match_score("hello world", "hello world")
        self.assertEqual(score, 1.0)
    
    def test_fuzzy_match_score_completely_different(self):
        """Test fuzzy matching with completely different strings."""
        score = fuzzy_match_score("hello", "xyz123")
        self.assertLess(score, 0.5)
    
    def test_fuzzy_match_score_case_insensitive(self):
        """Test that fuzzy matching is case insensitive."""
        score1 = fuzzy_match_score("Hello World", "hello world")
        score2 = fuzzy_match_score("HELLO WORLD", "hello world")
        
        self.assertEqual(score1, 1.0)
        self.assertEqual(score2, 1.0)
    
    def test_fuzzy_match_score_partial_match(self):
        """Test fuzzy matching with partial similarity."""
        score = fuzzy_match_score("hello world", "hello earth")
        
        # Should have some similarity but not perfect
        self.assertGreater(score, 0.5)
        self.assertLess(score, 1.0)
    
    def test_fuzzy_match_score_typos(self):
        """Test fuzzy matching with typos."""
        score = fuzzy_match_score("registration", "registrtion")  # missing 'a'
        
        # Should still have high similarity despite typo
        self.assertGreater(score, 0.8)
    
    def test_correct_common_typos_basic(self):
        """Test basic typo correction."""
        text = "What are the attendce requirements?"
        corrected = correct_common_typos(text)
        
        self.assertIn("attendance", corrected)
        self.assertNotIn("attendce", corrected)
    
    def test_correct_common_typos_multiple(self):
        """Test correction of multiple typos."""
        text = "registrtion and pyment info"
        corrected = correct_common_typos(text)
        
        self.assertIn("registration", corrected)
        self.assertIn("payment", corrected)
    
    def test_correct_common_typos_no_typos(self):
        """Test text without typos remains unchanged."""
        text = "This is correct text"
        corrected = correct_common_typos(text)
        
        self.assertEqual(text, corrected)
    
    def test_correct_common_typos_case_preservation(self):
        """Test that case is preserved for non-typo words."""
        text = "The Univrsity offers many courses"
        corrected = correct_common_typos(text)
        
        # The typo correction function converts everything to lowercase, 
        # so we should check for the corrected word
        self.assertIn("university", corrected.lower())  # Check corrected word exists
        self.assertIn("The", corrected)  # Case preserved for non-typo words
    
    def test_correct_common_typos_education_terms(self):
        """Test correction of education-specific typos."""
        typos = {
            "collge": "college",
            "stuent": "student", 
            "semster": "semester",
            "cours": "course"
        }
        
        for typo, correct in typos.items():
            result = correct_common_typos(f"The {typo} information")
            self.assertIn(correct, result.lower())
    
    def test_token_overlap_identical(self):
        """Test token overlap with identical strings."""
        overlap = token_overlap("hello world", "hello world")
        self.assertEqual(overlap, 1.0)
    
    def test_token_overlap_no_overlap(self):
        """Test token overlap with no common words."""
        overlap = token_overlap("hello world", "foo bar")
        self.assertEqual(overlap, 0.0)
    
    def test_token_overlap_partial(self):
        """Test token overlap with partial word overlap."""
        overlap = token_overlap("hello world test", "hello foo bar")
        
        # Should be 1/5 = 0.2 (1 common word "hello" out of 5 unique words: hello, world, test, foo, bar)
        self.assertAlmostEqual(overlap, 0.2, places=2)
    
    def test_token_overlap_case_insensitive(self):
        """Test that token overlap is case insensitive."""
        overlap = token_overlap("Hello World", "hello world")
        self.assertEqual(overlap, 1.0)
    
    def test_token_overlap_repeated_words(self):
        """Test token overlap with repeated words."""
        overlap = token_overlap("hello hello world", "hello world world")
        
        # Should handle repeated words correctly
        self.assertGreater(overlap, 0.5)
    
    def test_token_overlap_empty_strings(self):
        """Test token overlap with empty strings."""
        overlap = token_overlap("", "hello")
        self.assertEqual(overlap, 0.0)
        
        overlap = token_overlap("", "")
        self.assertEqual(overlap, 0.0)
    
    @patch('nlp_agent.model')
    def test_enhanced_similarity_mock(self, mock_model):
        """Test enhanced similarity with mocked model."""
        # Mock the sentence transformer model
        mock_tensor = MagicMock()
        mock_tensor.item.return_value = 0.8
        mock_model.encode.return_value = MagicMock()
        
        # Mock the cosine similarity result
        with patch('nlp_agent.util.cos_sim') as mock_cos_sim:
            mock_cos_sim.return_value = [[mock_tensor]]  # Mock similarity score with tensor-like behavior
            
            score = enhanced_similarity("hello world", "hello earth")
            
            # Should return a score between 0 and 1
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
    
    def test_enhanced_similarity_identical_strings(self):
        """Test enhanced similarity with identical strings."""
        score = enhanced_similarity("admission requirements", "admission requirements")
        
        # Should have very high similarity
        self.assertGreater(score, 0.8)
    
    def test_enhanced_similarity_different_strings(self):
        """Test enhanced similarity with very different strings."""
        score = enhanced_similarity("admission requirements", "pizza recipe")
        
        # Should have low similarity
        self.assertLess(score, 0.5)
    
    def test_enhanced_similarity_related_strings(self):
        """Test enhanced similarity with semantically related strings."""
        score = enhanced_similarity("tuition fees", "cost of education")
        
        # Should have moderate to high similarity (depends on the model)
        self.assertGreater(score, 0.3)  # Conservative threshold
    
    def test_get_best_match_exact_match(self):
        """Test get_best_match with exact match."""
        query = "What are the admission requirements?"
        questions = self.sample_questions
        
        best_question, score = get_best_match(query, questions)
        
        self.assertEqual(best_question, "What are the admission requirements?")
        self.assertGreater(score, 0.9)
    
    def test_get_best_match_no_match(self):
        """Test get_best_match with no good matches."""
        query = "random unrelated question about pizza"
        questions = self.sample_questions
        
        best_question, score = get_best_match(query, questions, threshold=0.8)
        
        # Should return None if no match above threshold
        if score < 0.8:
            self.assertIsNone(best_question)
    
    def test_get_best_match_with_typos(self):
        """Test get_best_match with typos in query."""
        query = "What are the admision requirements?"  # 'admision' instead of 'admission'
        questions = self.sample_questions
        
        best_question, score = get_best_match(query, questions)
        
        # Should still find the correct match despite typo
        self.assertIsNotNone(best_question)
        self.assertIn("admission", best_question.lower())
    
    def test_get_best_match_case_insensitive(self):
        """Test get_best_match is case insensitive."""
        query = "WHAT ARE THE ADMISSION REQUIREMENTS?"
        questions = self.sample_questions
        
        best_question, score = get_best_match(query, questions)
        
        self.assertIsNotNone(best_question)
        self.assertIn("admission", best_question.lower())
    
    def test_get_best_match_partial_query(self):
        """Test get_best_match with partial query."""
        query = "tuition fees"
        questions = self.sample_questions
        
        best_question, score = get_best_match(query, questions)
        
        # Should find the fees-related question
        if best_question:
            self.assertIn("fees", best_question.lower())
    

    
    def test_get_all_matches_basic(self):
        """Test get_all_matches returns sorted results."""
        query = "admission"
        questions = self.sample_questions
        
        matches = get_all_matches(query, questions)
        
        # Should return list of tuples (question, score)
        self.assertIsInstance(matches, list)
        
        if matches:
            self.assertIsInstance(matches[0], tuple)
            self.assertEqual(len(matches[0]), 2)
            
            # Should be sorted by score (highest first)
            scores = [match[1] for match in matches]
            self.assertEqual(scores, sorted(scores, reverse=True))
    
    def test_get_all_matches_with_typos(self):
        """Test get_all_matches with typos in query."""
        query = "admision requirements"  # typo: 'admision'
        questions = self.sample_questions
        
        matches = get_all_matches(query, questions)
        
        # Should still find relevant matches
        self.assertIsInstance(matches, list)
        
        # Top match should be relevant to admission
        if matches:
            top_match = matches[0]
            self.assertIn("admission", top_match[0].lower())
    
    def test_get_all_matches_empty_questions(self):
        """Test get_all_matches with empty questions list."""
        query = "any question"
        questions = []
        
        matches = get_all_matches(query, questions)
        
        self.assertEqual(matches, [])
    
    def test_get_all_matches_duplicate_removal(self):
        """Test that get_all_matches removes duplicates."""
        query = "fees"
        questions = ["How much are fees?", "How much are fees?", "What about costs?"]
        
        matches = get_all_matches(query, questions)
        
        # Should not have duplicates
        question_texts = [match[0] for match in matches]
        self.assertEqual(len(question_texts), len(set(question_texts)))
    
    @patch('nlp_agent.correct_common_typos')
    def test_get_best_match_typo_correction_called(self, mock_correct_typos):
        """Test that typo correction is called in get_best_match."""
        mock_correct_typos.return_value = "corrected query"
        
        query = "original query"
        questions = self.sample_questions
        
        get_best_match(query, questions)
        
        # Verify typo correction was called
        mock_correct_typos.assert_called_with(query)
    
    def test_get_best_match_threshold_behavior(self):
        """Test get_best_match threshold behavior."""
        query = "completely unrelated random text"
        questions = self.sample_questions
        
        # With high threshold, should return None
        best_question, score = get_best_match(query, questions, threshold=0.9)
        
        if score < 0.9:
            self.assertIsNone(best_question)
        
        # With low threshold, might return something
        best_question, score = get_best_match(query, questions, threshold=0.1)
        
        if score >= 0.1:
            self.assertIsNotNone(best_question)

if __name__ == '__main__':
    unittest.main()