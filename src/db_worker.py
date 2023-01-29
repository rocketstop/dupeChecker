from db_client import MongoHashClient


class DbWorker:

    def __init__(self, name: str, config, queue):
        self.name = name
        self._queue = queue
        self._db_client: MongoHashClient = MongoHashClient(
            config.get('Database', 'connection', fallback='mongodb://localhost:27017'),
            config.get('Database', 'database_name', fallback='hash_database')
        )

    async def work(self):
        while True:
            result = await self._queue.get()
            self._db_client.add_document(result)

            self._queue.task_done()
