import random
import time
import boto3


def create_new_id(table):
    """
    Generates a new id of type int for the input table.

    :param table: The trips table that the new id will be created for.
    :type table: dynamodb.Table
    :return: New unique key for the trips table.
    :rtype: dict
    :raises Exception: Raised after 3 attempts to create a new id fail.
    """

    for _ in range(3):
        timestamp = int(time.time())
        random_number = random.randint(0, 9999)
        uid = timestamp * 10000 + random_number

        response = table.get_item(Key={'trip_id': uid})
        if 'Item' not in response:
            return uid

    raise Exception("Failed to generate trips_id after 3 attempts")


def remove_element_from_list(table_name, is_user_table, lookup_id, element_to_remove, is_approved_column):
    """
    Generates a new id of type int for the input table.

    :param table_name: Name of the table to remove the application entries from.
    :type table_name: str
    :param is_user_table: True for user table, False for trip table.
    :type is_user_table: bool
    :param lookup_id: User_id or trip_id of the row containing the entry to remove.
    :type lookup_id: int
    :param element_to_remove: Trip_id or user_id of the entry to remove from applications.
    :type element_to_remove: int
    :param is_approved_column: Is the entry being removed in the approved (True) or awaiting approval (False) column.
    :type is_approved_column: bool
    :return: None
    :raises Exception: Raised if entry could not be removed, likely cause is if the entry did not exist.
    """

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    id_column = 'user_id' if is_user_table else 'trip_id'
    approval_column = 'approved' if is_approved_column else 'awaiting_approval'

    response = table.get_item(Key={id_column: int(lookup_id)})
    item = response.get('Item', {})

    index = 0
    for id_value in item[approval_column]:
        if str(id_value) == str(element_to_remove):
            update_expression = f'REMOVE {approval_column}[{index}]'
            table.update_item(
                Key={id_column: int(lookup_id)},
                UpdateExpression=update_expression
            )
            return
        else:
            index += 1

    raise Exception("User was not in the awaiting approval / approved list")


def str_to_upper(val):
    """
    This method reformats strings to a constant casing.
    Example: "helLo wOrlD" -> "Hello World"

    :param val: String to reformat.
    :type val: str
    :return: New reformatted string.
    :rtype: str
    """
    words = val.split()

    new_words = []
    for word in words:
        new_word = ''
        new_word += word[0].upper()
        new_word += word[1:].lower()
        new_words.append(new_word)

    return ' '.join(new_words)


# This code was copied from:
# https://stackoverflow.com/questions/32712675/formatting-dynamodb-data-to-normal-json-in-aws-lambda
def parse_dynamo_value(val):
    """
    Takes the response from dynamodb that specifies the types, and converts it into a standard python dict.

    :param val: Dict to reformat.
    :type val: dict
    :return: New dict.
    :rtype: dict
    """
    if 'S' in val:
        return val['S']
    elif 'N' in val:
        return int(val['N'])
    elif 'L' in val:
        return [parse_dynamo_value(i) for i in val['L']]


# This code was copied from:
# https://stackoverflow.com/questions/32712675/formatting-dynamodb-data-to-normal-json-in-aws-lambda
def parse_dynamo_item(item):
    parsed_item = {}
    for key, val in item.items():
        parsed_item[key] = parse_dynamo_value(val)
    return parsed_item
