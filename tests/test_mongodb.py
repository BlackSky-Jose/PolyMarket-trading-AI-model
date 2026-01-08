"""
Tests for MongoDB connector and history logging.
"""
import unittest
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from agents.connectors.mongodb import MongoDBConnector, get_mongodb
from agents.utils.history import HistoryLogger, get_history_logger


class TestMongoDBConnector(unittest.TestCase):
    """Test MongoDB connector functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock environment variables
        self.env_patcher = patch.dict(
            os.environ,
            {
                "MONGODB_URI": "mongodb://localhost:27017/",
                "MONGODB_DATABASE": "test_polymarket_agent",
            },
        )
        self.env_patcher.start()

    def tearDown(self):
        """Clean up after tests."""
        self.env_patcher.stop()

    @patch("agents.connectors.mongodb.MongoClient")
    def test_mongodb_connection_success(self, mock_mongo_client):
        """Test successful MongoDB connection."""
        mock_client = MagicMock()
        mock_client.server_info.return_value = {"version": "6.0.0"}
        mock_mongo_client.return_value = mock_client

        connector = MongoDBConnector()
        self.assertTrue(connector.is_connected())
        mock_mongo_client.assert_called_once()

    @patch("agents.connectors.mongodb.MongoClient")
    def test_mongodb_connection_failure(self, mock_mongo_client):
        """Test MongoDB connection failure handling."""
        mock_mongo_client.side_effect = Exception("Connection failed")

        connector = MongoDBConnector()
        self.assertFalse(connector.is_connected())
        self.assertIsNone(connector.db)

    @patch("agents.connectors.mongodb.MongoClient")
    def test_insert_one_success(self, mock_mongo_client):
        """Test successful document insertion."""
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_result = MagicMock()
        mock_result.inserted_id = "test_id_123"
        mock_collection.insert_one.return_value = mock_result
        mock_client.server_info.return_value = {"version": "6.0.0"}
        mock_client.__getitem__.return_value = mock_collection
        mock_mongo_client.return_value = mock_client

        connector = MongoDBConnector()
        result = connector.insert_one("test_collection", {"test": "data"})

        self.assertEqual(result, "test_id_123")
        mock_collection.insert_one.assert_called_once()

    @patch("agents.connectors.mongodb.MongoClient")
    def test_insert_one_without_connection(self, mock_mongo_client):
        """Test insert when MongoDB is not connected."""
        mock_mongo_client.side_effect = Exception("Connection failed")

        connector = MongoDBConnector()
        result = connector.insert_one("test_collection", {"test": "data"})

        self.assertIsNone(result)

    @patch("agents.connectors.mongodb.MongoClient")
    def test_find_documents(self, mock_mongo_client):
        """Test finding documents."""
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.find.return_value = [
            {"_id": "1", "test": "data1"},
            {"_id": "2", "test": "data2"},
        ]
        mock_client.server_info.return_value = {"version": "6.0.0"}
        mock_client.__getitem__.return_value = mock_collection
        mock_mongo_client.return_value = mock_client

        connector = MongoDBConnector()
        results = connector.find("test_collection", limit=10)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["test"], "data1")


class TestHistoryLogger(unittest.TestCase):
    """Test history logging functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.env_patcher = patch.dict(
            os.environ,
            {
                "MONGODB_URI": "mongodb://localhost:27017/",
                "MONGODB_DATABASE": "test_polymarket_agent",
            },
        )
        self.env_patcher.start()

    def tearDown(self):
        """Clean up after tests."""
        self.env_patcher.stop()

    @patch("agents.utils.history.get_mongodb")
    def test_log_cli_command(self, mock_get_mongodb):
        """Test logging CLI command."""
        mock_mongodb = MagicMock()
        mock_mongodb.insert_one.return_value = "test_id"
        mock_get_mongodb.return_value = mock_mongodb

        logger = HistoryLogger()
        result = logger.log_cli_command(
            command="test_command",
            parameters={"param1": "value1"},
            success=True,
        )

        self.assertEqual(result, "test_id")
        mock_mongodb.insert_one.assert_called_once()
        call_args = mock_mongodb.insert_one.call_args
        self.assertEqual(call_args[0][0], "cli_history")
        self.assertEqual(call_args[0][1]["command"], "test_command")

    @patch("agents.utils.history.get_mongodb")
    def test_log_trade_operation(self, mock_get_mongodb):
        """Test logging trade operation."""
        mock_mongodb = MagicMock()
        mock_mongodb.insert_one.return_value = "trade_id"
        mock_get_mongodb.return_value = mock_mongodb

        logger = HistoryLogger()
        result = logger.log_trade_operation(
            operation_type="one_best_trade",
            events_count=10,
            markets_count=5,
            success=True,
        )

        self.assertEqual(result, "trade_id")
        call_args = mock_mongodb.insert_one.call_args
        self.assertEqual(call_args[0][0], "trade_history")
        self.assertEqual(call_args[0][1]["operation_type"], "one_best_trade")

    @patch("agents.utils.history.get_mongodb")
    def test_log_llm_query(self, mock_get_mongodb):
        """Test logging LLM query."""
        mock_mongodb = MagicMock()
        mock_mongodb.insert_one.return_value = "llm_id"
        mock_get_mongodb.return_value = mock_mongodb

        logger = HistoryLogger()
        result = logger.log_llm_query(
            query_type="ask_llm",
            user_input="test question",
            response="test response",
            success=True,
        )

        self.assertEqual(result, "llm_id")
        call_args = mock_mongodb.insert_one.call_args
        self.assertEqual(call_args[0][0], "llm_history")
        self.assertEqual(call_args[0][1]["query_type"], "ask_llm")

    @patch("agents.utils.history.get_mongodb")
    def test_log_market_query(self, mock_get_mongodb):
        """Test logging market query."""
        mock_mongodb = MagicMock()
        mock_mongodb.insert_one.return_value = "market_id"
        mock_get_mongodb.return_value = mock_mongodb

        logger = HistoryLogger()
        result = logger.log_market_query(
            query_type="get_all_markets",
            limit=10,
            results_count=5,
            success=True,
        )

        self.assertEqual(result, "market_id")
        call_args = mock_mongodb.insert_one.call_args
        self.assertEqual(call_args[0][0], "market_query_history")

    @patch("agents.utils.history.get_mongodb")
    def test_serialize_object(self, mock_get_mongodb):
        """Test object serialization."""
        mock_mongodb = MagicMock()
        mock_get_mongodb.return_value = mock_mongodb

        logger = HistoryLogger()

        # Test with dict
        result = logger._serialize_object({"key": "value"})
        self.assertEqual(result, {"key": "value"})

        # Test with list
        result = logger._serialize_object([1, 2, 3])
        self.assertEqual(result, [1, 2, 3])

        # Test with string
        result = logger._serialize_object("test")
        self.assertEqual(result, "test")


class TestHistoryLoggerIntegration(unittest.TestCase):
    """Integration tests for history logger with error handling."""

    @patch("agents.utils.history.get_mongodb")
    def test_log_with_error(self, mock_get_mongodb):
        """Test logging with error handling."""
        mock_mongodb = MagicMock()
        mock_mongodb.insert_one.return_value = None  # Simulate failure
        mock_get_mongodb.return_value = mock_mongodb

        logger = HistoryLogger()
        result = logger.log_cli_command(
            command="test",
            success=False,
            error="Test error",
        )

        # Should not raise exception even if insert fails
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
