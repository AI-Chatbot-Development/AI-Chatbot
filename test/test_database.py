import unittest
import sqlite3
import os
import tempfile
import sys
from unittest.mock import patch, MagicMock

# Add the src directory to the path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import init_db, log_interaction, log_feedback, log_escalation

class TestDatabase(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary database for testing
        self.test_db_fd, self.test_db_path = tempfile.mkstemp()
        os.close(self.test_db_fd)  # Close the file descriptor
        
        # Patch the DB_PATH to use our test database
        self.db_path_patcher = patch('database.DB_PATH', self.test_db_path)
        self.db_path_patcher.start()
    
    def tearDown(self):
        """Clean up after each test method."""
        self.db_path_patcher.stop()
        if os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)

    def test_init_db_creates_tables(self):
        """Test that init_db creates the required tables."""
        init_db()
        
        # Check that database file was created
        self.assertTrue(os.path.exists(self.test_db_path))
        
        # Check that tables were created
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Check interactions table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='interactions';")
        self.assertIsNotNone(cursor.fetchone())
        
        # Check escalations table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='escalations';")
        self.assertIsNotNone(cursor.fetchone())
        
        conn.close()
    
    def test_init_db_table_schema(self):
        """Test that tables have correct schema."""
        init_db()
        
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Check interactions table schema
        cursor.execute("PRAGMA table_info(interactions)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        expected_columns = ['id', 'timestamp', 'user_query', 'bot_response', 'match_score', 'feedback', 'session_id']
        for col in expected_columns:
            self.assertIn(col, column_names)
        
        # Check escalations table schema
        cursor.execute("PRAGMA table_info(escalations)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        expected_columns = ['id', 'timestamp', 'user_query', 'suggested_answer']
        for col in expected_columns:
            self.assertIn(col, column_names)
        
        conn.close()
    
    def test_log_interaction_success(self):
        """Test logging an interaction successfully."""
        init_db()
        
        session_id = "test_session_123"
        query = "What are the fees?"
        response = "Fees are $1000"
        score = 0.85
        
        interaction_id = log_interaction(session_id, query, response, score)
        
        # Check that interaction_id is returned
        self.assertIsNotNone(interaction_id)
        self.assertIsInstance(interaction_id, int)
        
        # Verify data was inserted
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM interactions WHERE id = ?", (interaction_id,))
        row = cursor.fetchone()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[2], query)  # user_query
        self.assertEqual(row[3], response)  # bot_response
        self.assertEqual(row[4], score)  # match_score
        self.assertEqual(row[6], session_id)  # session_id
        
        conn.close()
    
    def test_log_interaction_multiple(self):
        """Test logging multiple interactions."""
        init_db()
        
        interactions = [
            ("session1", "Query 1", "Response 1", 0.8),
            ("session2", "Query 2", "Response 2", 0.9),
            ("session1", "Query 3", "Response 3", 0.7)
        ]
        
        ids = []
        for session_id, query, response, score in interactions:
            interaction_id = log_interaction(session_id, query, response, score)
            ids.append(interaction_id)
        
        # Verify all interactions were logged
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM interactions")
        count = cursor.fetchone()[0]
        
        self.assertEqual(count, 3)
        
        # Verify IDs are unique and sequential
        self.assertEqual(len(set(ids)), 3)  # All unique
        
        conn.close()
    
    def test_log_feedback_success(self):
        """Test logging feedback for an interaction."""
        init_db()
        
        # First create an interaction
        interaction_id = log_interaction("session1", "Test query", "Test response", 0.8)
        
        # Log feedback
        feedback = 1  # Positive feedback
        log_feedback(interaction_id, feedback)
        
        # Verify feedback was updated
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT feedback FROM interactions WHERE id = ?", (interaction_id,))
        stored_feedback = cursor.fetchone()[0]
        
        self.assertEqual(stored_feedback, feedback)
        conn.close()
    
    def test_log_feedback_negative(self):
        """Test logging negative feedback."""
        init_db()
        
        interaction_id = log_interaction("session1", "Test query", "Test response", 0.8)
        
        # Log negative feedback
        feedback = 0
        log_feedback(interaction_id, feedback)
        
        # Verify feedback was updated
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT feedback FROM interactions WHERE id = ?", (interaction_id,))
        stored_feedback = cursor.fetchone()[0]
        
        self.assertEqual(stored_feedback, feedback)
        conn.close()
    
    def test_log_feedback_nonexistent_interaction(self):
        """Test logging feedback for non-existent interaction."""
        init_db()
        
        # Try to log feedback for non-existent interaction
        # This should not raise an error, but also shouldn't affect anything
        log_feedback(999, 1)
        
        # Verify no interactions exist
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM interactions")
        count = cursor.fetchone()[0]
        
        self.assertEqual(count, 0)
        conn.close()
    
    def test_log_escalation_with_suggestion(self):
        """Test logging an escalation with a suggestion."""
        init_db()
        
        query = "Complex question that needs human help"
        suggestion = "This requires manual review by support team"
        
        log_escalation(query, suggestion)
        
        # Verify escalation was logged
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM escalations")
        row = cursor.fetchone()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[2], query)  # user_query
        self.assertEqual(row[3], suggestion)  # suggested_answer
        
        conn.close()
    
    def test_log_escalation_without_suggestion(self):
        """Test logging an escalation without a suggestion."""
        init_db()
        
        query = "Another complex question"
        
        log_escalation(query)
        
        # Verify escalation was logged
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM escalations")
        row = cursor.fetchone()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[2], query)  # user_query
        self.assertIsNone(row[3])  # suggested_answer should be None
        
        conn.close()
    
    def test_log_escalation_multiple(self):
        """Test logging multiple escalations."""
        init_db()
        
        escalations = [
            ("Query 1", "Suggestion 1"),
            ("Query 2", None),
            ("Query 3", "Suggestion 3")
        ]
        
        for query, suggestion in escalations:
            log_escalation(query, suggestion)
        
        # Verify all escalations were logged
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM escalations")
        count = cursor.fetchone()[0]
        
        self.assertEqual(count, 3)
        
        # Verify specific data
        cursor.execute("SELECT user_query, suggested_answer FROM escalations ORDER BY id")
        rows = cursor.fetchall()
        
        self.assertEqual(rows[0][0], "Query 1")
        self.assertEqual(rows[0][1], "Suggestion 1")
        self.assertEqual(rows[1][0], "Query 2")
        self.assertIsNone(rows[1][1])
        
        conn.close()
    
    def test_database_connection_error(self):
        """Test handling of database connection errors."""
        # Use a read-only directory path to cause permission error
        with patch('database.DB_PATH', '/invalid/path/test.db'):
            with self.assertRaises(sqlite3.OperationalError):
                init_db()
    
    def test_log_interaction_with_none_values(self):
        """Test logging interaction with None values."""
        init_db()
        
        # Test with None values
        interaction_id = log_interaction(None, None, None, None)
        
        self.assertIsNotNone(interaction_id)
        
        # Verify data was stored as None
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT session_id, user_query, bot_response, match_score FROM interactions WHERE id = ?", (interaction_id,))
        row = cursor.fetchone()
        
        self.assertIsNone(row[0])  # session_id
        self.assertIsNone(row[1])  # user_query
        self.assertIsNone(row[2])  # bot_response
        self.assertIsNone(row[3])  # match_score
        
        conn.close()
    
    def test_log_interaction_with_special_characters(self):
        """Test logging interaction with special characters."""
        init_db()
        
        session_id = "session_with_special_chars_!@#$%"
        query = "What's the cost? (Including fees & taxes)"
        response = "Cost is $1,000 + 10% tax = $1,100"
        score = 0.95
        
        interaction_id = log_interaction(session_id, query, response, score)
        
        # Verify data was stored correctly
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT session_id, user_query, bot_response FROM interactions WHERE id = ?", (interaction_id,))
        row = cursor.fetchone()
        
        self.assertEqual(row[0], session_id)
        self.assertEqual(row[1], query)
        self.assertEqual(row[2], response)
        
        conn.close()
    
    def test_init_db_multiple_calls(self):
        """Test that calling init_db multiple times doesn't cause errors."""
        # First call
        init_db()
        
        # Add some data
        interaction_id = log_interaction("session1", "query1", "response1", 0.8)
        
        # Second call should not affect existing data
        init_db()
        
        # Verify data still exists
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM interactions")
        count = cursor.fetchone()[0]
        
        self.assertEqual(count, 1)
        conn.close()

if __name__ == '__main__':
    unittest.main()