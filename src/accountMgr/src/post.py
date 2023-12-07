from botocore.exceptions import BotoCoreError
from .utils import email_exists, get_new_user_id


def post_create_user(event, table):
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
            'password': password
        })

        response = {
            'statusCode': 200,
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
