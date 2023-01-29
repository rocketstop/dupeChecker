import os
import logging
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from file_cache import FileHeuristicCache
from db_client import MongoHashClient


class DuplicateSearch:

    def __init__(self, config, path):
        """
        Construct instance to find and store results of search
        :param search path
        """
        self.max_workers = int(config.get('Engine', 'threads', fallback='1'))
        self.searchpath = path
        self.filecount = 0
        self.dupecount = 0
        # hashlist of all files and hashes
        self.filehash = dict()
        # set of all unique files
        self.uniques = set()
        # set of all duplicate files
        self.dupes = set()
        self.db_client: MongoHashClient = MongoHashClient(
            config.get('Database', 'connection', fallback='mongodb://localhost:27017'),
            config.get('Database', 'database_name', fallback='hash_database')
        )

    def __str__(self):
        return "<#%s#>" % self.searchpath

    def __repr__(self):
        return str(self)

    def show_dupes(self):
        for d in self.dupes:
            logging.info(str(self.filehash[d]))

    def report(self):
        # logging.info(str(self.uniques))
        logging.info('Total file count: ' + str(self.filecount))
        logging.info('Total dupe count: ' + str(self.dupecount))
        logging.info('Total unique file count: ' + str(len(self.uniques)))

    def files(self):
        """
        Filename generator, returns all files found
        at DuplicateSearch path
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

        self.filecount += 1  # sanity check

        self.db_client.add_document({"filename": result.filename, "file_hash": result.hash})

        if result in self.uniques:
            logging.debug('Dupe! - %s' % result.filename)
            logging.debug('Dupe! Hash - %s' % str(result.hash))
            logging.debug('Found: %s' % str(self.filehash[result.hash]))
            (self.filehash[result.hash]).append(result)
            self.dupes.add(result.hash)
            self.dupecount += 1
        else:
            self.filehash[result.hash] = [result]
            self.uniques.add(result)
            logging.debug('New file: %s' % result.filename)
            logging.debug('Adding to hash with key %s' % str(result.hash))