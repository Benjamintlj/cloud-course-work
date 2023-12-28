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


def pop_user_id_cache(table):
    try:
        response = table.get_item(Key={'user_id': 0})
        item = response.get('Item', {})
        cached_user_ids = item.get('cached_user_ids', [])

        if not cached_user_ids:
            raise Exception('No user_id available to pop')

        user_id = cached_user_ids[0]

    except Exception as e:
        raise Exception('Failed to read user_id')

    try:
        table.update_item(
            Key={'user_id': 0},
            UpdateExpression='REMOVE cached_user_ids[0]',
            ReturnValues='UPDATED_NEW'
        )
    except Exception as e:
        raise Exception('Failed to remove user_id')

    return user_id


def generate_cached_user_id(table):
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

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f'Failed to establish a new connection: {e}')

    except ValueError as e:
        raise ValueError(f'Error processing API response: {e}')

    return {
        'statusCode': 200
    }


def len_cached_user_ids(table):
    try:
        response = table.get_item(Key={'user_id': 0})
    except Exception as e:
        raise Exception('Failed to read cached user_ids')

    if 'Item' in response and 'cached_user_ids' in response['Item']:
        return len(response['Item']['cached_user_ids'])
    else:
        return 0


def get_new_user_id(table):
    """
    calls an external api to get a new user id, it will also update the user_id cache

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

    if len_cached_user_ids(table) < 5:
        generate_cached_user_id(table)

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
            # handle a bad connection
            return pop_user_id_cache(table)

        except ValueError as e:
            raise ValueError(f"Error processing API response: {e}")

        finally:
            attempts += 1

    raise Exception(f"Error cannot create a new user_id")
