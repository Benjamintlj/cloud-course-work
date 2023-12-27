from .auth_token_mgr import AuthTokenMgr
from fastapi import Header, HTTPException, Depends, Request


def authenticate_request(request: Request):
    headers = request.headers

    user_id = int(headers.get('User-Id'))
    authorization = headers.get('Authorization')

    if not AuthTokenMgr().is_token_valid(user_id, authorization):
        raise HTTPException(status_code=401, detail='Invalid authorization code or user_id')

    return user_id
