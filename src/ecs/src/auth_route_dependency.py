from .auth_token_mgr import AuthTokenMgr
from fastapi import Header, HTTPException, Depends, Request


def authenticate_request(request: Request):
    """
    Authenticates any request that depends on this method returning user_id.
    Example signature: def func_name(user_id=Depends(authenticate_request)):

    :return: user_id of the requester.
    """
    headers = request.headers

    user_id = int(headers.get('User-Id'))
    authorization = headers.get('Authorization')

    if not AuthTokenMgr().is_token_valid(user_id, authorization):
        raise HTTPException(status_code=401, detail='Invalid authorization code or user_id')

    return user_id
