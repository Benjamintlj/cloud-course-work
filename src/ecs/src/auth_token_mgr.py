import secrets
import boto3
import os
from fastapi import HTTPException


# PLEASE NOTE THIS IS A STANDARD PYTHON PATTERN
class SingletonParentClass(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class AuthTokenMgr(metaclass=SingletonParentClass):
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(os.environ['TOKEN_DYNAMODB_TABLE'])

    def is_token_valid(self, user_id, token):
        """
        Validates a user_id against a token.

        :param user_id: User_id to check.
        :type user_id: int
        :param token: Auth token.
        :type token: str

        :return: True if token is valid.

        :raises HTTPException: With status code 405 if the user id exists.
        :raises HTTPException: With status code 500 for some kind of internal error.
        """

        try:
            response = self.table.get_item(Key={'user_id': user_id})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not check existing sign-ins: {str(e)}")

        if 'Item' in response and 'token' in response['Item']:
            return token == response['Item']['token']

        if not response.get('Item'):
            raise HTTPException(status_code=405, detail="User ID not signed in")

        return False

    def create_token(self, user_id):
        """
        Creates a new token for a certain user_id.

        :param user_id: User_id the token is for.
        :type user_id: int

        :return: The new token.

        :raises HTTPException: With status code 500 for some kind of internal error.
        """

        new_token = secrets.token_hex(16)
        try:
            self.table.put_item(Item={'user_id': user_id, 'token': new_token})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unable to signin: {str(e)}")
        return new_token

    def remove_token(self, user_id):
        """
        Removes the token from the user_id.

        :param user_id: User_id the token is for.
        :type user_id: int

        :return: True if successful.

        :raises HTTPException: With status code 500 for some kind of internal error.
        """

        try:
            response = self.table.delete_item(Key={'user_id': user_id})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unable to sign-out correctly: {str(e)}")
        return True
