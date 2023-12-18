import unittest
from unittest.mock import patch, MagicMock
from src.index import main
from botocore.exceptions import ClientError


class TestDeleteTrip(unittest.TestCase):
    @patch('src.delete.remove_element_from_list')
    @patch('boto3.resource')
    def test_delete_trip(self, mock_boto3_resource, mock_remove_element):
        mock_dynamodb_resource = MagicMock()
        mock_boto3_resource.return_value = mock_dynamodb_resource

        mock_dynamodb_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_dynamodb_table

        trip_id = 17028438789525
        mock_dynamodb_table.get_item.return_value = {
            'Item': {
                'awaiting_approval': [1, 2],
                'approved': [3]
            }
        }

        lambda_event = {
            'httpMethod': 'DELETE',
            'action': 'delete_trip',
            'body': {
                'trip_id': trip_id
            }
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        mock_dynamodb_table.delete_item.assert_called_once_with(Key={'trip_id': trip_id})
        mock_remove_element.assert_any_call('user_table', True, 1, trip_id, False)
        mock_remove_element.assert_any_call('user_table', True, 2, trip_id, False)
        mock_remove_element.assert_any_call('user_table', True, 3, trip_id, True)

        expected_response = {
            'statusCode': 200
        }
        self.assertEqual(response, expected_response)

    @patch('src.delete.remove_element_from_list')
    @patch('boto3.resource')
    def test_delete_trip_client_error(self, mock_boto3_resource, mock_remove_element):
        mock_dynamodb_resource = MagicMock()
        mock_boto3_resource.return_value = mock_dynamodb_resource
        mock_dynamodb_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_dynamodb_table
        mock_dynamodb_table.delete_item.side_effect = ClientError({
            'Error': {}
        }, 'DeleteItem')

        trip_id = 17028438789525
        lambda_event = {
            'httpMethod': 'DELETE',
            'action': 'delete_trip',
            'body': {
                'trip_id': trip_id
            }
        }

        lambda_context = {}

        response = main(lambda_event, lambda_context)

        self.assertEqual(response['statusCode'], 400)
