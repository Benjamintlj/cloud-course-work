import pytest
from unittest.mock import Mock
import boto3
import os


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    boto3.setup_default_session(aws_access_key_id="testing", aws_secret_access_key="testing",
                                aws_session_token="testing")


# set environment variables
@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv('DYNAMO_TABLE', 'test_table')


@pytest.fixture(scope="function")
def lambda_context():
    """Mocked Lambda context."""
    return Mock()