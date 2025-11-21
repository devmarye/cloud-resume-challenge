import json
import boto3
from moto import mock_aws
from resumefunc import lambda_handler



@mock_aws
def test_lambda_handler_get():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.create_table(
        TableName="MyResumeViewCount",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST"
    )

    
    table.put_item(Item={"id": "views", "count": 5})
    event = {
        "requestContext": {
            "http": {
                "method": "GET"
            }
        }
    }
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200

    body = json.loads(response["body"])
    assert "views" in body
    assert body["views"] == 6


@mock_aws
def test_invalid_method():

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    dynamodb.create_table(
        TableName="MyResumeViewCount",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST"
    )

    event = {
        "requestContext": {
            "http": {
                "method": "POST"
            }
        }
    }

    response = lambda_handler(event, None)

    assert response["statusCode"] == 400

@mock_aws
def test_lambda_handler_creates_item_if_missing():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    dynamodb.create_table(
        TableName="MyResumeViewCount",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST"
    )

    event = {
        "requestContext": {
            "http": {
                "method": "GET"
            }
        }
    }

    response = lambda_handler(event, None)

    assert response["statusCode"] == 200

    body = json.loads(response["body"])
    assert body["views"] == 1
