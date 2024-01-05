from .utils import remove_element_from_list
from botocore.exceptions import ClientError


def delete_trip(event, trips_table, user_table_name):
    """
    Takes the response from dynamodb that specifies the types, and converts it into a standard python dict.

    :param event: Event passed to lambda.
    :type event: dict
    :param trips_table: The trips table client.
    :type trips_table: dynamodb.Table
    :param user_table_name: The name of the user table.
    :type user_table_name: str
    :return: 200 if removal was successful, 400 if the transaction failed, 500 for any internal error.
    :rtype: dict
    """

    response = None

    try:
        trip_id = int(event['body']['trip_id'])

        trip_row = trips_table.get_item(Key={'trip_id': trip_id})
        item = trip_row.get('Item', {})

        for id_value in item['awaiting_approval']:
            remove_element_from_list(user_table_name, True, id_value, trip_id, False)

        for id_value in item['approved']:
            remove_element_from_list(user_table_name, True, id_value, trip_id, True)

        trips_table.delete_item(Key={'trip_id': trip_id})

        response = {
            'statusCode': 200,
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
