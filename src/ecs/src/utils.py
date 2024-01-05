from fastapi import HTTPException
import os
import json
import logging
from datetime import datetime
import time
import boto3
from botocore.exceptions import ClientError


def handle_lambda_response(lambda_response):
    """
    Checks a lambdas response to ensure that it worked correctly.

    :param lambda_response: The raw response from the lambda called.
    :type lambda_response: dict
    :return: The response payload from the lambda.
    :rtype: dict

    :raises HTTPException: With status code 502 if the lambda fails unexpectedly.
    """

    if lambda_response['ResponseMetadata']['HTTPStatusCode'] != 200:
        logging.error('lambda returned non-200 response: ' + str(lambda_response))
        raise HTTPException(status_code=502, detail='Error lambda returned non-200 response')

    response_payload = lambda_response['Payload'].read().decode('utf-8')
    response_payload = json.loads(response_payload)

    return response_payload


def call_account_mgr(lambda_client, payload):
    """
    Calls the account_mgr lambda with the given payload.

    :param lambda_client: The lambda client.
    :type lambda_client: boto3.client
    :param payload: Payload to send to the lambda.
    :type payload: dict
    :return: The response payload from the lambda with any other details abstracted away.
    :rtype: dict

    :raises HTTPException: With status code 502 if the lambda fails unexpectedly.
    """

    lambda_response = lambda_client.invoke(
        FunctionName=os.getenv('USER_MGR_ARN'),
        InvocationType='RequestResponse',
        Payload=payload
    )

    return handle_lambda_response(lambda_response)


def call_trip_mgr(lambda_client, payload):
    """
    Calls the trip_mgr lambda with the given payload.

    :param lambda_client: The lambda client.
    :type lambda_client: boto3.client
    :param payload: Payload to send to the lambda.
    :type payload: dict
    :return: The response payload from the lambda with any other details abstracted away.
    :rtype: dict

    :raises HTTPException: With status code 502 if the lambda fails unexpectedly.
    """

    lambda_response = lambda_client.invoke(
        FunctionName=os.getenv('TRIP_MGR_ARN'),
        InvocationType='RequestResponse',
        Payload=payload
    )

    return handle_lambda_response(lambda_response)


def convert_unix_to_datetime(unix_time):
    """
    Takes the unix time and converts it into the format desired by the weather api.

    :param unix_time: The unix time to convert.
    :type unix_time: int
    :return: The unix time converted to the desired format.
    :rtype: str
    """
    return datetime.utcfromtimestamp(unix_time).strftime('%Y-%m-%d:%H')


def get_secrets(region_name):
    """
    Sets the environment variables `WEATHER_API_KEY` & `IMAGE_API_KEY`, so that they can be used
    on the external api managers.

    :param region_name: The region the secrets are located in.
    :type region_name: str

    :return: None
    """

    secret_name = "cloudCourseWork"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secrets = json.loads(get_secret_value_response['SecretString'])

    os.environ['WEATHER_API_KEY'] = secrets['WEATHER_API_KEY']
    os.environ['IMAGE_API_KEY'] = secrets['IMAGE_API_KEY']
