

def get(event, table):
    pk = event['pk']
    sk = event['sk']

    response = table.get_item(Key={
        'pk': pk,
        'sk': sk
    })

    return {
        'statusCode': 200,
        'name': response['Item']['name']
    }