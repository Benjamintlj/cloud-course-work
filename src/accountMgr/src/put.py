

def put(event, table):
    response = None

    # TODO: pk must be a random number gotten from the api
    pk = event['username']
    sk = event['password']

    try:
        table.put_item(Item={
            'pk': pk,
            'sk': sk,
        })

        response = {
            'statusCode': 200,
            'body': 'User created successfully'
        }
    except Exception as e:
        response = {
            'statusCode': 500,
            'body': str(e)
        }

    return response