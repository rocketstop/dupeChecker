#!/usr/bin/env python

import os
import sys
import hashlib
import logging
import argparse
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from time import time
from configparser import ConfigParser


BASE_PATH = os.path.dirname(os.path.realpath(__file__))


class FileHeuristicCache:
    def __init__(self, fn):
        """
        Construct an object that stores file comparison heuristics.
        :param filename of file
        """
        self.fn = fn
        self.hash = self.getHash()

    def __eq__(self, other):
        if self.hash == other.hash:
            return bool(self.hash)
        return False

    def __str__(self):
        return "<#%s#>" % self.fn

    def __repr__(self):
        return str(self)

    def __hash__(self):
        if self.hash is None:
            # if we can't hash contents, fall back to filename
            return hash(self.fn)
        return hash(self.hash)

    def getHash(self):
        """
        Calculate hash of file contents
        :return string, hash value or None if file doesn't exist
        """
        hashMethod = hashlib.sha256()

        def hash_bytestr_iter(bytesiter, hasher, ashexstr=False):
            for block in bytesiter:
                hasher.update(block)
            return (hasher.hexdigest() if ashexstr else hasher.digest())

        def file_as_blockiter(afile, blocksize=65536):
            with afile:
                block = afile.read(blocksize)
                while len(block) > 0:
                    yield block
                    block = afile.read(blocksize)

        if (os.path.exists(self.fn)):
            hash = hash_bytestr_iter(
                file_as_blockiter(open(self.fn, 'rb')), hashMethod, True)
            logging.debug('Generating hash for: ' + str(self.fn))
            logging.debug('Hash ' + str(hash))
            return hash
        return None


class DuplicateSearch:

    def __init__(self, path):
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

    def __str__(self):
        return "<#%s#>" % self.fn

    def __repr__(self):
        return str(self)

    def show_dupes(self):
        for d in self.dupes:
            logging.info(str(self.filehash[d]))

    def report(self):
        logging.info(str(self.uniques))
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

    def do(self, callback):
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

        if result in self.uniques:
            logging.debug('Dupe! - %s' % result.fn)
            logging.debug('Dupe! Hash - %s' % str(result.hash))
            logging.debug('Found: %s' % str(self.filehash[result.hash]))
            (self.filehash[result.hash]).append(result)
            self.dupes.add(result.hash)
            self.dupecount += 1
        else:
            self.filehash[result.hash] = [result]
            self.uniques.add(result)
            logging.debug('New file: %s' % result.fn)
            logging.debug('Adding to hash with key %s' % str(result.hash))


def main(args, config, loglevel):

    start_time = time()
    search = DuplicateSearch(args.searchpath)
    logging.info("Specified search path: %s" % search.searchpath)

    search.do(search.handle)

    search.report()
    search.show_dupes()

    logging.info("Elapsed time: %f" % (time() - start_time))


def init_config():
    """
    Load configuration from config file
    :return config
    """
    config_logfilepath = os.path.join(BASE_PATH, 'dupeChecker.conf')

    if not os.path.exists(config_logfilepath):
        print('Config file not found: {}'.format(config_logfilepath))
        sys.exit(1)
    config = ConfigParser()
    config.read(config_logfilepath)
    return config


def init_logging(logfile="log.log", loglevel=logging.INFO):
    """
    Initialize basic logging functionality
    :param log filename
    :param loglevel
    """
    file_fmt = '%(asctime)s %(thread)d %(message)s'
    console_fmt = '%(message)s'

    if (loglevel == logging.DEBUG):
        console_fmt = file_fmt

    logging.basicConfig(level=loglevel,
                        format=file_fmt,
                        filename=logfile)

    console = logging.StreamHandler()
    console.setLevel(loglevel)
    formatter = logging.Formatter(console_fmt)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def init_parse_args():
    parser = argparse.ArgumentParser(
        description="Compares files in a given directory for \
                duplicates based on contents.",
        epilog="commandline like '%(prog)s @params.conf'.",
        fromfile_prefix_chars='@')

    parser.add_argument(
        "searchpath",
        help="supply path to check for duplicates",
        metavar="PATH")

    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true")

    arguments = parser.parse_args()
    return arguments


if __name__ == '__main__':

    config = init_config()
    args = init_parse_args()

    logfile = os.path.join(BASE_PATH, config.get('Logging', 'log-filename'))
    loglevel = logging.DEBUG if args.verbose else logging.INFO

    init_logging(logfile, loglevel)

    main(args, config, loglevel)

# Todo : add filter for EXIF creation time
# Todo : add filter for similar filename (like suffix)
# Todo : Exclusions, leave some files/filetypes out
# Todo : database for duplicates?
