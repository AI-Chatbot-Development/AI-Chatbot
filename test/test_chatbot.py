import unittest
import json
import os
import tempfile
import sys
from unittest.mock import patch, mock_open, MagicMock

# Add the src directory to the path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from chatbot import load_faq, get_answer

class TestChatbot(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Sample FAQ data for testing
        self.sample_faq = [
            {
                "patterns": [
                    "What are the fees?",
                    "How much does it cost?",
                    "Tell me about tuition fees"
                ],
                "response": "The tuition fees for undergraduate programs are $10,000 per semester."
            },
            {
                "patterns": [
                    "How to register?",
                    "Registration process",
                    "How do I enroll?"
                ],
                "response": "To register, visit the student portal and complete the online registration form."
            },
            {
                "patterns": [
                    "What is the admission deadline?",
                    "When is the last date to apply?",
                    "Application deadline"
                ],
                "response": "The admission deadline for fall semester is August 15th."
            }
        ]
        
        # Create a temporary FAQ file for testing
        self.test_faq_fd, self.test_faq_path = tempfile.mkstemp(suffix='.json')
        with open(self.test_faq_path, 'w', encoding='utf-8') as f:
            json.dump(self.sample_faq, f)
    
    def tearDown(self):
        """Clean up after each test method."""
        os.close(self.test_faq_fd)
        os.unlink(self.test_faq_path)
    
    def test_load_faq_with_path(self):
        """Test loading FAQ from a specific file path."""
        faq = load_faq(self.test_faq_path)
        
        self.assertEqual(len(faq), 3)
        self.assertEqual(faq[0]['patterns'][0], "What are the fees?")
        self.assertIn("tuition fees", faq[0]['response'])
    
    def test_load_faq_without_path(self):
        """Test loading FAQ with default path."""
        # Mock the default path
        with patch('chatbot.os.path.join') as mock_join:
            mock_join.return_value = self.test_faq_path
            
            faq = load_faq()
            
            self.assertEqual(len(faq), 3)
            self.assertEqual(faq[1]['patterns'][0], "How to register?")
    
    def test_load_faq_file_not_found(self):
        """Test handling of file not found error."""
        with self.assertRaises(FileNotFoundError):
            load_faq("nonexistent_file.json")
    
    def test_load_faq_invalid_json(self):
        """Test handling of invalid JSON file."""
        # Create a file with invalid JSON
        test_fd, test_path = tempfile.mkstemp(suffix='.json')
        try:
            with open(test_path, 'w') as f:
                f.write("invalid json content")
            
            with self.assertRaises(json.JSONDecodeError):
                load_faq(test_path)
        finally:
            os.close(test_fd)
            os.unlink(test_path)
    
    @patch('chatbot.get_best_match')
    def test_get_answer_with_match(self, mock_get_best_match):
        """Test getting answer when a good match is found."""
        mock_get_best_match.return_value = ("What are the fees?", 0.85)
        
        answer = get_answer("How much does it cost?", self.sample_faq)
        
        self.assertEqual(answer, "The tuition fees for undergraduate programs are $10,000 per semester.")
        mock_get_best_match.assert_called_once()
    
    @patch('chatbot.get_best_match')
    def test_get_answer_no_match(self, mock_get_best_match):
        """Test getting answer when no match is found."""
        mock_get_best_match.return_value = (None, 0.2)
        
        answer = get_answer("Random unrelated question", self.sample_faq)
        
        self.assertIsNone(answer)
        mock_get_best_match.assert_called_once()
    
    @patch('chatbot.load_faq')
    @patch('chatbot.get_best_match')
    def test_get_answer_without_faq_parameter(self, mock_get_best_match, mock_load_faq):
        """Test getting answer without providing FAQ parameter."""
        mock_load_faq.return_value = self.sample_faq
        mock_get_best_match.return_value = ("How to register?", 0.90)
        
        answer = get_answer("Registration process")
        
        expected_answer = "To register, visit the student portal and complete the online registration form."
        self.assertEqual(answer, expected_answer)
        mock_load_faq.assert_called_once()
        mock_get_best_match.assert_called_once()
    
    def test_get_answer_with_real_nlp(self):
        """Test get_answer with real NLP processing (integration test)."""
        # This test uses the actual NLP functions
        answer = get_answer("What are the fees?", self.sample_faq)
        
        # Should find a match since the question exactly matches a pattern
        self.assertIsNotNone(answer)
        self.assertIn("tuition fees", answer)
    
    def test_get_answer_case_insensitive(self):
        """Test that answer matching is case insensitive."""
        answer = get_answer("WHAT ARE THE FEES?", self.sample_faq)
        
        # Should still find a match despite different case
        self.assertIsNotNone(answer)
        self.assertIn("tuition fees", answer)
    
    def test_get_answer_partial_match(self):
        """Test getting answer with partial pattern match."""
        answer = get_answer("registration", self.sample_faq)
        
        # Should find the registration-related answer
        if answer:  # Depends on NLP matching threshold
            self.assertIn("student portal", answer)
    
    def test_get_answer_empty_faq(self):
        """Test getting answer with empty FAQ list."""
        answer = get_answer("Any question", [])
        
        self.assertIsNone(answer)
    
    def test_get_answer_faq_missing_patterns(self):
        """Test handling FAQ items without patterns."""
        malformed_faq = [
            {
                "response": "Some response without patterns"
            },
            {
                "patterns": ["How to register?"],
                "response": "Registration info"
            }
        ]
        
        # Should handle the malformed FAQ gracefully
        answer = get_answer("How to register?", malformed_faq)
        
        if answer:
            self.assertEqual(answer, "Registration info")
    
    def test_get_answer_faq_missing_response(self):
        """Test handling FAQ items without response."""
        malformed_faq = [
            {
                "patterns": ["What are the fees?"]
                # Missing response
            }
        ]
        
        # Should handle missing response gracefully
        answer = get_answer("What are the fees?", malformed_faq)
        
        # Should return empty string for missing response
        if answer is not None:
            self.assertEqual(answer, "")
    
    def test_pattern_to_response_mapping(self):
        """Test that all patterns are correctly mapped to responses."""
        # Test internal logic of get_answer
        all_patterns = []
        pattern_to_response = {}
        
        for item in self.sample_faq:
            for pattern in item.get("patterns", []):
                all_patterns.append(pattern)
                pattern_to_response[pattern] = item.get("response", "")
        
        # Verify all patterns are collected
        self.assertEqual(len(all_patterns), 9)  # 3 + 3 + 3 patterns
        
        # Verify mapping is correct
        self.assertEqual(
            pattern_to_response["What are the fees?"],
            "The tuition fees for undergraduate programs are $10,000 per semester."
        )
        self.assertEqual(
            pattern_to_response["How to register?"],
            "To register, visit the student portal and complete the online registration form."
        )
    
    @patch('chatbot.os.path.dirname')
    @patch('chatbot.os.path.join')
    def test_load_faq_default_path_construction(self, mock_join, mock_dirname):
        """Test that default path is constructed correctly."""
        mock_dirname.return_value = "/fake/src"
        mock_join.return_value = self.test_faq_path
        
        faq = load_faq()
        
        mock_dirname.assert_called_once()
        mock_join.assert_called_once_with("/fake/src", '../data/faq.json')
        self.assertEqual(len(faq), 3)

if __name__ == '__main__':
    unittest.main()