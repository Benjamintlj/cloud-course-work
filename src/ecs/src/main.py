from fastapi import FastAPI
import boto3
import os
import json

app = FastAPI()


@app.get('/')
def home():
    # Get the ARNs
    trip_mgr_arn = os.getenv('TRIP_MGR_ARN')
    if not trip_mgr_arn:
        return {'error': "TRIP_MGR_ARN environment variable not set."}

    # Create the boto3 clients
    try:
        lambda_client = boto3.client('lambda', region_name='eu-west-1')
    except Exception as e:
        return {'error': "Error initializing boto3 client: " + str(e)}

    try:
        payload = {"message": "hi lambda"}
        json_payload = json.dumps(payload)

        # Invoke the trip_mgr
        response = lambda_client.invoke(
            FunctionName=trip_mgr_arn,
            InvocationType='RequestResponse',
            Payload=json_payload
        )

        response_payload = response['Payload'].read()
        return {'message': response_payload}

    except Exception as e:
        return {'error': str(e)}
