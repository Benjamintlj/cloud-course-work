import boto3
import os
import json
from botocore.exceptions import ClientError
import datetime

dynamodb = boto3.resource('dynamodb')


def main(event, context):
    """
    Relays messages from sqs to dynamoDB
    """
    table_name = os.environ['FAILED_REQUESTS_DYNAMODB_TABLE']
    table = dynamodb.Table(table_name)

    response = {
        'statusCode': 200,
        'body': json.dumps('Data successfully processed.')
    }

    for record in event['Records']:
        message_body = json.loads(record['body'])

        status_code = message_body['status_code']
        description = message_body['description']
        request = message_body['request']

        request_id = int(datetime.datetime.now().timestamp() * 1000)

        try:
            response = table.put_item(
                Item={
                    'request_id': request_id,
                    'status_code': status_code,
                    'description': description,
                    'request': request
                }
            )
        except ClientError as ignore:
            response = {
                'statusCode': 500,
                'body': json.dumps('An error occurred during processing.')
            }

    return response
