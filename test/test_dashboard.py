import unittest
import sqlite3
import pandas as pd
import os
import tempfile
import sys
from unittest.mock import patch, MagicMock

# Add the src directory to the path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dashboard import (
    get_db_connection,
    get_table_names,
    get_table_data,
    get_table_info,
    get_table_count
)

class TestDashboard(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary database for testing
        self.test_db_fd, self.test_db_path = tempfile.mkstemp()
        
        # Create test database with sample data
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Create test tables
        cursor.execute('''
            CREATE TABLE interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_query TEXT,
                bot_response TEXT,
                match_score REAL,
                feedback INTEGER,
                session_id TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE escalations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_query TEXT,
                suggested_answer TEXT
            )
        ''')
        
        # Insert sample data
        cursor.execute('''
            INSERT INTO interactions (user_query, bot_response, match_score, feedback, session_id)
            VALUES ('What are the fees?', 'The fees are...', 0.85, 1, 'session1')
        ''')
        
        cursor.execute('''
            INSERT INTO interactions (user_query, bot_response, match_score, feedback, session_id)
            VALUES ('How to register?', 'To register...', 0.92, 1, 'session2')
        ''')
        
        cursor.execute('''
            INSERT INTO escalations (user_query, suggested_answer)
            VALUES ('Complex question', 'This needs human review')
        ''')
        
        conn.commit()
        conn.close()
    
    def tearDown(self):
        """Clean up after each test method."""
        os.close(self.test_db_fd)
        os.unlink(self.test_db_path)
    
    @patch('dashboard.DB_PATH')
    def test_get_db_connection(self, mock_db_path):
        """Test database connection function."""
        mock_db_path.__str__ = lambda x: self.test_db_path
        mock_db_path.__fspath__ = lambda x: self.test_db_path
        
        with patch('dashboard.sqlite3.connect') as mock_connect:
            mock_connect.return_value = MagicMock()
            
            conn = get_db_connection()
            
            mock_connect.assert_called_once()
            self.assertIsNotNone(conn)
    
    @patch('dashboard.DB_PATH')
    def test_get_table_names(self, mock_db_path):
        """Test getting table names from database."""
        mock_db_path.__str__ = lambda x: self.test_db_path
        mock_db_path.__fspath__ = lambda x: self.test_db_path
        
        with patch('dashboard.get_db_connection') as mock_get_conn:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchall.return_value = [('interactions',), ('escalations',)]
            mock_get_conn.return_value = mock_conn
            
            tables = get_table_names()
            
            self.assertEqual(tables, ['interactions', 'escalations'])
            mock_cursor.execute.assert_called_once_with("SELECT name FROM sqlite_master WHERE type='table';")
            mock_conn.close.assert_called_once()
    
    @patch('dashboard.DB_PATH')
    def test_get_table_data(self, mock_db_path):
        """Test getting data from a specific table."""
        mock_db_path.__str__ = lambda x: self.test_db_path
        mock_db_path.__fspath__ = lambda x: self.test_db_path
        
        with patch('dashboard.get_db_connection') as mock_get_conn:
            mock_conn = MagicMock()
            mock_get_conn.return_value = mock_conn
            
            with patch('dashboard.pd.read_sql_query') as mock_read_sql:
                mock_df = pd.DataFrame({'id': [1, 2], 'user_query': ['test1', 'test2']})
                mock_read_sql.return_value = mock_df
                
                result = get_table_data('interactions')
                
                mock_read_sql.assert_called_once_with("SELECT * FROM interactions", mock_conn)
                mock_conn.close.assert_called_once()
                pd.testing.assert_frame_equal(result, mock_df)
    
    @patch('dashboard.DB_PATH')
    def test_get_table_info(self, mock_db_path):
        """Test getting table schema information."""
        mock_db_path.__str__ = lambda x: self.test_db_path
        mock_db_path.__fspath__ = lambda x: self.test_db_path
        
        with patch('dashboard.get_db_connection') as mock_get_conn:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchall.return_value = [
                (0, 'id', 'INTEGER', 0, None, 1),
                (1, 'user_query', 'TEXT', 0, None, 0)
            ]
            mock_get_conn.return_value = mock_conn
            
            result = get_table_info('interactions')
            
            expected = [
                (0, 'id', 'INTEGER', 0, None, 1),
                (1, 'user_query', 'TEXT', 0, None, 0)
            ]
            
            self.assertEqual(result, expected)
            mock_cursor.execute.assert_called_once_with("PRAGMA table_info(interactions)")
            mock_conn.close.assert_called_once()
    
    @patch('dashboard.DB_PATH')
    def test_get_table_count(self, mock_db_path):
        """Test getting row count for a table."""
        mock_db_path.__str__ = lambda x: self.test_db_path
        mock_db_path.__fspath__ = lambda x: self.test_db_path
        
        with patch('dashboard.get_db_connection') as mock_get_conn:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = (5,)
            mock_get_conn.return_value = mock_conn
            
            count = get_table_count('interactions')
            
            self.assertEqual(count, 5)
            mock_cursor.execute.assert_called_once_with("SELECT COUNT(*) FROM interactions")
            mock_conn.close.assert_called_once()
    
    def test_get_table_names_with_real_db(self):
        """Test get_table_names with a real database connection."""
        # Use the test database directly
        with patch('dashboard.DB_PATH', self.test_db_path):
            tables = get_table_names()
            
            self.assertIn('interactions', tables)
            self.assertIn('escalations', tables)
            # Check that we have at least our expected tables (SQLite may create additional system tables)
            self.assertGreaterEqual(len(tables), 2)
    
    def test_get_table_data_with_real_db(self):
        """Test get_table_data with a real database connection."""
        with patch('dashboard.DB_PATH', self.test_db_path):
            df = get_table_data('interactions')
            
            self.assertIsInstance(df, pd.DataFrame)
            self.assertEqual(len(df), 2)
            self.assertIn('user_query', df.columns)
            self.assertIn('bot_response', df.columns)
            self.assertEqual(df.iloc[0]['user_query'], 'What are the fees?')
    
    def test_get_table_count_with_real_db(self):
        """Test get_table_count with a real database connection."""
        with patch('dashboard.DB_PATH', self.test_db_path):
            count = get_table_count('interactions')
            self.assertEqual(count, 2)
            
            count = get_table_count('escalations')
            self.assertEqual(count, 1)
    
    def test_get_table_info_with_real_db(self):
        """Test get_table_info with a real database connection."""
        with patch('dashboard.DB_PATH', self.test_db_path):
            info = get_table_info('interactions')
            
            self.assertIsInstance(info, list)
            self.assertTrue(len(info) > 0)
            
            # Check if expected columns exist
            column_names = [col[1] for col in info]
            self.assertIn('id', column_names)
            self.assertIn('user_query', column_names)
            self.assertIn('bot_response', column_names)
    
    @patch('dashboard.get_db_connection')
    def test_database_connection_error(self, mock_get_conn):
        """Test handling of database connection errors."""
        mock_get_conn.side_effect = sqlite3.Error("Database connection failed")
        
        with self.assertRaises(sqlite3.Error):
            get_table_names()
    
    @patch('dashboard.get_db_connection')
    def test_invalid_table_name(self, mock_get_conn):
        """Test handling of invalid table names."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.OperationalError("no such table: invalid_table")
        mock_get_conn.return_value = mock_conn
        
        with self.assertRaises(sqlite3.OperationalError):
            get_table_count('invalid_table')

if __name__ == '__main__':
    unittest.main()