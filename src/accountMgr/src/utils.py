from boto3.dynamodb.conditions import Key
from botocore.exceptions import BotoCoreError
import requests


def email_exists(email, table):
    """
    Check if email exists in the table.

    :param email: Email to be checked against the table.
    :type email: str
    :param table: Table to be checked against.
    :type table: dynamodb.Table
    :returns: True if email exists in the table.
    :rtype: bool
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
    Gets the entry associated with the email.

    :param email: Email to be retrieved.
    :type email: str
    :param table: Table containing the users.
    :type table: dynamodb.Table
    :returns: A dictionary with the status code and either the entry or an error message. It returns 200 and the entry associated with the email if found, 404 if the email is not found, 500 for internal BotoCoreError.
    :rtype: dict
    """

    result = None

    try:
        response = table.query(
            IndexName='email-index',
            KeyConditionExpression=Key('email').eq(email)
        )

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
    Check if user_id exists in the table.

    :param user_id: Value to check if the user_id exists against.
    :type user_id: int
    :param table: The table to check against.
    :type table: dynamodb.Table
    :returns: True if the user_id exists.
    :rtype: bool
    """

    result = False

    try:
        response = table.get_item(
            Key={
                'user_id': user_id
            }
        )

        if 'Item' in response:
            result = True

    except BotoCoreError as e:
        pass

    return result


def pop_user_id_cache(table):
    """
    Pops the user_id from the cache within DynamoDB.

    :param table: The table containing the cache.
    :type table: dynamodb.Table
    :returns: The user_id from the top of the FILO.
    :rtype: int
    :raises Exception: if the operation fails, this may result in loss of data from the FILO.
    """

    try:
        response = table.get_item(Key={'user_id': 0})
        item = response.get('Item', {})
        cached_user_ids = item.get('cached_user_ids', [])

        if not cached_user_ids:
            raise Exception('No user_id exists')

        user_id = cached_user_ids[0]

    except Exception as ignore:
        raise Exception('Failed to read user_id')

    try:
        table.update_item(
            Key={'user_id': 0},
            UpdateExpression='REMOVE cached_user_ids[0]',
            ReturnValues='UPDATED_NEW'
        )

    except BotoCoreError as ignore:
        raise Exception('Botocore error: Failed to remove user_id')

    except Exception as ignore:
        raise Exception('Failed to remove user_id')

    return user_id


def generate_cached_user_id(table):
    """
    Generates a new user_id between 100000000000 & 999999999999, the user_id is guaranteed to not clash with existing
    user_ids, it then stores the user_id within cache.

    :param table: The table to generate the new user_id for.
    :type table: dynamodb.Table
    :returns: True if no failures.
    :rtype: bool
    :raises ValueError: if API fails to respond correctly.
    :raises ConnectionError: if connection fails API via Requests.
    :raises BotoCoreError: if an issue occurs while adding the user_id to the FILO. Please note that checks happen
    during this stage, so they can also raise the exception.
    """

    random_min = 100000000000
    random_max = 999999999999
    url = f'https://csrng.net/csrng/csrng.php?min={random_min}&max={random_max}'
    cached_user_id_entry = 0

    try:
        response = requests.get(url)
        data = response.json()

        if data[0]['status'] != 'success':
            raise ValueError('API response status is not success')

        user_id = data[0]['random']

        if not user_id_exists(user_id, table):
            table.update_item(
                Key={'user_id': cached_user_id_entry},
                UpdateExpression='SET cached_user_ids = '
                                 'list_append(if_not_exists(cached_user_ids, :empty_list), :num)',
                ExpressionAttributeValues={
                    ':num': [user_id],
                    ':empty_list': [],
                    ':val': user_id
                },
                ConditionExpression='NOT contains (cached_user_ids, :val)',
                ReturnValues='UPDATED_NEW'
            )

    except BotoCoreError as e:
        raise e

    except requests.exceptions.RequestException as e:
        raise ConnectionError('Failed to establish a new connection: ' + str(e))

    except ValueError as e:
        raise ValueError('Error processing API response: ' + str(e))

    return True


def length_of_cached_user_ids(table):
    """
    Returns the length of the cached user FILO queue.

    :param table: Table containing the queue.
    :type table: dynamodb.Table
    :returns: The length of the queue.
    :rtype: int
    :raises BotoCoreError: if failed to read the queue.
    :raises Exception: for safe guarding.
    """

    try:
        response = table.get_item(Key={'user_id': 0})
    except BotoCoreError as e:
        raise e
    except Exception as e:
        raise Exception('Failed to read cached user_ids: ' + str(e))

    if 'Item' in response and 'cached_user_ids' in response['Item']:
        return len(response['Item']['cached_user_ids'])
    else:
        return 0


def get_new_user_id(table):
    """
    Calls an external API to get a new user id, it will also update the user_id cache.

    :param table: The table to check against.
    :type table: dynamodb.Table
    :returns: A new user_id that does not clash with the existing user_ids.
    :rtype: int
    :raises BotoCoreError: if an exception is thrown while interacting with DynamoDB.
    :raises ValueError: if API response cannot be parsed.
    :raises ConnectionError: if function cannot connect to API.
    :raises Exception: if after multiple attempts to create new user_id fail.
    """

    random_min = 0
    random_max = 100000000000
    url = f'https://csrng.net/csrng/csrng.php?min={random_min}&max={random_max}'
    attempts = 0

    if length_of_cached_user_ids(table) < 5:
        # this function can raise a ValueError or ConnectionError
        generate_cached_user_id(table)

    while attempts < 3:
        try:
            response = requests.get(url)
            data = response.json()

            if data[0]['status'] != 'success':
                raise ValueError('API response status is not success')

            user_id = data[0]['random']

            if not user_id_exists(user_id, table):
                return user_id

        except requests.exceptions.RequestException as e:
            # handle a bad connection
            return pop_user_id_cache(table)

        except ValueError as e:
            raise ValueError(f'Error processing API response: {e}')

        finally:
            attempts += 1

    raise Exception('Error cannot create a new user_id')
