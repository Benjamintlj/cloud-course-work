import os
from botocore.exceptions import BotoCoreError
from boto3.dynamodb.conditions import Key
import boto3
from .utils import parse_dynamo_item, str_to_upper


def get_by_id(event, table):
    """
    Gets a trip by its id.

    :param event: Event passed to lambda.
    :type event: dict
    :param table: Table containing the trips.
    :type table: dynamodb.Table
    :return: 200 if trip_id was found, 404 if trip_id was not found, 500 for any internal error.
    :rtype: dict
    """
    response = None

    try:
        dynamo_response = table.get_item(Key={'trip_id': event['body']['trip_id']})

        if 'Item' in dynamo_response and dynamo_response['Item']:
            response = {
                'statusCode': 200,
                'body': dynamo_response['Item']
            }
        else:
            response = {
                'statusCode': 404,
            }

    except BotoCoreError as e:
        response = {
            'statusCode': 500,
            'details': 'BotoCoreError: ' + str(e)
        }

    except Exception as e:
        response = {
            'statusCode': 500,
            'details': 'Error: ' + str(e)
        }

    return response


def get_by_location(event, table):
    """
    Gets trips by location.

    :param event: Event passed to lambda.
    :type event: dict
    :param table: Table containing the trips.
    :type table: dynamodb.Table
    :return: 200 if location was found, 404 if location was not found, 500 for any internal error.
    :rtype: dict
    """
    response = None

    try:
        location = str_to_upper(event['body']['location'])

        dynamo_response = table.query(
            IndexName='location-index',
            KeyConditionExpression=Key('location').eq(location)
        )

        if len(dynamo_response.get('Items', [])) > 0:
            response = {
                'statusCode': 200,
                'body': dynamo_response.get('Items', [])
            }
        else:
            response = {
                'statusCode': 404,
            }

    except BotoCoreError as e:
        response = {
            'statusCode': 500,
            'details': 'BotoCoreError: ' + str(e)
        }

    except Exception as e:
        response = {
            'statusCode': 500,
            'details': 'Error: ' + str(e)
        }

    return response


def get_by_admin_id(event, table):
    """
    Gets trips by their associated admin_id.

    :param event: Event passed to lambda.
    :type event: dict
    :param table: Table containing the trips.
    :type table: dynamodb.Table
    :return: 200 if admin_id was found, 404 if admin_id was not found, 500 for any internal error.
    :rtype: dict
    """
    response = None

    try:
        admin_id = event['body']['admin_id']

        dynamo_response = table.query(
            IndexName='admin_id-index',
            KeyConditionExpression=Key('admin_id').eq(admin_id)
        )

        if len(dynamo_response.get('Items', [])) > 0:
            response = {
                'statusCode': 200,
                'body': dynamo_response.get('Items', [])
            }
        else:
            response = {
                'statusCode': 404,
            }

    except BotoCoreError as e:
        response = {
            'statusCode': 500,
            'details': 'BotoCoreError: ' + str(e)
        }

    except Exception as e:
        response = {
            'statusCode': 500,
            'details': 'Error: ' + str(e)
        }

    return response


def get_all_trips(table):
    """
    Scans dynamodb and returns all trips.

    :param table: Table containing the trips.
    :type table: dynamodb.Table
    :return: 200 if all trips are being returned maximum is around 1mb, 404 if no trips exist,
    500 for any internal error.
    :rtype: dict
    """
    response = None

    try:
        # Scan the table - Note that this will read the entire table.
        dynamo_response = table.scan()

        response = {
            'statusCode': 200,
            'body': dynamo_response['Items']  # 'Items' will contain all the records
        }

    except BotoCoreError as e:
        if "Invalid length for parameter" in str(e):
            response = {
                'statusCode': 404,
                'details': 'Invalid parameter: ' + str(e)
            }
        else:
            response = {
                'statusCode': 500,
                'details': 'BotoCoreError: ' + str(e)
            }

    except Exception as e:
        response = {
            'statusCode': 500,
            'details': 'Error: ' + str(e)
        }

    return response


def get_all_trips_for_user_id(event, user_table, trip_table_name):
    """
    Gets trips associated with a specified user_id.

    :param event: Event passed to lambda.
    :type event: dict
    :param user_table: Table containing the user.
    :type user_table: dynamodb.Table
    :param trip_table_name: The name of the trips table.
    :return: 200 if user_id was found, 404 if user_id or trips where not found, 500 for any internal error.
    :rtype: dict
    """
    dynamodb = boto3.client('dynamodb')

    response = None

    try:
        # 1. Get awaiting approval and approved, and append them into one list
        dynamo_response = user_table.get_item(Key={'user_id': event['body']['user_id']})

        trip_ids = dynamo_response['Item']['approved']
        trip_ids += dynamo_response['Item']['awaiting_approval']

        # 2. Return a list of all the trip ids
        keys = [{'trip_id': {'N': str(trip_id)}} for trip_id in trip_ids]

        dynamo_response = dynamodb.batch_get_item(
            RequestItems={
                trip_table_name: {
                    'Keys': keys,
                    'ConsistentRead': False
                }
            }
        )

        items = dynamo_response['Responses'][trip_table_name]
        json_items = [parse_dynamo_item(item) for item in items]

        response = {
            'statusCode': 200,
            'body': {
                'items': json_items
            }
        }

    except BotoCoreError as e:
        if "Invalid length for parameter" in str(e):
            response = {
                'statusCode': 404,
                'details': 'Invalid parameter: ' + str(e)
            }
        else:
            response = {
                'statusCode': 500,
                'details': 'BotoCoreError: ' + str(e)
            }
    except Exception as e:
        response = {
            'statusCode': 500,
            'details': 'Error: ' + str(e)
        }

    return response
