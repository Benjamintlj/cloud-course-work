from botocore.exceptions import BotoCoreError
from .utils import email_exists, get_new_user_id, get_email_item


def post_create_user(event, table):
    """
    Creates a new user.

    :param event: Event passed to lambda.
    :type event: dict
    :param table: Table containing the user accounts.
    :type table: dynamodb.Table
    :returns: 201 if the creation of the user is successful, 400 if Email already exists, 500 for internal errors.
    :rtype: dict
    """

    response = None

    email = event['body']['email']
    password = event['body']['password']

    # Check if the email already exists
    if email_exists(email, table):
        response = {
            'statusCode': 400,
            'body': 'Email already exists'
        }
        return response

    try:
        # Get a new user id
        user_id = get_new_user_id(table)

        table.put_item(Item={
            'user_id': user_id,
            'email': email,
            'password': password,
            'awaiting_approval': [],
            'approved': []
        })

        response = {
            'statusCode': 201,
            'body': 'User created successfully'
        }

    except ValueError as e:
        response = {
            'statusCode': 500,
            'body': 'ValueError: ' + str(e)
        }

    except ConnectionError as e:
        response = {
            'statusCode': 500,
            'body': 'ConnectionError: ' + str(e)
        }

    except BotoCoreError as e:
        response = {
            'statusCode': 500,
            'body': 'BotoCoreError: ' + str(e)
        }

    except Exception as e:
        response = {
            'statusCode': 500,
            'body': 'Exception: ' + str(e)
        }

    return response


def post_login(event, table):
    """
    Validates if the user exists and if the credentials are correct.

    :param event: Event passed to lambda.
    :type event: dict
    :param table: Table containing the user accounts.
    :type table: dynamodb.Table
    :returns: 200 & user_id, if login was successful, 404 if user is not found, 401 if password is incorrect, 500 for internal error.
    :rtype: dict
    """

    response = None
    account_entry = get_email_item(event['body']['email'], table)

    if account_entry['statusCode'] == 200:
        if account_entry['body']['password'] == event['body']['password']:
            response = {
                'statusCode': 200,
                'body': {
                    'user_id': account_entry['body']['user_id'],
                }
            }
        else:
            response = {
                'statusCode': 401,
                'body': 'Incorrect password'
            }
    else:
        response = account_entry

    return response
