from fastapi import FastAPI
import boto3
from .account_mgr import account_mgr
from .trip_mgr import trip_mgr
from .weather_mgr import weather_mgr
from .image_mgr import image_mgr
from .utils import get_secrets

region_name = 'eu-west-1'

# Get secrets
get_secrets(region_name)

# Create client
lambda_client = boto3.client('lambda', region_name=region_name)

# Init the app
app = FastAPI()

# Set endpoints
account_mgr(app, lambda_client)

trip_mgr(app, lambda_client)

weather_mgr(app, lambda_client)

image_mgr(app, lambda_client)
