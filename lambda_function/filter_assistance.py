import json
import boto3
from boto3.dynamodb.conditions import Attr
import logging
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')

TABLE_NAME_STRUCTURE = "sheet_assistance_"
TABLE_NAME_PERSONA_STUCTURE = "personal_assistance_"

def findCompanyForUser(stageVariable, nameOfGroup):
    company = nameOfGroup
    if(stageVariable is not None):
        company = stageVariable
    return company
    
def merge_visit_with_client_name(visit, name):
    # Create a dictionary to map ids to names
    id_to_name = {item["find"]: item for item in name}
    
    # Merge visit list with names
    merged_list = [{"person": id_to_name[visit_item["personid"]], **visit_item} for visit_item in visit]
    
    return merged_list
    
def merge_visit_with_assist_name(visit, name):
    # Create a dictionary to map ids to names
    id_to_name = {item["find"]: item for item in name}
    
    # Merge visit list with names
    merged_list = [{"employee": id_to_name[visit_item["employeeid"]], **visit_item} for visit_item in visit]
    
    return merged_list

def lambda_handler(event, context):
    # Initialize a logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    response = ""
    httpMethod = event.get("requestContext").get("http").get("method")
    print(httpMethod)
    initial_remaining_time = context.get_remaining_time_in_millis() / 1000  # Convert to seconds
    logger.info("Initial remaining time: %.2f seconds", initial_remaining_time)

    stageVariable = None
    if "stageVariables" in event:
        stageVariable = event.get("stageVariables").get("table")
        print("stageVariable " + stageVariable)
    
    company = findCompanyForUser(stageVariable, event.get("requestContext").get("authorizer").get("jwt").get("claims").get("cognito:groups")[1:-1])

    tableName = TABLE_NAME_STRUCTURE + company
    table = dynamodb.Table(tableName)
    print("get sheet table")
    
    tablePersonName = TABLE_NAME_PERSONA_STUCTURE + company
    tablePerson = dynamodb.Table(tablePersonName)
    print("get person name")

    jsonBody = json.loads(event.get("body"))
    startDate = jsonBody.get("startDate")
    endDate = jsonBody.get("endDate")
    print("get json data " + startDate + " " + endDate)
    print(table)
    try:
        data = table.scan(
            FilterExpression=Attr('date').between(startDate, endDate)
            )
        logger.info("Scan successful. Items: %s", data.get("Items"))
    except ClientError as e:
        logger.info("DynamoDB scan failed. Error: %s", e.data['Error']['Message'])
    except Exception as e:
        # Catch-all for other potential Python errors
        logger.info("An unexpected error occurred: %s", str(e))
    
    if len(data["Items"]) == 0 :
        return {
                'statusCode': 200,
                'body': json.dumps([])
        }
    
        
    # dataPersonalClient = tablePerson.scan(
    #     FilterExpression=Attr("area").eq("Client")
    # )
    # print("client")
    
    # dataPersonalAssist = tablePerson.scan(
    #     FilterExpression=Attr("area").eq("Assistant")
    # )

    dataPersonal  = tablePerson.scan(
        FilterExpression=Attr("area").eq("Client") | Attr("area").eq("Assistant")
    )
    clientData = [item for item in dataPersonal['Items'] if item.get("area") == "Client"]
    assistData = [item for item in dataPersonal['Items'] if item.get("area") == "Assistant"]
    # print(clientData)
    
    print("get Client and assist data")
    output = merge_visit_with_client_name(data["Items"], clientData)
    output2 = merge_visit_with_assist_name(output, assistData)
    print("after merge")
    
    return {
        'statusCode': 200,
        'body': json.dumps(output2)
    }
