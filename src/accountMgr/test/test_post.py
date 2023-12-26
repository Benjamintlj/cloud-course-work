import unittest
from unittest.mock import patch
from src.index import main
from botocore.exceptions import BotoCoreError


class TestPost(unittest.TestCase):

    @patch('boto3.resource')
    @patch('src.post.get_new_user_id')
    @patch('src.post.email_exists')
    def test_lambda_post_create_user(self, mock_email_exists, mock_get_new_user_id, mock_boto3_resource):
        user_id = 14231
        email = 'test@example.com'
        password = 'password123'

        mock_dynamodb_table = mock_boto3_resource.return_value.Table.return_value
        mock_get_new_user_id.return_value = user_id
        mock_email_exists.return_value = False
        mock_dynamodb_table.put_item.return_value = {
            'ResponseMetadata': {
                'HTTPStatusCode': 200,
            }
        }

        lambda_event = {
            'httpMethod': 'POST',
            'action': 'create_user',
            'body': {
                'email': email,
                'password': password
            },
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        mock_email_exists.assert_called_with(email, mock_dynamodb_table)
        mock_get_new_user_id.assert_called_with(mock_dynamodb_table)
        mock_dynamodb_table.put_item.assert_called_with(Item={
            'user_id': user_id,
            'email': email,
            'password': password,
            'awaiting_approval': [],
            'approved': []
        })

        expected_response = {
            'statusCode': 201,
            'body': 'User created successfully'
        }
        self.assertEqual(response, expected_response)

    @patch('boto3.resource')
    @patch('src.post.get_new_user_id')
    @patch('src.post.email_exists')
    def test_lambda_post_create_user_email_exists(self, mock_email_exists, mock_get_new_user_id, mock_boto3_resource):
        user_id = 14231
        email = 'test@example.com'
        password = 'password123'

        mock_dynamodb_table = mock_boto3_resource.return_value.Table.return_value
        mock_email_exists.return_value = True

        lambda_event = {
            'httpMethod': 'POST',
            'action': 'create_user',
            'body': {
                'email': email,
                'password': password
            },
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        mock_email_exists.assert_called_with(email, mock_dynamodb_table)
        mock_get_new_user_id.assert_not_called()
        mock_dynamodb_table.put_item.assert_not_called()

        expected_response = {
            'statusCode': 400,
            'body': 'Email already exists'
        }
        self.assertEqual(response, expected_response)

    @patch('boto3.resource')
    @patch('src.post.get_new_user_id')
    @patch('src.post.email_exists')
    def test_lambda_post_create_throws_BotoCoreError(self, mock_email_exists, mock_get_new_user_id, mock_boto3_resource):
        user_id = 14231
        email = 'test@example.com'
        password = 'password123'

        mock_dynamodb_table = mock_boto3_resource.return_value.Table.return_value
        mock_get_new_user_id.return_value = user_id
        mock_email_exists.return_value = False
        mock_dynamodb_table.put_item.side_effect = BotoCoreError()

        lambda_event = {
            'httpMethod': 'POST',
            'action': 'create_user',
            'body': {
                'email': email,
                'password': password
            },
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        mock_email_exists.assert_called_with(email, mock_dynamodb_table)
        mock_get_new_user_id.assert_called_with(mock_dynamodb_table)
        mock_dynamodb_table.put_item.assert_called_with(Item={
            'user_id': user_id,
            'email': email,
            'password': password,
            'awaiting_approval': [],
            'approved': []
        })

        expected_response = {
            'statusCode': 500,
            'body': 'BotoCoreError: An unspecified error occurred'
        }
        self.assertEqual(response, expected_response)

    @patch('boto3.resource')
    @patch('src.post.get_new_user_id')
    @patch('src.post.email_exists')
    def test_main_function_throws_exception(self, mock_email_exists, mock_get_new_user_id, mock_boto3_resource):
        email = 'test@example.com'
        password = 'password123'

        mock_dynamodb_table = mock_boto3_resource.return_value.Table.return_value
        mock_email_exists.return_value = False

        mock_get_new_user_id.side_effect = Exception('An error occurred')

        lambda_event = {
            'httpMethod': 'POST',
            'action': 'create_user',
            'body': {
                'email': email,
                'password': password
            },
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        mock_email_exists.assert_called_with(email, mock_dynamodb_table)
        mock_get_new_user_id.assert_called_with(mock_dynamodb_table)
        mock_dynamodb_table.put_item.assert_not_called()

        expected_response = {
            'statusCode': 500,
            'body': 'Exception: An error occurred'
        }

        self.assertEqual(response, expected_response)

    @patch('boto3.resource')
    @patch('src.post.get_email_item')
    def test_post_login(self, mock_get_email_item, mock_boto3_resource):
        user_id = 12848983912
        email = 'test@example.com'
        password = 'password123'

        mock_dynamodb_table = mock_boto3_resource.return_value.Table.return_value
        mock_get_email_item.return_value = {
            'statusCode': 200,
            'body': {
                'user_id': user_id,
                'email': email,
                'password': password
            }
        }

        lambda_event = {
            'httpMethod': 'POST',
            'action': 'login',
            'body': {
                'email': email,
                'password': password
            },
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        mock_get_email_item.assert_called_with(email, mock_dynamodb_table)

        expected_response = {
            'statusCode': 200,
            'body': {
                'user_id': user_id,
            }
        }
        self.assertEqual(response, expected_response)
    
    @patch('boto3.resource')
    @patch('src.post.get_email_item')
    def test_post_login_incorrect_password(self, mock_get_email_item, mock_boto3_resource):
        user_id = 12848983912
        email = 'test@example.com'
        password = 'password123'
        different_password = 'passWord123'

        mock_dynamodb_table = mock_boto3_resource.return_value.Table.return_value
        mock_get_email_item.return_value = {
            'statusCode': 200,
            'body': {
                'user_id': user_id,
                'email': email,
                'password': different_password
            }
        }

        lambda_event = {
            'httpMethod': 'POST',
            'action': 'login',
            'body': {
                'email': email,
                'password': password
            },
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        mock_get_email_item.assert_called_with(email, mock_dynamodb_table)

        expected_response = {
            'statusCode': 401,
            'Error': 'Incorrect password'
        }
        self.assertEqual(response, expected_response)

    @patch('boto3.resource')
    @patch('src.post.get_email_item')
    def test_post_login_account_not_found(self, mock_get_email_item, mock_boto3_resource):
        user_id = 12848983912
        email = 'test@example.com'
        password = 'password123'

        mock_dynamodb_table = mock_boto3_resource.return_value.Table.return_value
        mock_get_email_item.return_value = {
            'statusCode': 404,
            'Error': 'Account not found'
        }

        lambda_event = {
            'httpMethod': 'POST',
            'action': 'login',
            'body': {
                'email': email,
                'password': password
            },
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        mock_get_email_item.assert_called_with(email, mock_dynamodb_table)

        expected_response = {
            'statusCode': 404,
            'Error': 'Account not found'
        }
        
        self.assertEqual(response, expected_response)

    @patch('boto3.resource')
    @patch('src.post.get_email_item')
    def test_post_login_boto_core_error(self, mock_get_email_item, mock_boto3_resource):
        user_id = 12848983912
        email = 'test@example.com'
        password = 'password123'

        mock_dynamodb_table = mock_boto3_resource.return_value.Table.return_value
        mock_get_email_item.return_value = {
            'statusCode': 500,
            'Error': 'BotoCoreError An unspecified error occurred'
        }

        lambda_event = {
            'httpMethod': 'POST',
            'action': 'login',
            'body': {
                'email': email,
                'password': password
            },
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        mock_get_email_item.assert_called_with(email, mock_dynamodb_table)

        expected_response = {
            'statusCode': 500,
            'Error': 'BotoCoreError An unspecified error occurred'
        }

        self.assertEqual(response, expected_response)

