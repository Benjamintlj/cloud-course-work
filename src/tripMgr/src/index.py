from .get import get_by_id, get_by_location, get_by_admin_id
from .post import create_trip, user_wants_to_go_on_trip, user_approval_request, user_no_longer_wants_to_attend
import boto3
import os


def main(event, context):
    # get DYNAMO_TABLE from environment variable
    dynamodb_resource = boto3.resource('dynamodb')
    TRIPS_DYNAMO_TABLE = os.environ['TRIPS_DYNAMODB_TABLE']
    trips_table = dynamodb_resource.Table(TRIPS_DYNAMO_TABLE)
    USERS_DYNAMODB_TABLE = os.environ['USERS_DYNAMODB_TABLE']
    user_table = dynamodb_resource.Table(USERS_DYNAMODB_TABLE)

    http_method = event['httpMethod']
    action = event['action']

    response = None

    if http_method == 'GET':
        if action == 'get_trip_info_by_id':
            response = get_by_id(event, trips_table)

        elif action == 'get_trip_info_by_location':
            response = get_by_location(event, trips_table)

        elif action == 'get_trip_info_by_admin_id':
            response = get_by_admin_id(event, trips_table)

    elif http_method == 'POST':
        if action == 'create_trip':
            response = create_trip(event, trips_table)

        elif action == 'user_wants_to_go_on_trip':
            response = user_wants_to_go_on_trip(event, TRIPS_DYNAMO_TABLE, USERS_DYNAMODB_TABLE)

        elif action == 'user_approval':
            response = user_approval_request(event, TRIPS_DYNAMO_TABLE, USERS_DYNAMODB_TABLE)

        elif action == 'user_no_longer_wants_to_attend':
            response = user_no_longer_wants_to_attend(event, TRIPS_DYNAMO_TABLE, USERS_DYNAMODB_TABLE)

    return response if response else {
        'statusCode': 400,
        'body': 'Bad Request'
    }

