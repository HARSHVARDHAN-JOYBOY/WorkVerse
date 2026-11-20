"""
WorkVerse - Test Suite
Verifies application imports, configuration validation, retry logic,
route resilience, and error handling.
"""

import unittest
from unittest.mock import patch, MagicMock
import pymysql
import os

from config import Config
from app import app, get_db_connection

class WorkVerseTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_config_validation_missing_variables(self):
        """Test that missing required DB variables are caught without exposing secrets"""
        with patch.object(Config, 'DB_HOST', None), \
             patch.object(Config, 'DB_USER', None), \
             patch.object(Config, 'DB_PASSWORD', None), \
             patch.object(Config, 'DB_NAME', None):
            is_valid, missing, msg = Config.validate_db_config()
            self.assertFalse(is_valid)
            self.assertIn('DB_HOST', missing[0])
            self.assertIn('DB_USER', missing[1])
            self.assertIn('DB_PASSWORD', missing[2])
            self.assertIn('DB_NAME', missing[3])

    def test_config_validation_complete(self):
        """Test that complete configuration validates cleanly"""
        with patch.object(Config, 'DB_HOST', 'mainline.proxy.rlwy.net'), \
             patch.object(Config, 'DB_USER', 'root'), \
             patch.object(Config, 'DB_PASSWORD', 'testpass'), \
             patch.object(Config, 'DB_NAME', 'railway'):
            is_valid, missing, msg = Config.validate_db_config()
            self.assertTrue(is_valid)
            self.assertEqual(len(missing), 0)

    def test_get_db_connection_missing_config_raises(self):
        """Test get_db_connection raises RuntimeError when config is missing"""
        with patch.object(Config, 'DB_HOST', None):
            with self.assertRaises(RuntimeError) as ctx:
                get_db_connection()
            self.assertIn("Missing required environment variables", str(ctx.exception))

    @patch('time.sleep', return_value=None)
    @patch('pymysql.connect')
    def test_get_db_connection_retries_transient_error(self, mock_connect, mock_sleep):
        """Test that get_db_connection retries on transient OperationalError (e.g. 2013 handshake lost)"""
        mock_conn = MagicMock()
        # Fail first 2 attempts with code 2013, succeed on 3rd attempt
        mock_connect.side_effect = [
            pymysql.err.OperationalError(2013, 'Lost connection to MySQL server during query'),
            pymysql.err.OperationalError(2013, 'Lost connection to MySQL server during query'),
            mock_conn
        ]

        with patch.dict(app.config, {
            'DB_HOST': 'mainline.proxy.rlwy.net',
            'DB_PORT': 43679,
            'DB_USER': 'root',
            'DB_PASSWORD': 'dummy_password',
            'DB_NAME': 'railway',
            'DB_MAX_RETRIES': 3,
            'DB_RETRY_BACKOFF': 0.01
        }):
            conn = get_db_connection()
            self.assertEqual(conn, mock_conn)
            self.assertEqual(mock_connect.call_count, 3)

    @patch('pymysql.connect')
    def test_get_db_connection_fails_fast_on_auth_error(self, mock_connect):
        """Test that get_db_connection does NOT retry fatal auth error 1045"""
        mock_connect.side_effect = pymysql.err.OperationalError(1045, "Access denied for user 'root'@'host'")

        with patch.dict(app.config, {
            'DB_HOST': 'mainline.proxy.rlwy.net',
            'DB_PORT': 43679,
            'DB_USER': 'root',
            'DB_PASSWORD': 'wrong_password',
            'DB_NAME': 'railway',
            'DB_MAX_RETRIES': 5
        }):
            with self.assertRaises(pymysql.err.OperationalError) as ctx:
                get_db_connection()
            self.assertEqual(ctx.exception.args[0], 1045)
            # Must fail on the very first attempt without looping 5 times
            self.assertEqual(mock_connect.call_count, 1)

    @patch('app.get_db_connection')
    def test_home_route_with_simulations(self, mock_get_db):
        """Test home route successfully renders with simulations"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'title': 'Data Analyst', 'description': 'Analyze data', 'created_at': '2026-01-01'}
        ]
        mock_get_db.return_value = mock_conn

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Data Analyst', response.data)
        mock_conn.close.assert_called_once()

    @patch('app.get_db_connection')
    def test_home_route_graceful_degradation_on_db_error(self, mock_get_db):
        """Test home route degrades gracefully if database is initializing / sleeping"""
        mock_get_db.side_effect = pymysql.err.OperationalError(2013, 'Lost connection to MySQL server')

        response = self.client.get('/')
        # Should return 200 with flash notice rather than unhandled 500 error
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Master Real-World Job Skills', response.data)

    @patch('app.get_db_connection')
    def test_health_route_connected(self, mock_get_db):
        """Test health endpoint reports healthy when database is reachable"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'ping': 1}
        mock_get_db.return_value = mock_conn

        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'healthy')
        self.assertEqual(json_data['database'], 'connected')

    @patch('app.get_db_connection')
    def test_health_route_disconnected(self, mock_get_db):
        """Test health endpoint reports degraded 503 when database is unreachable"""
        mock_get_db.side_effect = pymysql.err.OperationalError(2013, 'Lost connection')

        response = self.client.get('/health')
        self.assertEqual(response.status_code, 503)
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'degraded')
        self.assertEqual(json_data['database'], 'disconnected')

    def test_404_handler(self):
        """Test 404 error handler"""
        response = self.client.get('/nonexistent-page-url')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
