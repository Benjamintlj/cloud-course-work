import unittest
from botocore.exceptions import BotoCoreError, ClientError
from src.index import main
from unittest.mock import patch, MagicMock


class TestLambdaFunction(unittest.TestCase):
    @patch('src.post.create_new_id')
    @patch('boto3.resource')
    def test_create_trip(self, mock_boto3_resources, mock_new_id):
        trip_id = 23423412341
        mock_new_id.return_value = trip_id

        # Mock the DynamoDB table
        mock_dynamodb_resource = MagicMock()
        mock_boto3_resources.return_value = mock_dynamodb_resource

        mock_dynamodb_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_dynamodb_table

        # Mock the Lambda event
        admin_id = 19823091
        start_date = 946684800  # 1st jan 2000
        end_date = 956684800  # other date
        location = 'London'
        title = 'the big trip'
        description = 'is is gonna be years!'

        lambda_event = {
            'httpMethod': 'POST',
            'action': 'create_trip',
            'body': {
                'admin_id': admin_id,
                'start_date': start_date,
                'end_date': end_date,
                'location': location,
                'title': title,
                'description': description
            }
        }

        # Mock the lambda context
        lambda_context = {}

        # Call the lambda function
        response = main(lambda_event, lambda_context)

        print(response)
        calls = mock_dynamodb_table.put_item.call_args_list
        print("Calls to put_item:", calls)

        # mock getting uid
        mock_new_id.assert_called_once_with(
            mock_dynamodb_table
        )

        # Mock dynamodb
        mock_dynamodb_table.put_item.assert_called_with(Item={
            'trip_id': trip_id,
            'admin_id': admin_id,
            'start_date': start_date,
            'end_date': end_date,
            'location': location,
            'title': title,
            'description': description,
            'awaiting_approval': [],
            'approved': []
        })

        # Define the expected response
        expected_response = {
            'statusCode': 200
        }

        # Assert the response
        assert response == expected_response

    @patch('src.post.create_new_id')
    @patch('boto3.resource')
    def test_create_trip_boto_core_error(self, mock_boto3_resources, mock_new_id):
        mock_new_id.return_value = 23423412341

        mock_dynamodb_resource = MagicMock()
        mock_boto3_resources.return_value = mock_dynamodb_resource

        mock_dynamodb_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_dynamodb_table

        mock_dynamodb_table.put_item.side_effect = BotoCoreError()

        lambda_event = {
            'httpMethod': 'POST',
            'action': 'create_trip',
            'body': {
                'admin_id': 19823091,
                'start_date': 946684800,
                'end_date': 956684800,
                'location': 'London',
                'title': 'the big trip',
                'description': 'is is gonna be years!'
            }
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('BotoCoreError', response['details'])

    @patch('src.post.create_new_id')
    @patch('boto3.resource')
    def test_create_trip_exception(self, mock_boto3_resources, mock_new_id):
        mock_new_id.return_value = 23423412341

        mock_dynamodb_resource = MagicMock()
        mock_boto3_resources.return_value = mock_dynamodb_resource

        mock_dynamodb_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_dynamodb_table

        mock_dynamodb_table.put_item.side_effect = Exception("error")

        lambda_event = {
            'httpMethod': 'POST',
            'action': 'create_trip',
            'body': {
                'admin_id': 19823091,
                'start_date': 946684800,
                'end_date': 956684800,
                'location': 'London',
                'title': 'the big trip',
                'description': 'is is gonna be years!'
            }
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error: error', response['details'])

    ######################################
    #  user wants to go on trip
    @patch('boto3.client')
    def test_user_wants_to_go_on_trip(self, mock_boto3_client):
        mock_dynamodb_client = MagicMock()
        mock_boto3_client.return_value = mock_dynamodb_client

        user_id = 1223423
        trip_id = 4523426

        mock_transaction_response = {}
        mock_dynamodb_client.transact_write_items.return_value = mock_transaction_response

        lambda_event = {
            'httpMethod': 'POST',
            'action': 'user_wants_to_go_on_trip',
            'body': {
                'user_id': user_id,
                'trip_id': trip_id,
            }
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        mock_dynamodb_client.transact_write_items.assert_called()

        expected_response = {
            'statusCode': 200
        }
        self.assertEqual(response, expected_response)

    @patch('boto3.client')
    def test_user_wants_to_go_on_trip_client_error(self, mock_boto3_client):
        mock_dynamodb_client = MagicMock()
        mock_boto3_client.return_value = mock_dynamodb_client
        error_message = "An error occurred (ValidationException) when calling the TransactWriteItems operation: Unknown"
        mock_dynamodb_client.transact_write_items.side_effect = ClientError({
            'Error': {
                'Code': 'ValidationException',
                'Message': error_message
            }
        }, 'TransactWriteItems')

        lambda_event = {
            'httpMethod': 'POST',
            'action': 'user_wants_to_go_on_trip',
            'body': {
                'user_id': 1223423,
                'trip_id': 4523426,
            }
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        self.assertEqual(response['statusCode'], 400)

    @patch('boto3.client')
    def test_user_wants_to_go_on_trip_exception(self, mock_boto3_client):
        mock_dynamodb_client = MagicMock()
        mock_boto3_client.return_value = mock_dynamodb_client
        mock_dynamodb_client.transact_write_items.side_effect = Exception("error")

        lambda_event = {
            'httpMethod': 'POST',
            'action': 'user_wants_to_go_on_trip',
            'body': {
                'user_id': 1223423,
                'trip_id': 4523426,
            }
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        expected_response = {'statusCode': 500, 'details': 'Error: error'}
        self.assertEqual(response, expected_response)

    ######################################
    #  user wants to go on trip
    @patch('src.post.remove_element_from_list')
    @patch('boto3.client')
    def test_user_approval_request_approved(self, mock_boto3_client, mock_remove_element):
        mock_dynamodb_client = MagicMock()
        mock_boto3_client.return_value = mock_dynamodb_client

        user_id = 1223423
        trip_id = 4523426

        lambda_event = {
            'httpMethod': 'POST',
            'action': 'user_approval',
            'body': {
                'user_id': user_id,
                'trip_id': trip_id,
                'is_approved': True
            }
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        print(mock_remove_element.call_args_list)

        mock_remove_element.assert_any_call('trip_table', False, str(trip_id), str(user_id), False)
        mock_remove_element.assert_any_call('user_table', True, str(user_id), str(trip_id), False)
        mock_dynamodb_client.transact_write_items.assert_called()

        # Assert response
        expected_response = {'statusCode': 200}
        self.assertEqual(response, expected_response)

    ######################################
    # user doesn't want to go on the trip
    @patch('src.post.remove_element_from_list')
    @patch('boto3.client')
    def test_user_no_longer_wants_to_attend(self, mock_boto3_client, mock_remove_element):
        mock_dynamodb_client = MagicMock()
        mock_boto3_client.return_value = mock_dynamodb_client

        user_id = 1234567
        trip_id = 7654321
        lambda_event = {
            'httpMethod': 'POST',
            'action': 'user_no_longer_wants_to_attend',
            'body': {
                'user_id': user_id,
                'trip_id': trip_id
            }
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        mock_remove_element.assert_any_call('trip_table', False, str(trip_id), str(user_id), False)
        mock_remove_element.assert_any_call('user_table', True, str(user_id), str(trip_id), False)
        mock_remove_element.assert_any_call('trip_table', False, str(trip_id), str(user_id), True)
        mock_remove_element.assert_any_call('user_table', True, str(user_id), str(trip_id), True)

        # Assert response
        expected_response = {'statusCode': 200}
        self.assertEqual(response, expected_response)
