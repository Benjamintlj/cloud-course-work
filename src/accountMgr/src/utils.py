from boto3.dynamodb.conditions import Key
from botocore.exceptions import BotoCoreError
import requests


def email_exists(email, table):
    """
    check if email exists in the table

    :param email: email to be checked against the table
    :param table: table to be checked against

    :return: True if email exists in the table
    """
    result = True

    try:
        response = table.query(
            IndexName='email-index',
            KeyConditionExpression=Key('email').eq(email)
        )

        if len(response['Items']) is 0:
            result = False

    except BotoCoreError as e:
        pass

    return result


def get_email_item(email, table):
    """
    gets the entry associated with the email

    :param email: email to be retrieved
    :param table: table containing the users

    :return: 200 & the entry associated with the email,
    404 if the email is not found,
    500 if for internal BotoCoreError
    """
    result = None

    try:
        response = table.query(
            IndexName='email-index',
            KeyConditionExpression=Key('email').eq(email)
        )
        print(response)

        if len(response['Items']) is 0:
            result = {
                "statusCode": 404,
                "Error": "Account not found"
            }
        else:
            result = {
                "statusCode": 200,
                "body": {
                    'user_id': response['Items'][0]['user_id'],
                    'email': response['Items'][0]['email'],
                    'password': response['Items'][0]['password']
                }
            }

    except BotoCoreError as e:
        result = {
            "statusCode": 500,
            "Error": "BotoCoreError " + str(e)
        }

    return result


def user_id_exists(user_id, table):
    """
    check if user_id exists in the table

    :param user_id: value to check if the user_id exist against
    :param table: the table to check against

    :return True if the user_id exists
    """
    result = True

    try:
        response = table.get_item(
            Key={
                'user_id': user_id
            }
        )

        if 'Item' in response:
            result = True
        else:
            result = False

    except BotoCoreError as e:
        pass

    return result


def get_new_user_id(table):
    """
    calls an external api to get a new user id

    :param table: the table to check against

    :return a new user_id that does not clash with the existing user_ids

    :raise ValueError: if API response cannot be parsed
    :raise ConnectionError: if function cannot connect to API
    :raise Exception: if after multiple attempts to create new user_id fail
    """
    random_min = 0
    random_max = 100000000000
    url = f"https://csrng.net/csrng/csrng.php?min={random_min}&max={random_max}"
    attempts = 0

    while attempts < 3:
        try:
            response = requests.get(url)
            data = response.json()

            if data[0]['status'] != 'success':
                raise ValueError("API response status is not success")

            user_id = data[0]['random']

            if not user_id_exists(user_id, table):
                return user_id

        except requests.exceptions.RequestException as e:
            # Handle exceptions related to the package library
            raise ConnectionError(f"Failed to establish a new connection: {e}")

        except ValueError as e:
            raise ValueError(f"Error processing API response: {e}")

        finally:
            attempts += 1

    raise Exception(f"Error cannot create a new user_id")
