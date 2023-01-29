from typing import Any, List

import pymongo


class MongoHashClient:

    def __init__(self, connection_string: str, hash_database: str):
        self._db_client = pymongo.MongoClient(connection_string)

        self._db = self._db_client[hash_database]
        self._collection = self._db["file_hashes"]

    def add_document(self, document: dict) -> Any:
        if self._collection is not None:
            r = self._collection.insert_one(document)
            return r.inserted_id

    def add_documents(self, documents: List[dict]) -> List[Any]:
        if self._collection is not None:
            r = self._collection.insert_many(documents)
            return r.inserted_ids

    def find_by_id(self, id: str):
        if self._collection is not None:
            r = self._collection.find_one({"_id": id})
            return r

    def find_by_hash(self, hash: str):
        if self._collection is not None:
            docs = self._collection.find({"file_hash": hash})
            return docs

    def find_duplicate_hashes(self):
        if self._collection is not None:
            duplicates = self._collection.aggregate(
                [
                    {"$match": {"file_hash": {"$ne": None}}},
                    {"$group": {"_id": "$file_hash", "files": {"$addToSet": "$filename"}, "count": {"$sum": 1}}},
                    {"$match": {"count": {"$gt": 1}}},
                    {"$project": {"file_hash": "$_id", "_id": 0, "count": 1, "files": 1}}
                ]
            )
            return duplicates


def test():
    client: MongoHashClient = MongoHashClient("mongodb://lettuce:27017", "hash_database")

    client.add_document({"file_hash": "abcdef", "file": "hello.txt"})
    client.add_document({"file_hash": "kkjlislkjj", "file": "test.txt"})
    client.add_document({"file_hash": "abcdef", "file": "backups/hello.txt"})

    matches = client.find_by_hash("abcdef")

    for m in matches:
        print(m)

    duplicates = client.find_duplicate_hashes()

    for d in duplicates:
        print(d)


if __name__ == "__main__":
    test()








