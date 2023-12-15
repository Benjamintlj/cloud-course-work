from botocore.exceptions import BotoCoreError
from .utils import create_new_id


def create_trip(event, table):
    """
    creates a new trip entry

    :param event: event passed to lambda
    :param table: pointing to the trips table

    :return 200 if create was successful
    500 if create failed
    """

    response = None

    try:
        uid = create_new_id(table)

        table.put_item(Item={
            'trip_id': uid,
            'admin_id': event['body']['admin_id'],
            'start_date': event['body']['start_date'],
            'end_date': event['body']['end_date'],
            'location': event['body']['location'],
            'title': event['body']['title'],
            'description': event['body']['description']
        })

        response = {
            'statusCode': 200
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
