from .post import post_create_user, post_login
import boto3
import os


def main(event, context):
    # create dynamodb resource
    DYNAMO_TABLE = os.environ['USERS_DYNAMODB_TABLE']
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DYNAMO_TABLE)

    response = None

    if event['httpMethod'] == 'POST':
        if event['action'] == 'create_user':
            response = post_create_user(event, table)
        elif event['action'] == 'login':
            response = post_login(event, table)

    return response if response else {
        'statusCode': 400,
        'body': 'Bad Request'
    }
