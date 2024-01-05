from botocore.exceptions import BotoCoreError


def get_email(event, table):
    """
    Gets the email for a given user_id.

    :param event: Event passed to lambda.
    :type event: dict
    :param table: Table containing the user accounts.
    :type table: dynamodb.Table
    :return: 200 if user_id was found, 404 if user_id was not found, 500 for any internal error.
    :rtype: dict
    """
    response = None

    user_id = event['body']['user_id']

    try:
        result = table.get_item(Key={'user_id': user_id})

        if 'Item' in result:
            email = result['Item'].get('email', 'No email found')
            response = {
                'statusCode': 200,
                'body': {
                    "email": email
                }
            }
        else:
            response = {
                'statusCode': 404,
                'body': 'User not found'
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
