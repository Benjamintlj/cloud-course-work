from botocore.exceptions import BotoCoreError
from boto3.dynamodb.conditions import Key


def get_by_id(event, table):
    response = None

    try:
        dynamo_response = table.get_item(Key={'trip_id': event['body']['trip_id']})

        response = {
            'statusCode': 200,
            'body': dynamo_response['Item']
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
        location = event['body']['location']
        dynamo_response = table.query(
            IndexName='location-index',
            KeyConditionExpression=Key('location').eq(location)
        )

        response = {
            'statusCode': 200,
            'body': dynamo_response.get('Items', [])
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

        response = {
            'statusCode': 200,
            'body': dynamo_response.get('Items', [])
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
