import unittest
from unittest.mock import patch, MagicMock
from src.index import main
from botocore.exceptions import BotoCoreError
from boto3.dynamodb.conditions import Key


class TestLambdaFunction(unittest.TestCase):
    @patch('boto3.resource')
    def test_get_trip_by_id(self, mock_boto3_resource):
        mock_dynamodb_resource = MagicMock()
        mock_boto3_resource.return_value = mock_dynamodb_resource

        mock_dynamodb_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_dynamodb_table

        trip_id = 123
        admin_id = 19823091
        start_date = 946684800  # 1st jan 2000
        end_date = 956684800  # other date
        location = 'London'
        title = 'the big trip'
        description = 'is is gonna be years!'

        mock_response = {
            'Item': {
                'trip_id': trip_id,
                'admin_id': admin_id,
                'start_date': start_date,
                'end_date': end_date,
                'location': location,
                'title': title,
                'description': description,
                'awaiting_approval': [],
                'approved': []
            }
        }
        mock_dynamodb_table.get_item.return_value = mock_response

        lambda_event = {
            'httpMethod': 'GET',
            'action': 'get_trip_info_by_id',
            'body': {
                'trip_id': trip_id
            }
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        mock_dynamodb_table.get_item.assert_called_once_with(Key={'trip_id': trip_id})

        expected_response = {
            'statusCode': 200,
            'body': mock_response['Item']
        }

        self.assertEqual(response, expected_response)

    @patch('boto3.resource')
    def test_get_trip_by_id_boto_core_error(self, mock_boto3_resource):
        mock_dynamodb_resource = MagicMock()
        mock_boto3_resource.return_value = mock_dynamodb_resource
        mock_dynamodb_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_dynamodb_table

        mock_dynamodb_table.get_item.side_effect = BotoCoreError()

        lambda_event = {
            'httpMethod': 'GET',
            'action': 'get_trip_info_by_id',
            'body': {
                'trip_id': 123
            }
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        expected_response = {
            'statusCode': 500,
            'details': 'BotoCoreError: An unspecified error occurred'
        }

        self.assertEqual(response, expected_response)

    @patch('boto3.resource')
    def test_get_trip_by_id_exception(self, mock_boto3_resource):
        mock_dynamodb_resource = MagicMock()
        mock_boto3_resource.return_value = mock_dynamodb_resource
        mock_dynamodb_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_dynamodb_table

        mock_dynamodb_table.get_item.side_effect = Exception("Test Error")

        lambda_event = {
            'httpMethod': 'GET',
            'action': 'get_trip_info_by_id',
            'body': {
                'trip_id': 123
            }
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        expected_response = {
            'statusCode': 500,
            'details': 'Error: Test Error'
        }

        self.assertEqual(response, expected_response)

    @patch('boto3.resource')
    def test_get_trip_by_location(self, mock_boto3_resource):
        mock_dynamodb_resource = MagicMock()
        mock_boto3_resource.return_value = mock_dynamodb_resource
        mock_dynamodb_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_dynamodb_table

        trip_id = 123
        admin_id = 19823091
        start_date = 946684800
        end_date = 956684800
        location = 'London'
        title = 'the big trip'
        description = 'is is gonna be years!'

        mock_response = {
            'Items': [{
                'trip_id': trip_id,
                'admin_id': admin_id,
                'start_date': start_date,
                'end_date': end_date,
                'location': location,
                'title': title,
                'description': description,
                'awaiting_approval': [],
                'approved': []
            }]
        }
        mock_dynamodb_table.query.return_value = mock_response

        lambda_event = {
            'httpMethod': 'GET',
            'action': 'get_trip_info_by_location',
            'body': {
                'location': location
            }
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        mock_dynamodb_table.query.assert_called_once_with(
            IndexName='location-index',
            KeyConditionExpression=Key('location').eq(location)
        )

        expected_response = {
            'statusCode': 200,
            'body': mock_response['Items']
        }

        self.assertEqual(response, expected_response)

    @patch('boto3.resource')
    def test_get_trip_by_location_boto_core_error(self, mock_boto3_resource):
        mock_dynamodb_resource = MagicMock()
        mock_boto3_resource.return_value = mock_dynamodb_resource
        mock_dynamodb_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_dynamodb_table

        mock_dynamodb_table.query.side_effect = BotoCoreError()

        lambda_event = {
            'httpMethod': 'GET',
            'action': 'get_trip_info_by_location',
            'body': {
                'location': 'London'
            }
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        expected_response = {
            'statusCode': 500,
            'details': 'BotoCoreError: An unspecified error occurred'
        }

        self.assertEqual(response, expected_response)

    @patch('boto3.resource')
    def test_get_trip_by_location_exception(self, mock_boto3_resource):
        mock_dynamodb_resource = MagicMock()
        mock_boto3_resource.return_value = mock_dynamodb_resource
        mock_dynamodb_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_dynamodb_table

        mock_dynamodb_table.query.side_effect = Exception("Test Error")

        lambda_event = {
            'httpMethod': 'GET',
            'action': 'get_trip_info_by_location',
            'body': {
                'location': 'London'
            }
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        expected_response = {
            'statusCode': 500,
            'details': 'Error: Test Error'
        }

        self.assertEqual(response, expected_response)

    @patch('boto3.resource')
    def test_get_trip_by_admin_id(self, mock_boto3_resource):
        mock_dynamodb_resource = MagicMock()
        mock_boto3_resource.return_value = mock_dynamodb_resource
        mock_dynamodb_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_dynamodb_table

        trip_id = 123
        admin_id = 19823091
        start_date = 946684800
        end_date = 956684800
        location = 'London'
        title = 'the big trip'
        description = 'is is gonna be years!'

        mock_response = {
            'Items': [{
                'trip_id': trip_id,
                'admin_id': admin_id,
                'start_date': start_date,
                'end_date': end_date,
                'location': location,
                'title': title,
                'description': description,
                'awaiting_approval': [],
                'approved': []
            }]
        }
        mock_dynamodb_table.query.return_value = mock_response

        lambda_event = {
            'httpMethod': 'GET',
            'action': 'get_trip_info_by_admin_id',
            'body': {
                'admin_id': admin_id
            }
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        mock_dynamodb_table.query.assert_called_once_with(
            IndexName='admin_id-index',
            KeyConditionExpression=Key('admin_id').eq(admin_id)
        )

        expected_response = {
            'statusCode': 200,
            'body': mock_response['Items']
        }

        self.assertEqual(response, expected_response)

    @patch('boto3.resource')
    def test_get_trip_by_admin_id_boto_core_error(self, mock_boto3_resource):
        mock_dynamodb_resource = MagicMock()
        mock_boto3_resource.return_value = mock_dynamodb_resource
        mock_dynamodb_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_dynamodb_table

        mock_dynamodb_table.query.side_effect = BotoCoreError()

        lambda_event = {
            'httpMethod': 'GET',
            'action': 'get_trip_info_by_admin_id',
            'body': {
                'admin_id': 19823091
            }
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        expected_response = {
            'statusCode': 500,
            'details': 'BotoCoreError: An unspecified error occurred'
        }

        self.assertEqual(response, expected_response)

    @patch('boto3.resource')
    def test_get_trip_by_admin_id_exception(self, mock_boto3_resource):
        mock_dynamodb_resource = MagicMock()
        mock_boto3_resource.return_value = mock_dynamodb_resource
        mock_dynamodb_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_dynamodb_table

        mock_dynamodb_table.query.side_effect = Exception("Test Error")

        lambda_event = {
            'httpMethod': 'GET',
            'action': 'get_trip_info_by_admin_id',
            'body': {
                'admin_id': 19823091
            }
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        expected_response = {
            'statusCode': 500,
            'details': 'Error: Test Error'
        }

        self.assertEqual(response, expected_response)
