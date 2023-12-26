from fastapi import HTTPException
import os
import json
import logging


def handle_lambda_response(lambda_response):
    if lambda_response['ResponseMetadata']['HTTPStatusCode'] != 200:
        logging.error('lambda returned non-200 response: ' + str(lambda_response))
        raise HTTPException(status_code=502, detail='Error lambda returned non-200 response')

    response_payload = lambda_response['Payload'].read().decode('utf-8')
    response_payload = json.loads(response_payload)

    return response_payload


def call_account_mgr(lambda_client, payload):
    lambda_response = lambda_client.invoke(
        FunctionName=os.getenv('USER_MGR_ARN'),
        InvocationType='RequestResponse',
        Payload=payload
    )

    return handle_lambda_response(lambda_response)


def call_trip_mgr(lambda_client, payload):
    lambda_response = lambda_client.invoke(
        FunctionName=os.getenv('TRIP_MGR_ARN'),
        InvocationType='RequestResponse',
        Payload=payload
    )

    return handle_lambda_response(lambda_response)
