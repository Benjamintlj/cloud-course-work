from fastapi import FastAPI, Request, HTTPException
import boto3
import os
import json
import logging

app = FastAPI()


@app.get('/')
def get(pk: str, sk: int):

    try:
        # I don't like calling this multiple times, but it cannot be defined outside of this and be mocked
        lambda_client = boto3.client('lambda', region_name='eu-west-1')

        payload = json.dumps({
            'httpMethod': 'GET',
            'pk': pk,
            'sk': sk
        })

        # Invoke the trip_mgr
        response = lambda_client.invoke(
            FunctionName=os.getenv('TRIP_MGR_ARN'),
            InvocationType='RequestResponse',
            Payload=payload
        )
        logging.error(" invoked trip_mgr: " + str(response))

        response_payload = response['Payload'].read().decode('utf-8')
        response_payload = json.loads(response_payload)
        logging.error(" read trip_mgr: " + str(response_payload))

        return {
            'statusCode': 200,
            'body': {
                'name': response_payload['name']
            }
        }

    except Exception as e:
        logging.error(" invoking trip_mgr: " + str(e))
        return HTTPException(status_code=500, detail=str(e))
