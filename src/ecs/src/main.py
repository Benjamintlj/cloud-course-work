from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette.requests import Request
import boto3
from .account_mgr import account_mgr
from .trip_mgr import trip_mgr
from .weather_mgr import weather_mgr
from .image_mgr import image_mgr
from .utils import get_secrets, send_message_to_sqs
from .health import health

region_name = 'eu-west-1'

# Get secrets
get_secrets(region_name)

# Create client
lambda_client = boto3.client('lambda', region_name=region_name)

# Init the app
app = FastAPI()


# Specify handlers
@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exception: HTTPException):
    print('about to send')
    send_message_to_sqs(request, exception)
    print('sent')
    return JSONResponse(
        status_code=exception.status_code,
        content={"detail": exception.detail},
    )

# Set endpoints
health(app)

account_mgr(app, lambda_client)

trip_mgr(app, lambda_client)

weather_mgr(app, lambda_client)

image_mgr(app, lambda_client)
