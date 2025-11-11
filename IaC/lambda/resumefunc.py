import json
import boto3
import os
from decimal import Decimal
from botocore.exceptions import ClientError

# Helper for decimals
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    print("Received Event:", json.dumps(event, indent=2))
    
    http_method = event.get("httpMethod", "")
    table_name = os.environ.get("TABLE_NAME", "MyResumeViewCount")

    # 👇 Move boto3 initialization INSIDE the function (so Moto can patch it)
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.Table(table_name)

    try:
        if http_method == "GET":
            # Try to get existing record
            item = table.get_item(Key={'id': 'views'}).get('Item', {'id': 'views', 'count': 0})
            new_count = item['count'] + 1
            table.put_item(Item={'id': 'views', 'count': new_count})

            return {
                'statusCode': 200,
                'body': json.dumps({'views': new_count}, default=decimal_default)
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
