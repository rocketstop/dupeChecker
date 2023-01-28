import os
import sys
import logging
import argparse
from configparser import ConfigParser
from time import time
from duplicate_search import DuplicateSearch

BASE_PATH: str = os.path.dirname(os.path.realpath(__file__))


def init_config():
    """
    Load configuration from config file
    :return config
    """
    config_file_path: str = os.path.join(BASE_PATH, '../dupeChecker.conf')

    if not os.path.exists(config_file_path):
        print('Config file not found: {}'.format(config_file_path))
        sys.exit(1)
    config = ConfigParser()
    config.read(config_file_path)
    return config


def init_logging(logfile="log.log", loglevel=logging.INFO):
    """
    Initialize basic logging functionality
    :param logfile log filename
    :param loglevel
    """
    log_fmt: str = '%(asctime)s %(thread)d %(message)s'

    logging.basicConfig(level=loglevel,
                        format=log_fmt,
                        filename=logfile)

    console = logging.StreamHandler()
    console.setLevel(loglevel)
    formatter = logging.Formatter(log_fmt)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def init_parse_args():
    parser = argparse.ArgumentParser(
        description="Compares files in a given directory for duplicates based on contents.",
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


def main(config, args, loglevel):

    start_time = time()
    search = DuplicateSearch(config, args.searchpath)
    logging.info("Specified search path: %s" % search.searchpath)
    logging.info("Starting duplicate search")

    search.do(search.handle)

    search.report()
    search.show_dupes()

    logging.info("Elapsed time: %f" % (time() - start_time))


if __name__ == '__main__':

    config = init_config()
    args = init_parse_args()

    logfile = os.path.join(BASE_PATH, config.get('Logging', 'log-filename'))
    loglevel = logging.DEBUG if args.verbose else logging.INFO

    init_logging(logfile, loglevel)

    main(config, args, loglevel)

# TODO : add filter for EXIF creation time
# TODO : add filter for similar filename (like suffix)
# TODO : Exclusions, leave some files/filetypes out
# TODO : database for duplicates?
