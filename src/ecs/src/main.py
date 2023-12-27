from fastapi import FastAPI
import boto3
from .account_mgr import account_mgr
from .trip_mgr import trip_mgr
from .weather_mgr import weather_mgr
from .auth_token_mgr import AuthTokenMgr

app = FastAPI()

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

account_mgr(app, lambda_client)

trip_mgr(app, lambda_client)

weather_mgr(app, lambda_client)
