import json
import pytest
from unittest.mock import patch, MagicMock
from lambda_function import filter_asistance

@pytest.fixture
def fake_event():
    return {
        "body": json.dumps({
            "startDate": "2023-01-01",
            "endDate": "2023-01-31"
        }),
        "requestContext": {
            "http": {"method": "POST"},
            "authorizer": {
                "jwt": {
                    "claims": {
                        "cognito:groups": "[testcompany]"
                    }
                }
            }
        },
        "stageVariables": {
            "table": "testcompany"
        }
    }

@pytest.fixture
def fake_context():
    class Context:
        def get_remaining_time_in_millis(self):
            return 5000
    return Context()

@patch("lambda_function.filter_asistance.dynamodb")
def test_lambda_handler_success(mock_dynamodb, fake_event, fake_context):
    # Mock table scan results
    mock_table = MagicMock()
    mock_person_table = MagicMock()

    # Mocked visit entries (from sheet_assistance_testcompany)
    mock_table.scan.return_value = {
        "Items": [
            {"personid": "p1", "employeeid": "e1", "date": "2023-01-15"}
        ]
    }

    # Mocked personal_assistance_testcompany entries
    mock_person_table.scan.return_value = {
        "Items": [
            {"find": "p1", "name": "John", "area": "Client"},
            {"find": "e1", "name": "Anna", "area": "Assistant"}
        ]
    }

    # Set return values for mocked DynamoDB resource
    mock_dynamodb.Table.side_effect = [mock_table, mock_person_table]

    response = filter_asistance.lambda_handler(fake_event, fake_context)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert len(body) == 1
    assert body[0]["person"]["name"] == "John"
    assert body[0]["employee"]["name"] == "Anna"
