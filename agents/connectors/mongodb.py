import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class MongoDBConnector:
    """MongoDB connector for storing running history and operations."""

    def __init__(self):
        """Initialize MongoDB connection."""
        self.connection_string = os.getenv(
            "MONGODB_URI", "mongodb://localhost:27017/"
        )
        self.database_name = os.getenv("MONGODB_DATABASE", "polymarket_agent")
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self._connect()

    def _connect(self) -> None:
        """Establish connection to MongoDB."""
        try:
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,
            )
            # Test connection
            self.client.server_info()
            self.db = self.client[self.database_name]
            logger.info(f"Connected to MongoDB: {self.database_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            logger.warning("MongoDB operations will be disabled")
            self.client = None
            self.db = None

    def is_connected(self) -> bool:
        """Check if MongoDB is connected."""
        if self.client is None:
            return False
        try:
            self.client.server_info()
            return True
        except Exception:
            return False

    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """Get a MongoDB collection."""
        if not self.is_connected():
            return None
        return self.db[collection_name]

    def insert_one(
        self, collection_name: str, document: Dict[str, Any]
    ) -> Optional[str]:
        """Insert a single document into a collection."""
        collection = self.get_collection(collection_name)
        if collection is None:
            logger.warning(f"MongoDB not connected, skipping insert to {collection_name}")
            return None
        try:
            # Add timestamp if not present
            if "timestamp" not in document:
                document["timestamp"] = datetime.utcnow()
            result = collection.insert_one(document)
            logger.debug(f"Inserted document into {collection_name}: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting document into {collection_name}: {e}")
            return None

    def insert_many(
        self, collection_name: str, documents: List[Dict[str, Any]]
    ) -> Optional[List[str]]:
        """Insert multiple documents into a collection."""
        collection = self.get_collection(collection_name)
        if collection is None:
            logger.warning(f"MongoDB not connected, skipping insert to {collection_name}")
            return None
        try:
            # Add timestamp to each document if not present
            for doc in documents:
                if "timestamp" not in doc:
                    doc["timestamp"] = datetime.utcnow()
            result = collection.insert_many(documents)
            logger.debug(f"Inserted {len(result.inserted_ids)} documents into {collection_name}")
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            logger.error(f"Error inserting documents into {collection_name}: {e}")
            return None

    def find(
        self,
        collection_name: str,
        filter: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        sort: Optional[List[tuple]] = None,
    ) -> List[Dict[str, Any]]:
        """Find documents in a collection."""
        collection = self.get_collection(collection_name)
        if collection is None:
            logger.warning(f"MongoDB not connected, cannot query {collection_name}")
            return []
        try:
            query = collection.find(filter or {})
            if sort:
                query = query.sort(sort)
            if limit:
                query = query.limit(limit)
            return list(query)
        except Exception as e:
            logger.error(f"Error querying {collection_name}: {e}")
            return []

    def find_one(
        self, collection_name: str, filter: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Find a single document in a collection."""
        collection = self.get_collection(collection_name)
        if collection is None:
            logger.warning(f"MongoDB not connected, cannot query {collection_name}")
            return None
        try:
            return collection.find_one(filter or {})
        except Exception as e:
            logger.error(f"Error querying {collection_name}: {e}")
            return None

    def update_one(
        self,
        collection_name: str,
        filter: Dict[str, Any],
        update: Dict[str, Any],
    ) -> bool:
        """Update a single document in a collection."""
        collection = self.get_collection(collection_name)
        if collection is None:
            logger.warning(f"MongoDB not connected, cannot update {collection_name}")
            return False
        try:
            # Add update timestamp
            if "$set" in update:
                update["$set"]["updated_at"] = datetime.utcnow()
            else:
                update["$set"] = {"updated_at": datetime.utcnow()}
            result = collection.update_one(filter, update)
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating document in {collection_name}: {e}")
            return False

    def close(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Global instance
_mongodb_instance: Optional[MongoDBConnector] = None


def get_mongodb() -> MongoDBConnector:
    """Get or create MongoDB connector instance."""
    global _mongodb_instance
    if _mongodb_instance is None:
        _mongodb_instance = MongoDBConnector()
    return _mongodb_instance
