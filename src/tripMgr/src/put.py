

def put(event, table):
    pk = event['pk']
    sk = event['sk']
    name = event['name']

    table.put_item(Item={
        'pk': pk,
        'sk': sk,
        'name': name
    })

    return {
        'statusCode': 200
    }