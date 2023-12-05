from .get import get
from .put import put
import boto3
import os


def main(event, context):
    # get DYNAMO_TABLE from environment variable
    DYNAMO_TABLE = os.environ['DYNAMO_TABLE']
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DYNAMO_TABLE)

    http_method = event['httpMethod']

    response = None

    if http_method == 'GET':
        response = get(event, table)
    elif http_method == 'PUT':
        response = put(event, table)
    return response if response else {
        'statusCode': 400,
        'body': 'Bad Request'
    }

