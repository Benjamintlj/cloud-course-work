from .get import get_by_id, get_by_location, get_by_admin_id, get_all_trips, get_all_trips_for_user_id
from .post import create_trip, user_wants_to_go_on_trip, user_approval_request, remove_user_application
from .delete import delete_trip
import boto3
import os


def main(event, context):
    """
    Main event handler, this method directs events to the correct functions based on a action and httpMethod.
    """
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

        elif action == 'get_all_trips':
            response = get_all_trips(trips_table)

        elif action == 'get_all_trips_for_user_id':
            response = get_all_trips_for_user_id(event, user_table, TRIPS_DYNAMO_TABLE)

    elif http_method == 'POST':
        if action == 'create_trip':
            response = create_trip(event, trips_table)

        elif action == 'user_wants_to_go_on_trip':
            response = user_wants_to_go_on_trip(event, TRIPS_DYNAMO_TABLE, USERS_DYNAMODB_TABLE)

        elif action == 'user_approval':
            response = user_approval_request(event, TRIPS_DYNAMO_TABLE, USERS_DYNAMODB_TABLE)

        elif action == 'remove_user_application':
            response = remove_user_application(event, TRIPS_DYNAMO_TABLE, USERS_DYNAMODB_TABLE)

    elif http_method == 'DELETE':
        if action == 'delete_trip':
            response = delete_trip(event, trips_table, USERS_DYNAMODB_TABLE)

    return response if response else {
        'statusCode': 400,
        'body': 'Bad Request'
    }

