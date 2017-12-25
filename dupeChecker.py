#!/usr/bin/env python

import os
import sys
import uuid
import logging
import argparse
import ConfigParser

BASE_PATH = os.path.dirname(os.path.realpath(__file__))


def main(args, config, loglevel):

    logging.info("Filename: %s" % args.argument)

    if os.path.exists(args.argument):
        print 'Found the supplied filepath: %s' % args.argument
        logging.info('Found the supplied filepath: %s' % args.argument)

    # line for line in lines if pattern in line
    for root, dirs, files in os.walk(args.searchpath):
        if not files:
            continue

        for f in files:
            filename = os.path.join(root, f)
            if (os.path.exists(filename)):
                print '+'
            else:
                print 'F'


def init_config():
    """
    Load configuration from config file
    :return config:
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
