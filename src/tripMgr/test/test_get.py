# test_lambda_function.py

from src.index import main


def test_lambda_function(sqs, lambda_context):
    # Mock the Lambda event
    lambda_event = {
        'Records': [
            {
                'body': 'Message from SQS',
                'attributes': {
                    'ApproximateReceiveCount': '1',
                    'SentTimestamp': '1234567890',
                    'SenderId': 'test',
                    'ApproximateFirstReceiveTimestamp': '1234567890'
                },
                'messageId': 'test-message-id',
                'receiptHandle': 'test-receipt-handle',
            }
        ]
    }

    # Call the lambda function
    response = main(lambda_event, lambda_context)

    # Assert the response
    assert response == {
        'statusCode': 200,
        'body': 'Hello World!'
    }
