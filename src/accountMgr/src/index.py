from .put import put
import boto3


def main(event, context):
    # create dynamodb resource
    DYNAMO_TABLE = os.environ['DYNAMO_TABLE']
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DYNAMO_TABLE)

    http_method = event['httpMethod']

    response = None

    if http_method == 'PUT':
        response = put(event, table)

    return response if response else {
        'statusCode': 400,
        'body': 'Bad Request'
    }