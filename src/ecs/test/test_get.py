from fastapi.testclient import TestClient
from src.index import app
from unittest.mock import patch, MagicMock
import json
import os

client = TestClient(app)


def test_get(aws_credentials, mock_env):

    with patch('boto3.client') as mock_boto_client:
        mock_lambda_client = MagicMock()
        mock_boto_client.return_value = mock_lambda_client

        lambda_response = {
            'Payload': MagicMock()
        }
        # Return a byte string from `read()`
        mock_response_data = json.dumps({
            'statusCode': 200,
            'name': 'test'
        }).encode('utf-8')  # Encodes the string into bytes
        lambda_response['Payload'].read.return_value = mock_response_data
        mock_lambda_client.invoke.return_value = lambda_response

        response = client.get('/?pk=1&sk=1')

        assert response.json() == {
            'statusCode': 200,
            'body': {
                'name': 'test'
            }
        }

        mock_lambda_client.invoke.assert_called_once_with(
            FunctionName=os.getenv('TRIP_MGR_ARN'),
            InvocationType='RequestResponse',
            Payload=json.dumps({
                'httpMethod': 'GET',
                'pk': '1',
                'sk': 1
            })
        )
