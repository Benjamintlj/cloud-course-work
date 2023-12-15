import unittest
from src.utils import create_new_id
from unittest.mock import patch, MagicMock


class TestUtils(unittest.TestCase):
    @patch('random.randint')
    @patch('time.time')
    @patch('boto3.resource')
    def test_get_new_id(self, mock_boto3_resources, mock_time, mock_randint):
        mock_time.return_value = 1000000
        mock_randint.return_value = 1234
        mock_uuid = int(mock_time.return_value) * 10000 + mock_randint.return_value

        mock_dynamodb_table = MagicMock()
        mock_boto3_resources.Table.return_value = mock_dynamodb_table

        call_count = 0

        def check_item_exists(Key):
            nonlocal call_count
            call_count += 1
            if call_count == 1 and Key == {'trip_id': mock_uuid}:
                return {'Item': {'trip_id': mock_uuid}}
            else:
                return {}

        mock_dynamodb_table.get_item.side_effect = check_item_exists

        response = create_new_id(mock_dynamodb_table)

        self.assertEqual(response, mock_uuid)
        self.assertTrue(mock_dynamodb_table.get_item.called)
        self.assertGreater(mock_randint.call_count, 1)

    @patch('random.randint')
    @patch('time.time')
    @patch('boto3.resource')
    def test_create_new_id_failure(self, mock_boto3_resources, mock_time, mock_randint):
        mock_time.return_value = 1000000
        mock_randint.return_value = 1234

        mock_dynamodb_table = MagicMock()
        mock_boto3_resources.Table.return_value = mock_dynamodb_table

        # Setup mock_dynamodb_table.get_item to always return a response indicating that the item exists
        def always_exists(Key):
            return {'Item': {'trip_id': Key['trip_id']}}

        mock_dynamodb_table.get_item.side_effect = always_exists

        # Test that create_new_id raises an exception after 3 failed attempts
        with self.assertRaises(Exception) as context:
            create_new_id(mock_dynamodb_table)

        self.assertTrue("Failed to generate trips_id after 3 attempts" in str(context.exception))

        # Check that get_item was called exactly 3 times
        self.assertEqual(mock_dynamodb_table.get_item.call_count, 3)
