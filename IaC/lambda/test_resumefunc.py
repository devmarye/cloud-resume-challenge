import unittest
from moto import mock_aws
import boto3
from resumefunc import lambda_handler

@mock_aws
class TestLambda(unittest.TestCase):
    def setUp(self):
        # Create mock DynamoDB table
        self.dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        self.table = self.dynamodb.create_table(
            TableName="MyResumeViewCount",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1}
        )
        self.table.put_item(Item={"id": "views", "count": 0})

    def test_get_method_returns_status_200(self):
        event = {"httpMethod": "GET"}
        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("views", response["body"])

    def test_invalid_method_returns_400(self):
        event = {"httpMethod": "POST"}
        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 400)

if __name__ == "__main__":
    unittest.main()
