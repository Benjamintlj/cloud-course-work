import unittest
from unittest.mock import patch, MagicMock
from src.utils import email_exists, user_id_exists, get_new_user_id, get_email_item
from src.column_names import __email_column__, __password_column__, __user_id_column__, __email_index__
from boto3.dynamodb.conditions import Key
from botocore.exceptions import BotoCoreError


class TestUtils(unittest.TestCase):

    @patch('boto3.resource')
    def test_email_exists_when_not_found(self, mock_boto3_resource):
        # returns no item key
        mock_table = mock_boto3_resource.return_value.Table
        mock_table.query.return_value = {
            'Items': []
        }

        email = 'email@example.com'

        response = email_exists(email, mock_table)

        mock_table.query.assert_called_once_with(
            IndexName=__email_index__,
            KeyConditionExpression=Key(__email_column__).eq(email)
        )

        assert response is False

    @patch('boto3.resource')
    def test_email_exists(self, mock_boto3_resource):
        # returns no item key
        mock_table = mock_boto3_resource.return_value.Table
        mock_table.query.return_value = {
            'Items': [{
                'thing': 'thing'
            }]
        }

        email = 'email@example.com'

        response = email_exists(email, mock_table)

        mock_table.query.assert_called_once_with(
            IndexName=__email_index__,
            KeyConditionExpression=Key(__email_column__).eq(email)
        )

        assert response is True

    # TODO: email and password should be in vars
    @patch('boto3.resource')
    def test_get_email_item(self, mock_boto3_resource):
        # returns no item key
        mock_table = mock_boto3_resource.return_value.Table
        mock_table.query.return_value = {
            'Items': [{
                __user_id_column__: 12848983912,
                __email_column__: 'example@email.com',
                __password_column__: 'password123!'
            }]
        }

        email = 'example@email.com'

        response = get_email_item(email, mock_table)

        mock_table.query.assert_called_once_with(
            IndexName=__email_index__,
            KeyConditionExpression=Key(__email_column__).eq(email)
        )

        expected_response = {
            'statusCode': 200,
            'body': {
                __user_id_column__: 12848983912,
                __email_column__: 'example@email.com',
                __password_column__: 'password123!'
            }
        }

        assert response == expected_response

    @patch('boto3.resource')
    def test_get_email_item_no_item_exists(self, mock_boto3_resource):
        # returns no item key
        mock_table = mock_boto3_resource.return_value.Table
        mock_table.query.return_value = {
            'Items': []
        }

        email = 'example@email.com'

        response = get_email_item(email, mock_table)

        mock_table.query.assert_called_once_with(
            IndexName=__email_index__,
            KeyConditionExpression=Key(__email_column__).eq(email)
        )

        expected_response = {
            'statusCode': 404,
            'Error': 'Account not found'
        }

        assert response == expected_response

    @patch('boto3.resource')
    def test_get_email_item_boto_core_error(self, mock_boto3_resource):
        mock_table = mock_boto3_resource.return_value.Table
        mock_table.query.side_effect = BotoCoreError

        email = 'example@email.com'

        response = get_email_item(email, mock_table)

        mock_table.query.assert_called_once_with(
            IndexName=__email_index__,
            KeyConditionExpression=Key(__email_column__).eq(email)
        )

        expected_response = {
            'statusCode': 500,
            'Error': 'BotoCoreError An unspecified error occurred'
        }

        assert response == expected_response

    @patch('boto3.resource')
    def test_email_exists_throw_exception(self, mock_boto3_resource):
        # returns no item key
        mock_table = mock_boto3_resource.return_value.Table
        mock_table.query.side_effect = BotoCoreError()

        email = 'email@example.com'

        response = email_exists(email, mock_table)

        mock_table.query.assert_called_once_with(
            IndexName=__email_index__,
            KeyConditionExpression=Key(__email_column__).eq(email)
        )

        assert response is True

    @patch('boto3.resource')
    def test_user_id_does_not_exist(self, mock_boto3_resource):
        user_id = 123

        # Item is not in get_item
        mock_table = mock_boto3_resource.return_value.Table
        mock_table.get_item.return_value = {}

        response = user_id_exists(user_id, mock_table)

        mock_table.get_item.assert_called_once_with(
            Key={
                __user_id_column__: user_id,
            }
        )

        assert response is False

    @patch('boto3.resource')
    def test_user_id_exists(self, mock_boto3_resource):
        user_id = 123

        # Item is not in get_item
        mock_table = mock_boto3_resource.return_value.Table
        mock_table.get_item.return_value = {
            'Item': {
                'thing': 'thing'
            }
        }

        response = user_id_exists(user_id, mock_table)

        mock_table.get_item.assert_called_once_with(
            Key={
                __user_id_column__: user_id,
            }
        )

        assert response is True

    @patch('boto3.resource')
    def test_user_id_does_not_exist(self, mock_boto3_resource):
        user_id = 123

        # Item is not in get_item
        mock_table = mock_boto3_resource.return_value.Table
        mock_table.get_item.side_effect = BotoCoreError()

        response = user_id_exists(user_id, mock_table)

        mock_table.get_item.assert_called_once_with(
            Key={
                __user_id_column__: user_id,
            }
        )

        assert response is True

    @patch('boto3.resource')
    @patch('src.utils.user_id_exists')
    @patch('requests.get')
    def test_get_new_user_id(self, mock_requests_get, mock_user_id_exists, mock_boto3_resource):
        random_min = 0
        random_max = 100000000000
        random_number = 2138912342
        url = f'https://csrng.net/csrng/csrng.php?min={random_min}&max={random_max}'

        mock_table = mock_boto3_resource.return_value.Table
        mock_user_id_exists.return_value = False
        mock_requests_get_response = mock_requests_get.return_value
        mock_requests_get_response.json.return_value = [{
            'status': 'success',
            'min': random_min,
            'max': random_max,
            'random': random_number
        }]

        response = get_new_user_id(mock_table)

        mock_user_id_exists.assert_called_once_with(
            random_number,
            mock_table
        )
        mock_requests_get.assert_called_once_with(url)
        mock_requests_get_response.called_once_with()

        assert response is random_number

    @patch('boto3.resource')
    @patch('src.utils.user_id_exists')
    @patch('requests.get')
    def test_get_new_user_id_multiple_times(self, mock_requests_get, mock_user_id_exists, mock_boto3_resource):
        random_min = 0
        random_max = 100000000000
        first_random_number = 2138912342
        second_random_number = 9876543210
        url = f'https://csrng.net/csrng/csrng.php?min={random_min}&max={random_max}'

        mock_table = mock_boto3_resource.return_value.Table
        mock_user_id_exists.side_effect = [True, False]

        first_response = MagicMock()
        first_response.json.return_value = [{
            'status': 'success',
            'min': random_min,
            'max': random_max,
            'random': first_random_number
        }]

        second_response = MagicMock()
        second_response.json.return_value = [{
            'status': 'success',
            'min': random_min,
            'max': random_max,
            'random': second_random_number
        }]

        mock_requests_get.side_effect = [first_response, second_response]

        response = get_new_user_id(mock_table)

        calls = [unittest.mock.call(first_random_number, mock_table),
                 unittest.mock.call(second_random_number, mock_table)]
        mock_user_id_exists.assert_has_calls(calls, any_order=True)

        assert mock_requests_get.call_count is 2
        assert response is second_random_number

    @patch('boto3.resource')
    @patch('src.utils.user_id_exists')
    @patch('requests.get')
    def test_get_new_user_id_error_on_non_success_status(self, mock_requests_get, mock_user_id_exists, mock_boto3_resource):
        random_min = 0
        random_max = 100000000000
        url = f'https://csrng.net/csrng/csrng.php?min={random_min}&max={random_max}'

        mock_table = mock_boto3_resource.return_value.Table
        mock_user_id_exists.return_value = False

        mock_requests_get_response = MagicMock()
        mock_requests_get_response.json.return_value = [{
            'status': 'error',
            'errorMessage': 'Error processing API response: API response status is not success'
        }]
        mock_requests_get.return_value = mock_requests_get_response

        with self.assertRaises(Exception) as context:
            get_new_user_id(mock_table)

        # Optionally, check the message of the exception
        self.assertIn('Error processing API response: API response status is not success', str(context.exception))

        # Ensure the API was called
        mock_requests_get.assert_called_once_with(url)

    @patch('boto3.resource')
    @patch('src.utils.user_id_exists')
    @patch('requests.get')
    def test_get_new_user_id_error_on_connection_failure(self, mock_requests_get, mock_user_id_exists, mock_boto3_resource):
        random_min = 0
        random_max = 100000000000
        url = f'https://csrng.net/csrng/csrng.php?min={random_min}&max={random_max}'

        mock_table = mock_boto3_resource.return_value.Table
        mock_user_id_exists.return_value = False

        mock_requests_get.side_effect = ConnectionError('Failed to establish a new connection')

        with self.assertRaises(ConnectionError):
            get_new_user_id(mock_table)

        mock_requests_get.assert_called_once_with(url)

    @patch('boto3.resource')
    @patch('src.utils.user_id_exists')
    @patch('requests.get')
    def test_get_new_user_id_error_on_invalid_json(self, mock_requests_get, mock_user_id_exists, mock_boto3_resource):
        random_min = 0
        random_max = 100000000000
        url = f'https://csrng.net/csrng/csrng.php?min={random_min}&max={random_max}'

        mock_table = mock_boto3_resource.return_value.Table
        mock_user_id_exists.return_value = False

        # Invalid JSON response
        mock_requests_get_response = MagicMock()
        mock_requests_get_response.json.side_effect = ValueError('No JSON object could be decoded')
        mock_requests_get.return_value = mock_requests_get_response

        with self.assertRaises(ValueError):
            get_new_user_id(mock_table)

        mock_requests_get.assert_called_once_with(url)
