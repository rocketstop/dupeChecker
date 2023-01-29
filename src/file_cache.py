import os
import hashlib
import logging


class FileHeuristicCache:
    def __init__(self, filename):
        """
        Construct an object that stores file comparison heuristics.
        :param filename of file
        """
        self.filename = filename
        self.hash = self.getHash()

    def __eq__(self, other):
        if self.hash == other.hash:
            return bool(self.hash)
        return False

    def __str__(self):
        return "<#%s#>" % self.filename

    def __repr__(self):
        return str(self)

    def __hash__(self):
        if self.hash is None:
            # if we can't hash contents, fall back to filename
            return hash(self.filename)
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

        if os.path.exists(self.filename):
            hash = hash_bytestr_iter(
                file_as_blockiter(open(self.filename, 'rb')), hashMethod, True)
            logging.debug('Generating hash for: ' + str(self.filename))
            logging.debug('Hash ' + str(hash))
            return hash
        return None
