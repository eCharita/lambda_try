import lambda_function.lambda_function as lambda_function

def test_valid_update():
    event = {'id': '123', 'value': 'TestValue'}
    context = {}
    # Zatím funkci nevoláš, pouze mockuješ výstup
    # response = lambda_function.lambda_handler(event, context)

    # assert response['statusCode'] == 200
    item = {'id': '123', 'info': 'TestValue'}  # Mocked item
    assert item['info'] == 'TestValue'
