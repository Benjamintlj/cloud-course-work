from src.index import main
from unittest.mock import patch, MagicMock


def test_lambda_get(lambda_context, mock_env):
    with patch('boto3.resource') as mock_boto3_resources:
        # Mock the DynamoDB table
        mock_dynamodb_resource = MagicMock()
        mock_boto3_resources.return_value = mock_dynamodb_resource

        mock_dynamodb_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_dynamodb_table

        mock_dynamodb_table.get_item.return_value = {
            'Item': {
                'pk': '1',
                'name': 'test'
            }
        }

        # Mock the Lambda event
        lambda_event = {
            'httpMethod': 'GET',
            'pk': '1',
            'sk': 1
        }

        # Call the lambda function
        response = main(lambda_event, lambda_context)

        # Assert the DynamoDB call
        mock_dynamodb_table.get_item.assert_called_with(Key={
            'pk': '1',
            'sk': 1
        })

        # Define the expected response
        expected_response = {
            'statusCode': 200,
            'name': 'test'
        }

        # Assert the response
        assert response == expected_response
