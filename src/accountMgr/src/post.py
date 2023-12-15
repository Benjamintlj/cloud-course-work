from botocore.exceptions import BotoCoreError
from .utils import email_exists, get_new_user_id, get_email_item
from .column_names import __user_id_column__, __password_column__, __email_column__, __email_index__


def post_create_user(event, table):
    """
    creates a new user

    :param event: event passed to lambda
    :param table: table containing the user accounts
    :return: 201 if the creation of the user is successful,
    400 if Email already exists
    500 for internal errors
    """
    response = None

    email = event['body'][__email_column__]
    password = event['body'][__password_column__]

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
            __user_id_column__: user_id,
            __email_column__: email,
            __password_column__: password
        })

        response = {
            'statusCode': 201,
            'body': 'User created successfully'
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
    validates if the user exists and if the credentials are correct

    :param event: event passed to lambda
    :param table: table containing the user accounts

    :return 200 & user_id, if login was successful
    404 if user is not found
    401 if password is incorrect
    500 for internal error
    """
    response = None

    account_entry = get_email_item(event['body'][__email_column__], table)

    if account_entry['statusCode'] == 200:
        if account_entry['body'][__password_column__] == event['body'][__password_column__]:
            response = {
                'statusCode': 200,
                'body': {
                    __user_id_column__: account_entry['body'][__user_id_column__],
                }
            }
        else:
            response = {
                'statusCode': 401,
                'Error': 'Incorrect password'
            }
    else:
        response = account_entry

    return response
