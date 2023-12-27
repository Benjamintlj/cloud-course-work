from fastapi import HTTPException
import os
import json
import logging
from datetime import datetime
import time
import boto3
from botocore.exceptions import ClientError


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


def convert_unix_to_datetime(unix_time):
    return datetime.utcfromtimestamp(unix_time).strftime('%Y-%m-%d:%H')


def convert_datetime_to_unix(dt):
    return int(time.mktime(dt.timetuple()))


def get_secrets():
    secret_name = "cloudCourseWork"
    region_name = "eu-west-1"

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
