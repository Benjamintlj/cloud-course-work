import unittest
from botocore.exceptions import BotoCoreError
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
            'description': description
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