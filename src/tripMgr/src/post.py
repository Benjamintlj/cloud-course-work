from botocore.exceptions import BotoCoreError, ClientError
from .utils import create_new_id, remove_element_from_list
import boto3


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
            'description': event['body']['description'],
            'awaiting_approval': [],
            'approved': []
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


def user_wants_to_go_on_trip(event, trip_table_name, user_table_name):
    response = None

    dynamodb_client = boto3.client('dynamodb')

    try:
        user_id = int(event['body']['user_id'])
        trip_id = int(event['body']['trip_id'])

        transactions = [
            {
                'Update': {
                    'TableName': user_table_name,
                    'Key': {'user_id': {'N': str(user_id)}},
                    'UpdateExpression': 'SET awaiting_approval = list_append(if_not_exists(awaiting_approval, :empty_list), :val)',
                    'ExpressionAttributeValues': {':val': {'L': [{'N': str(trip_id)}]},
                                                  ':empty_list': {'L': []},
                                                  ':trip_id': {'N': str(trip_id)}
                                                  },
                    'ConditionExpression': 'attribute_not_exists(awaiting_approval) OR NOT contains(awaiting_approval, :trip_id)',
                }
            },
            {
                'Update': {
                    'TableName': trip_table_name,
                    'Key': {'trip_id': {'N': str(trip_id)}},
                    'UpdateExpression': 'SET awaiting_approval = list_append(if_not_exists(awaiting_approval, :empty_list), :val)',
                    'ExpressionAttributeValues': {':val': {'L': [{'N': str(user_id)}]},
                                                  ':empty_list': {'L': []},
                                                  ':user_id': {'N': str(user_id)}
                                                  },
                    'ConditionExpression': 'attribute_not_exists(awaiting_approval) OR NOT contains(awaiting_approval, :user_id)',
                }
            }
        ]

        dynamodb_client.transact_write_items(TransactItems=transactions)

        response = {
            'statusCode': 200
        }

    except ClientError as e:
        # this most likely means that the entries already exist in the awaiting approval column in ether table
        response = {
            'statusCode': 400,
            'details': 'Client Error the transaction failed: ' + str(e)
        }

    except Exception as e:
        response = {
            'statusCode': 500,
            'details': 'Error: ' + str(e)
        }

    return response


def user_approval_request(event, trip_table_name, user_table_name):
    response = None
    dynamodb_client = boto3.client('dynamodb')

    try:
        # must be a string for the expression
        user_id = str(event['body']['user_id'])
        trip_id = str(event['body']['trip_id'])
        is_approved = event['body']['is_approved']

        remove_element_from_list(trip_table_name, False, trip_id, user_id, False)
        remove_element_from_list(user_table_name, True, user_id, trip_id, False)

        if is_approved:
            """
            1.  user_id in awaiting_approval in trip_table should be moved to approved
            2.  trip_id in the awaiting_approval in the user_table should be moved in to the approved column
            """

            transactions = [
                {
                    'Update': {
                        'TableName': trip_table_name,
                        'Key': {'trip_id': {'N': str(trip_id)}},
                        'UpdateExpression': 'SET approved = list_append(if_not_exists(approved, :empty_list), :val)',
                        'ExpressionAttributeValues': {':val': {'L': [{'N': str(user_id)}]},
                                                      ':empty_list': {'L': []},
                                                      ':user_id': {'N': str(user_id)}
                                                      },
                        'ConditionExpression': 'attribute_not_exists(approved) OR NOT contains(approved, :user_id)',
                    }
                },
                {
                    'Update': {
                        'TableName': user_table_name,
                        'Key': {'user_id': {'N': str(user_id)}},
                        'UpdateExpression': 'SET approved = list_append(if_not_exists(approved, :empty_list), :val)',
                        'ExpressionAttributeValues': {':val': {'L': [{'N': str(trip_id)}]},
                                                      ':empty_list': {'L': []},
                                                      ':trip_id': {'N': str(trip_id)}
                                                      },
                        'ConditionExpression': 'attribute_not_exists(approved) OR NOT contains(approved, :trip_id)',
                    }
                }
            ]

            dynamodb_client.transact_write_items(TransactItems=transactions)

        response = {
            'statusCode': 200
        }

    except ClientError as e:
        response = {
            'statusCode': 400,
            'details': 'Transaction failed: ' + str(e)
        }

    except Exception as e:
        response = {
            'statusCode': 500,
            'details': 'Error: ' + str(e)
        }

    return response
