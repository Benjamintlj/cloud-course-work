import pytest
from moto import mock_sqs
from unittest.mock import Mock
import boto3


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    boto3.setup_default_session(aws_access_key_id="testing", aws_secret_access_key="testing",
                                aws_session_token="testing")


@pytest.fixture(scope="function")
def sqs(aws_credentials):
    with mock_sqs():
        sqs = boto3.client('sqs', region_name='eu-west-1')
        sqs.create_queue(QueueName='CloudCourseWorkTripMgrQueue')
        yield sqs


@pytest.fixture(scope="function")
def lambda_context():
    """Mocked Lambda context."""
    return Mock()