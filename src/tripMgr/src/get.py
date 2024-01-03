import os
from botocore.exceptions import BotoCoreError
from boto3.dynamodb.conditions import Key
import boto3
from .utils import parse_dynamo_item, str_to_upper


def get_by_id(event, table):
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


def get_all_trips_for_user_id(event, user_table, trips_table):
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
                os.environ['TRIPS_DYNAMODB_TABLE']: {
                    'Keys': keys,
                    'ConsistentRead': False
                }
            }
        )

        items = dynamo_response['Responses'][os.environ['TRIPS_DYNAMODB_TABLE']]
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


def get_all_trips_for_user_id(event, user_table, trips_table):
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
                os.environ['TRIPS_DYNAMODB_TABLE']: {
                    'Keys': keys,
                    'ConsistentRead': False
                }
            }
        )

        items = dynamo_response['Responses'][os.environ['TRIPS_DYNAMODB_TABLE']]
        json_items = [parse_dynamo_item(item) for item in items]

        response = {
            'statusCode': 200,
            'body': {
                'items': json_items
            }
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
