import os
import logging
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from file_cache import FileHeuristicCache


class DuplicateSearch:

    def __init__(self, config, queue, searchpath):
        """
        Construct instance to find and store results of search
        :param search path
        """
        self.max_workers = int(config.get('Engine', 'threads', fallback='1'))
        self.searchpath = searchpath
        self._queue = queue

    def __str__(self):
        return "<#%s#>" % self.searchpath

    def __repr__(self):
        return str(self)


class FileEngine:

    def __init__(self, searchpath, queue):
        self.searchpath = searchpath
        self._queue = queue

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

    def do(self, callback) -> dict:
        """
        Construct a list of FileHeuristicCache instances to be created
        asynchronously through ThreadPoolExecutor
        :return list of scheduled tasks, as Futures
        """
        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            tasks = {ex.submit(FileHeuristicCache, f): f for f in self.files()}
            logging.info('Scheduling %d tasks with %d threads'
                         % (len(tasks), self.max_workers))
            for future in as_completed(tasks):
                try:
                    result = future.result()
                except Exception as e:
                    logging.info('Exception! %s' % (e))
                else:

                    callback(result)

        return tasks

    def handle(self, result):

        self._queue.put(result)
