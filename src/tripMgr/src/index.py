from .get import get_by_id, get_by_location, get_by_admin_id
from .post import create_trip
import boto3
import os


def main(event, context):
    # get DYNAMO_TABLE from environment variable
    DYNAMO_TABLE = os.environ['TRIPS_DYNAMODB_TABLE']
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DYNAMO_TABLE)

    http_method = event['httpMethod']
    action = event['action']

    response = None

    if http_method == 'GET':
        if action == 'get_trip_info_by_id':
            response = get_by_id(event, table)

        elif action == 'get_trip_info_by_location':
            response = get_by_location(event, table)

        elif action == 'get_trip_info_by_admin_id':
            response = get_by_admin_id(event, table)

    elif http_method == 'POST':
        response = create_trip(event, table)

    return response if response else {
        'statusCode': 400,
        'body': 'Bad Request'
    }

