import random
import time
import boto3


def create_new_id(table):
    """
    generates a new id of type int for the input table

    :param table: that the new id will be created for

    :return the new id
    """
    for _ in range(3):
        timestamp = int(time.time())
        random_number = random.randint(0, 9999)
        uid = timestamp * 10000 + random_number

        response = table.get_item(Key={'trip_id': uid})
        if 'Item' not in response:
            return uid

    raise Exception("Failed to generate trips_id after 3 attempts")
