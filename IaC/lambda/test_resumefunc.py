import unittest
from resumefunc import lambda_handler

class TestLambda(unittest.TestCase):
    def test_get_method_returns_status_200(self):
        event = {"httpMethod": "GET"}
        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 200)

    def test_invalid_method_returns_400(self):
        event = {"httpMethod": "POST"}
        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 400)

if __name__ == "__main__":
    unittest.main()

