import os

def lambda_handler(event, context):
    #table_name = os.environ.get('TABLE_NAME')
    #dynamodb = boto3.resource('dynamodb')
    #table = dynamodb.Table(table_name)

    #item_id = event.get('id')
    #value = event.get('value')

    item_id = "123"  # Example item ID
    value = "TestValue"  # Example value

    if not item_id or not value:
        return {"statusCode": 400, "body": "Missing id or value"}

    #table.put_item(Item={'id': item_id, 'info': value})

    return {"statusCode": 200, "body": f"Item {item_id} updated"}
