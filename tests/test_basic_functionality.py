"""
Basic functionality tests that don't require external services.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import os


class TestBasicFunctionality(unittest.TestCase):
    """Test basic functionality without external dependencies."""

    @patch.dict(os.environ, {"MONGODB_URI": "mongodb://localhost:27017/"})
    def test_mongodb_connector_initialization(self):
        """Test MongoDB connector can be initialized."""
        from agents.connectors.mongodb import MongoDBConnector

        with patch("agents.connectors.mongodb.MongoClient") as mock_client:
            mock_client.return_value.server_info.return_value = {"version": "6.0.0"}
            connector = MongoDBConnector()
            self.assertIsNotNone(connector)

    @patch.dict(os.environ, {"MONGODB_URI": "mongodb://localhost:27017/"})
    def test_history_logger_initialization(self):
        """Test history logger can be initialized."""
        from agents.utils.history import HistoryLogger

        with patch("agents.utils.history.get_mongodb") as mock_get_mongodb:
            mock_mongodb = MagicMock()
            mock_get_mongodb.return_value = mock_mongodb
            logger = HistoryLogger()
            self.assertIsNotNone(logger)

    def test_history_logger_serialization(self):
        """Test object serialization in history logger."""
        from agents.utils.history import HistoryLogger

        with patch("agents.utils.history.get_mongodb"):
            logger = HistoryLogger()

            # Test various types
            self.assertEqual(logger._serialize_object("string"), "string")
            self.assertEqual(logger._serialize_object(123), 123)
            self.assertEqual(logger._serialize_object(True), True)
            self.assertEqual(logger._serialize_object(None), None)
            self.assertEqual(logger._serialize_object({"key": "value"}), {"key": "value"})
            self.assertEqual(logger._serialize_object([1, 2, 3]), [1, 2, 3])

    @patch.dict(os.environ, {"MONGODB_URI": "mongodb://localhost:27017/"})
    def test_get_mongodb_singleton(self):
        """Test get_mongodb returns singleton."""
        from agents.connectors.mongodb import get_mongodb

        with patch("agents.connectors.mongodb.MongoClient") as mock_client:
            mock_client.return_value.server_info.return_value = {"version": "6.0.0"}

            instance1 = get_mongodb()
            instance2 = get_mongodb()

            # Should be the same instance
            self.assertIs(instance1, instance2)

    @patch.dict(os.environ, {"MONGODB_URI": "mongodb://localhost:27017/"})
    def test_get_history_logger_singleton(self):
        """Test get_history_logger returns singleton."""
        from agents.utils.history import get_history_logger

        with patch("agents.utils.history.get_mongodb"):
            instance1 = get_history_logger()
            instance2 = get_history_logger()

            # Should be the same instance
            self.assertIs(instance1, instance2)


if __name__ == "__main__":
    unittest.main()
