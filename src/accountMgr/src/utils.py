from boto3.dynamodb.conditions import Key
from botocore.exceptions import BotoCoreError
import os
import requests


def email_exists(email, table):
    """
    check if email exists in the table

    :parameter
        email: email to be checked against the table
        table: table to be checked against

    :returns
        True if email exists in the table
    """
    result = True

    try:
        response = table.query(
            IndexName="email-index",
            KeyConditionExpression=Key("email").eq(email)
        )

        if len(response['Items']) is 0:
            result = False

    except BotoCoreError as e:
        pass

    return result


def user_id_exists(user_id, table):
    """
    check if user_id exists in the table

    :parameter
        user_id: value to check if the user_id exist against
        table: the table to check against

    :returns
        True if the user_id exists
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

    :parameter
        table - the table to check against

    :returns
        a new user_id that does not clash with the existing user_ids

    :raises
        ValueError: if API response cannot be parsed
        ConnectionError: if function cannot connect to API
        Exception: if after multiple attempts to create new user_id fail
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
