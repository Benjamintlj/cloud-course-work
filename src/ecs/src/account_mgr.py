from fastapi import HTTPException, Depends, Request
from fastapi.responses import JSONResponse
import json
import logging
from pydantic import BaseModel
from .utils import call_account_mgr
from .auth_token_mgr import AuthTokenMgr
from .auth_route_dependency import authenticate_request


class CreateAccountRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class SignOutRequest(BaseModel):
    user_id: int


def account_mgr(app, lambda_client):
    """
    Method that defines all account mgr methods.
    """
    @app.post('/account')
    def create_account(request: CreateAccountRequest):
        """
        Creates an account.

        :param request: Is the body containing the email and password as strings.
        :return: None

        :raises HTTPException: With status code 400 if username already exists.
        :raises HTTPException: With status code 500 in an internal error occurred.
        :raises HTTPException: With status code 502 if the lambda fails unexpectedly.
        """
        email = request.email
        password = request.password

        content = None

        try:
            payload = json.dumps({
                'httpMethod': 'POST',
                'action': 'create_user',
                'body': {
                    'email': email,
                    'password': password
                }
            })

            response_payload = call_account_mgr(lambda_client, payload)

            status_code = response_payload['statusCode']

            if status_code == 201:
                pass
            elif status_code == 400:
                raise HTTPException(status_code=400, detail='User already exists')
            else:
                logging.error('error while creating user returned non-201 response: ' + str(response_payload))
                raise HTTPException(status_code=500, detail='Error while creating user non-201 response')

        except HTTPException as http_exception:
            raise http_exception
        except Exception as e:
            logging.error('invoking user_mgr: ' + str(e))
            raise HTTPException(status_code=500, detail=str(e))

        return JSONResponse(status_code=201, content=content)

    @app.post('/login')
    def login(request: LoginRequest):
        """
        Signs the user in.

        :param request: Is the body containing the email and password as strings.
        :return: An auth token to be used in each subsequent request.

        :raises HTTPException: With status code 401 if password was incorrect.
        :raises HTTPException: With status code 404 if username was not found.
        :raises HTTPException: With status code 500 in an internal error occurred.
        :raises HTTPException: With status code 502 if the lambda fails unexpectedly.
        """

        email = request.email
        password = request.password

        content = None

        try:
            payload = json.dumps({
                'httpMethod': 'POST',
                'action': 'login',
                'body': {
                    'email': email,
                    'password': password
                }
            })

            response_payload = call_account_mgr(lambda_client, payload)

            status_code = response_payload['statusCode']

            if status_code == 200:
                auth_token = AuthTokenMgr().create_token(response_payload['body']['user_id'])

                content = {
                    'user_id': response_payload['body']['user_id'],
                    'auth_token': auth_token
                }
            elif status_code == 401:
                raise HTTPException(status_code=401, detail='Incorrect password')
            elif status_code == 404:
                raise HTTPException(status_code=404, detail='Unknown username')
            elif status_code == 500:
                logging.error('An error occurred while calling the lambda: ' + str(response_payload))
                raise HTTPException(status_code=500, detail='Server error occurred')
            else:
                logging.error('An error occurred while calling the lambda: ' + str(response_payload))
                raise HTTPException(status_code=500, detail='Internal error occurred')

        except HTTPException as http_exception:
            raise http_exception

        except Exception as e:
            logging.error('invoking user_mgr: ' + str(e))
            raise HTTPException(status_code=500, detail=str(e))

        return JSONResponse(status_code=200, content=content)

    @app.post('/sign-out')
    async def sign_out(user_id=Depends(authenticate_request)):
        """
        Signs the user out.

        :return: None

        :raises HTTPException: With status code 500 in an internal error occurred.
        :raises HTTPException: With status code 502 if the lambda fails unexpectedly.
        """

        content = None

        is_user_removed = AuthTokenMgr().remove_token(user_id)

        content = {
            'isUserRemovedFromTokenTable': is_user_removed
        }

        return JSONResponse(status_code=200, content=content)

    @app.get('/email')
    async def get_email(user_id_of_email: int, user_id=Depends(authenticate_request)):
        """
        Returns the email for a specific user_id.

        :param user_id_of_email: User id of the desired email.
        :type: int

        :return: The email.

        :raises HTTPException: With status code 404 if the user_id is unknown.
        :raises HTTPException: With status code 500 in an internal error occurred.
        :raises HTTPException: With status code 502 if the lambda fails unexpectedly.
        """

        content = None

        try:
            payload = json.dumps({
                'httpMethod': 'GET',
                'action': 'get_email',
                'body': {
                    'user_id': user_id_of_email,
                }
            })

            response_payload = call_account_mgr(lambda_client, payload)

            status_code = response_payload['statusCode']

            if status_code == 200:
                content = {
                    'email': response_payload['body']['email'],
                }
            elif status_code == 404:
                raise HTTPException(status_code=404, detail='Unknown userId')
            elif status_code == 500:
                logging.error('An error occurred while calling the lambda: ' + str(response_payload))
                raise HTTPException(status_code=500, detail='Server error occurred')
            else:
                logging.error('An error occurred while calling the lambda: ' + str(response_payload))
                raise HTTPException(status_code=500, detail='Internal error occurred')

        except HTTPException as http_exception:
            raise http_exception

        except Exception as e:
            logging.error('invoking user_mgr: ' + str(e))
            raise HTTPException(status_code=500, detail=str(e))

        return JSONResponse(status_code=200, content=content)
