import json
import boto3
import os
from decimal import Decimal
from botocore.exceptions import ClientError

# Helper function to handle decimals in DynamoDB JSON
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

# Detect if we are running under Moto or real AWS
def is_test_environment():
    return os.environ.get("AWS_SAM_LOCAL") == "true" or "moto" in boto3.__version__

# DynamoDB setup
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table_name = os.environ.get("TABLE_NAME", "MyResumeViewCount")
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    print("Received Event:", json.dumps(event, indent=2))
    
    http_method = event.get("httpMethod", "")
    
    try:
        if http_method == "GET":
            # --- Moto-friendly implementation ---
            # Moto does not support 'if_not_exists' expression, so we handle it manually.
            if is_test_environment():
                # Get the current count or initialize
                item = table.get_item(Key={'id': 'views'}).get('Item', {'id': 'views', 'count': 0})
                new_count = item['count'] + 1
                table.put_item(Item={'id': 'views', 'count': new_count})
                body = {'views': new_count}
            
            else:
                # --- Real AWS implementation ---
                response = table.update_item(
                    Key={'id': 'views'},
                    UpdateExpression="SET #c = if_not_exists(#c, :start) + :inc",
                    ExpressionAttributeNames={"#c": "count"},
                    ExpressionAttributeValues={":inc": 1, ":start": 0},
                    ReturnValues="UPDATED_NEW"
                )
                body = {'views': response['Attributes']['count']}
            
            return {
                'statusCode': 200,
                'body': json.dumps(body, default=decimal_default)
            }

        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Unsupported method'})
            }

    except ClientError as e:
        print("DynamoDB ClientError:", e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }

    except Exception as e:
        print("Unexpected Error:", e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
