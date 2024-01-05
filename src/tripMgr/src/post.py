from botocore.exceptions import BotoCoreError, ClientError
from .utils import create_new_id, remove_element_from_list, str_to_upper
import boto3


def create_trip(event, table):
    """
    Creates a new trip.

    :param event: Event passed to lambda.
    :type event: dict
    :param table: Table containing the trip.
    :type table: dynamodb.Table
    :return: 201 if the new trips is created successfully, 500 for any internal error.
    :rtype: dict
    """

    response = None

    try:
        uid = create_new_id(table)
        location_name = str_to_upper(event['body']['location'])
        title_name = str_to_upper(event['body']['title'])

        table.put_item(Item={
            'trip_id': uid,
            'admin_id': event['body']['admin_id'],
            'start_date': event['body']['start_date'],
            'end_date': event['body']['end_date'],
            'location': location_name,
            'title': title_name,
            'description': event['body']['description'],
            'awaiting_approval': [],
            'approved': []
        })

        response = {
            'statusCode': 201
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
    """
    User gets added to the application column of the trip entry.

    :param event: Event passed to lambda.
    :type event: dict
    :param trip_table_name: Name of the trip table.
    :type trip_table_name: str
    :param user_table_name: Name of the user table.
    :type user_table_name: str
    :return: 200 user application is successfully added, 400 entry fails to be added likely because user has
    already applied, 500 for any internal error.
    :rtype: dict
    """

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
    """
    Approve user from awaiting approval to approved columns.

    :param event: Event passed to lambda.
    :type event: dict
    :param trip_table_name: Name of the trip table.
    :type trip_table_name: str
    :param user_table_name: Name of the user table.
    :type user_table_name: str
    :return: 200 user application is successfully moved, 400 the transaction failed likely because user already
    exists in eather column, 500 for any internal error.
    :rtype: dict
    """

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


def remove_user_application(event, trip_table_name, user_table_name):
    """
    Removes user from awaiting approval and approved columns.

    :param event: Event passed to lambda.
    :type event: dict
    :param trip_table_name: Name of the trip table.
    :type trip_table_name: str
    :param user_table_name: Name of the user table.
    :type user_table_name: str
    :return: 200 if the user application is successfully moved.
    :rtype: dict
    """

    user_id = str(event['body']['user_id'])
    trip_id = str(event['body']['trip_id'])

    try:
        remove_element_from_list(trip_table_name, False, trip_id, user_id, False)
    except Exception:
        pass

    try:
        remove_element_from_list(user_table_name, True, user_id, trip_id, False)
    except Exception:
        pass

    try:
        remove_element_from_list(trip_table_name, False, trip_id, user_id, True)
    except Exception:
        pass

    try:
        remove_element_from_list(user_table_name, True, user_id, trip_id, True)
    except Exception:
        pass

    return {
        'statusCode': 200,
    }
