import asyncio
import os
import logging
from concurrent.futures import ThreadPoolExecutor, Future

from file_cache import FileHeuristicCache
from db_worker import DbWorker


class DuplicateSearch:

    def __init__(self, config, file_queue, hash_queue, searchpath):
        """
        Construct instance to find and store results of search
        :param config
        :param file_queue
        :param hash_queue
        :param searchpath
        """
        logging.info("creating duplicate search with searchpath: " + searchpath)
        self.max_workers = int(config.get('Engine', 'threads', fallback='1'))
        self._searchpath = searchpath
        self._file_queue = file_queue
        self._hash_queue = hash_queue
        self._config = config

    def __str__(self):
        return "<#%s#>" % self._searchpath

    def __repr__(self):
        return str(self)

    async def do(self):
        q_filename: asyncio.Queue[float] = asyncio.Queue(20)
        q_hash: asyncio.Queue[dict] = asyncio.Queue()

        tasks = []

        tasks.append(asyncio.create_task(FileProducer(self._searchpath, q_filename).do()))
        tasks.append(asyncio.create_task(FileHasher(q_filename, q_hash).do()))
        tasks.append(asyncio.create_task(DbWorker("hash_worker", self._config, q_hash).do()))

        await asyncio.gather(*tasks, return_exceptions=True)


class FileProducer:

    def __init__(self, searchpath, file_queue):
        logging.info("creating FileProducer with searchpath: " + searchpath)
        self.searchpath = searchpath
        self._file_queue = file_queue

    def files(self):
        """
        Filename generator, returns all files found at DuplicateSearch search path
        :return filename, generated
        """
        if os.path.exists(self.searchpath):
            logging.info('Found the search path: %s' % self.searchpath)

            for root, dirs, files in os.walk(self.searchpath):
                if not files:
                    continue
                for f in files:
                    yield os.path.join(root, f)
        else:
            logging.error("search path does not exist")

    async def do(self):
        """
        Construct a list of FileHeuristicCache instances to be created
        asynchronously through ThreadPoolExecutor
        :return list of scheduled tasks, as Futures
        """
        for f in self.files():
            logging.info("Putting filename: " + f)
            await self._file_queue.put(f)


class FileHasher:

    def __init__(self, file_queue, hash_queue):
        self._file_queue = file_queue
        self._hash_queue = hash_queue
        self._thread_pool = ThreadPoolExecutor(20)

    async def do(self):
        while True:
            filename: str = await self._file_queue.get()
            logging.info("Got filename for hashing: " + filename)
            f: Future = self._thread_pool.submit(FileHeuristicCache(filename))
            f.add_done_callback(self.handle)
            self._file_queue.task_done()

    async def handle(self, future: Future):

            result = future.result()
            logging.info("Hashing for filename complete: " + result.filename)
            await self._hash_queue.put({
                "file_hash": result.hash,
                "filename": result.filename
            })

