from typing import Optional, Dict, Any, List
from datetime import datetime
from pymongo import MongoClient, UpdateOne
from ...core.config import settings

COLLECTION_NAME = "editais_canon"


class MongoCanonService:
    _client: Optional[MongoClient] = None

    @staticmethod
    def _collection():
        if MongoCanonService._client is None:
            MongoCanonService._client = MongoClient(settings.MONGO_URI)
        db = MongoCanonService._client[settings.MONGO_DB]
        return db[COLLECTION_NAME]

    @staticmethod
    def get_by_edital_id(edital_id: str) -> Optional[Dict[str, Any]]:
        col = MongoCanonService._collection()
        return col.find_one({"edital_id": edital_id})

    @staticmethod
    def touch_last_seen(edital_id: str) -> None:
        col = MongoCanonService._collection()
        col.update_one(
            {"edital_id": edital_id},
            {"$set": {"last_seen_at": datetime.utcnow()}},
        )

    @staticmethod
    def upsert_canonical(
        *,
        edital_id: str,
        json_final: Dict[str, Any],
        status: str,
        source_url: str,
        download_url: str,
        content_sha256: str,
        chunk_ids: List[str],
        provenance: Dict[str, Any],
        is_update: bool,
    ) -> None:
        col = MongoCanonService._collection()
        now = datetime.utcnow()
        existing = col.find_one({"edital_id": edital_id})
        history_entry = {
            "content_sha256": content_sha256,
            "timestamp": now,
        }
        if existing:
            # Maintain minimal history of hashes
            hashes = existing.get("hash_history", [])
            if not hashes or hashes[-1].get("content_sha256") != content_sha256:
                hashes.append(history_entry)
            update = {
                "$set": {
                    "json_final": json_final,
                    "status": status,
                    "source_url": source_url,
                    "download_url": download_url,
                    "content_sha256": content_sha256,
                    "chunk_ids": chunk_ids,
                    "provenance": provenance,
                    "last_seen_at": now,
                },
                "$setOnInsert": {"first_seen_at": existing.get("first_seen_at", now)},
                "$push": {"hash_history": {"$each": [history_entry], "$slice": -10}},
            }
            col.update_one({"edital_id": edital_id}, update, upsert=True)
        else:
            doc = {
                "edital_id": edital_id,
                "json_final": json_final,
                "status": status,
                "source_url": source_url,
                "download_url": download_url,
                "content_sha256": content_sha256,
                "first_seen_at": now,
                "last_seen_at": now,
                "chunk_ids": chunk_ids,
                "provenance": provenance,
                "hash_history": [history_entry],
            }
            col.insert_one(doc)
