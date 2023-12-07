from .post import post_create_user
import boto3
import os


def main(event, context):
    # create dynamodb resource
    DYNAMO_TABLE = os.environ['DYNAMO_TABLE']
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DYNAMO_TABLE)

    http_method = event['httpMethod']

    response = None

    if http_method == 'POST':
        response = post_create_user(event, table)

    return response if response else {
        'statusCode': 400,
        'body': 'Bad Request'
    }
