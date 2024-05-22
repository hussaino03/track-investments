import unittest
from unittest.mock import patch
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.db import create_user, add_investment_to_user, get_user_investments, save_report_to_db, get_report_from_db

class TestFirebaseFunctions(unittest.TestCase):

    @patch('db.db.auth.create_user')
    def test_create_user_success(self, mock_create_user):
        mock_create_user.return_value = {'uid': 'test_uid'}
        result = create_user('test@example.com', 'password123')
        self.assertEqual(result, 'test_uid')

    @patch('db.db.auth.create_user')
    def test_create_user_failure(self, mock_create_user):
        mock_create_user.side_effect = Exception('AuthError')
        result = create_user('test@example.com', 'password123')
        self.assertIsNone(result)

    @patch('db.db.db.reference')
    def test_add_investment_to_user(self, mock_db_reference):
        mock_push = mock_db_reference.return_value.push
        add_investment_to_user('test_uid', {'investment': 'details'})
        mock_push.assert_called_once_with({'investment': 'details'})

    @patch('db.db.db.reference')
    def test_get_user_investments(self, mock_db_reference):
        mock_get = mock_db_reference.return_value.get
        mock_get.return_value = {'investment1': 'details1', 'investment2': 'details2'}
        result = get_user_investments('test_uid')
        self.assertEqual(result, {'investment1': 'details1', 'investment2': 'details2'})

    @patch('db.db.db.reference')
    def test_save_report_to_db(self, mock_db_reference):
        mock_set = mock_db_reference.return_value.set
        save_report_to_db('test_uid', {'report': 'details'})
        mock_set.assert_called_once_with({'report': 'details'})

    @patch('db.db.db.reference')
    def test_get_report_from_db(self, mock_db_reference):
        mock_get = mock_db_reference.return_value.get
        mock_get.return_value = {'report': 'details'}
        result = get_report_from_db('test_uid')
        self.assertEqual(result, {'report': 'details'})

if __name__ == '__main__':
    unittest.main()
