import pytest
import boto3
import src.main as main


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    boto3.setup_default_session(aws_access_key_id="testing", aws_secret_access_key="testing",
                                aws_session_token="testing")


# set environment variables
@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv('TRIP_MGR_ARN', 'lambda_arn')
