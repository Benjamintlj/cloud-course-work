import boto3


def main(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello World!'
    }