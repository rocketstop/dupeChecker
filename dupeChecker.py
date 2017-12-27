#!/usr/bin/env python

import os
import sys
import uuid
import hashlib
import logging
import argparse
import ConfigParser

BASE_PATH = os.path.dirname(os.path.realpath(__file__))


def main(args, config, loglevel):

    # dictionary of file hashes
    fileHash = dict()
    # current count of all files found in path
    filecount = 0
    # set of the hashes of all duplicates
    dupes = set()

    logging.info("Specified search path: %s" % args.searchpath)

    if os.path.exists(args.searchpath):
        logging.info('Found the supplied filepath: %s' % args.searchpath)

    # mega-lists of components for all child paths of search path
    for root, dirs, files in os.walk(args.searchpath):
        if not files:
            continue

        for f in files:
            filecount += 1 # sanity check
            fn = os.path.join(root, f) # get full path
            hash = getHash(fn)
            if hash:
                if hash in fileHash.keys():
                    logging.info('Dupe!')
                    dupes.add(hash)
                    (fileHash[hash]).append(fn)
                else:
                    logging.info('New file: ' + fn)
                    fileHash[hash] = [fn]

        logging.info('Total file count: ' + str(filecount))
        logging.info('Total dupe count: ' + str(len(dupes)))

        for h in dupes:
            logging.info(fileHash[h])


def getHash(fn):
    """
    Calculate hash of file contents
    :param filename of file to hash
    :return string, hash value or None if file doesn't exist
    """
    hashMethod = hashlib.sha256()

    if (os.path.exists(fn)):
        hash = hash_bytestr_iter(
            file_as_blockiter(open(fn, 'rb')), hashMethod, True)
        return hash
    return None


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


def init_config():
    """
    Load configuration from config file
    :return config
    """
    config_logfilepath = os.path.join(BASE_PATH, 'dupeChecker.conf')

    if not os.path.exists(config_logfilepath):
        print 'Config file not found: %s' % config_logfilepath
        sys.exit(1)
    config = ConfigParser.SafeConfigParser()
    config.read(config_logfilepath)
    return config


def init_logging(config, loglevel):
    """
    Initialize basic logging functionality
    :param config
    :param loglevel
    """

    fmt = '%%(asctime)s [%s] %%(message)s' % str(uuid.uuid4())[:6]
    logfile = os.path.join(BASE_PATH, config.get('Logging', 'log-filename'))

    logging.basicConfig(level=loglevel,
                        format=fmt,
                        filename=logfile)

    console = logging.StreamHandler()
    console.setLevel(loglevel)
    formatter = logging.Formatter('%(message)s')
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

    loglevel = logging.DEBUG if args.verbose else logging.INFO

    init_logging(config, loglevel)

    main(args, config, loglevel)

# Todo : refactor for multiple filter types
# Todo : add filter for EXIF creation time
# Todo : add filter for similar filename (like suffix)
# Todo : Exclusions, leave some files/filetypes out
# Todo : database for duplicates?
# Todo : Parallelize?
