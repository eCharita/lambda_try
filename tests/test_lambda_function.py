import os
import lambda_function.lambda_function as lambda_function

def test_valid_update(setup_table):
    event = {'id': '123', 'value': 'TestValue'}
    context = {}
    response = lambda_function.lambda_handler(event, context)

    assert response['statusCode'] == 200
    item = setup_table.get_item(Key={'id': '123'})['Item']
    assert item['info'] == 'TestValue'

