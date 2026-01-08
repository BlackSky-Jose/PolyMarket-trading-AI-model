"""
Test that all imports work correctly.
"""
import unittest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestImports(unittest.TestCase):
    """Test that all critical imports work."""

    def test_mongodb_connector_import(self):
        """Test MongoDB connector import."""
        try:
            from agents.connectors.mongodb import MongoDBConnector, get_mongodb
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import MongoDBConnector: {e}")

    def test_history_logger_import(self):
        """Test history logger import."""
        try:
            from agents.utils.history import HistoryLogger, get_history_logger
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import HistoryLogger: {e}")

    def test_polymarket_import(self):
        """Test Polymarket import."""
        try:
            from agents.polymarket.polymarket import Polymarket
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import Polymarket: {e}")

    def test_executor_import(self):
        """Test Executor import."""
        try:
            from agents.application.executor import Executor
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import Executor: {e}")

    def test_trader_import(self):
        """Test Trader import."""
        try:
            from agents.application.trade import Trader
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import Trader: {e}")

    def test_creator_import(self):
        """Test Creator import."""
        try:
            from agents.application.creator import Creator
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import Creator: {e}")

    def test_cli_import(self):
        """Test CLI import."""
        try:
            from scripts.python.cli import app
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import CLI app: {e}")

    def test_pymongo_available(self):
        """Test that pymongo is available."""
        try:
            import pymongo
            self.assertTrue(True)
        except ImportError:
            self.fail("pymongo is not installed. Run: pip install pymongo")


if __name__ == "__main__":
    unittest.main()
