from __future__ import division
import sys
import os
import hashlib
import time
try:
    import queue
except ImportError:
    # Using Python 2 and the future module is not installed
    import Queue as queue
import threading
from argparse import ArgumentParser
import codecs

__version__ = '0.1'
__version_c4__ = '0.7.0'

# When using threading this is used to ensure printing is consistent.
_thread_lock = threading.Lock()

class HashIncomplete(Exception):
    """ Raised if the c4 hash calculation was canceled before finishing. """

class C4id(object):
    """ Data store object for a C4id.

    Args:
        c4id (str): The c4id for this file object.
        path (str or None, optional): The path for this file object.
        bytes (int or None, optional): The size of the file in bytes.

    Attributes:
        c4id (str): The c4id for this file object.
        path (str): The path for this file object.
        bytes (int): The size of the file in bytes.
        name (bool or None): The filename of this file. This is None until 
            metadata_from_path is called.
        folder (bool or None): This object is a folder. This is None until
            metadata_from_path is called.
        link (bool or None): This object is a link. This is None until
            metadata_from_path is called.
    """
    def __init__(self, c4id, path=None, bytes=None):
        self.c4id = c4id
        self.path = path
        self.bytes = bytes
        self.name = None
        self.folder = None
        self.link = None

    def __str__(self):
        return self.c4id

    def format(self, show_metadata=False, show_path=False, absolute=False, fmt='id'):
        """ Convert to a standard string representation.

        Args:
            show_metadata (bool, optional): If True, then a full metadata report
                is returned. Defaults to False.
            show_path (bool, optional): If show_path and show_metadata are both
                False(default), only the c4id is returned.
            absolute (str, optional): If False(Default), the relative file path
                is returned.
            fmt (str, optional): Output formatting options. "id": c4id oriented.
                "path": path oriented. (default "id")

        Returns:
            str: The formatted text representation of this c4id.
        """
        if not (show_path or show_metadata):
            return self.c4id

        path = self.path_absolute if absolute else self.path_relative

        # TODO: Would this be better handled by a python yaml library?
        ret = ['{c4id}:', '  path: "{path}"']
        if fmt == 'path':
            ret = ['{path}:', '  c4id: {c4id}']
        if show_metadata:
            if self.name is None:
                # populate the metadata info
                self.metadata_from_path()
            ret.append('  name:  "{}"'.format(self.name))
            ret.append('  folder:  {}'.format(self.folder).lower())
            ret.append('  link:  {}'.format(self.link).lower())
            ret.append('  bytes:  {}'.format(self.bytes))

        return '\n'.join(ret).format(c4id=self.c4id, path=path)

    @property
    def path_absolute(self):
        """ Return the absolute path.
        """
        return os.path.abspath(self.path)

    @property
    def path_relative(self):
        """ Return the relative path.
        """
        return os.path.relpath(self.path)

    def metadata_from_path(self):
        """ Populate folder, link, and name.
        """
        self.folder = os.path.isdir(self.path)
        self.link = os.path.islink(self.path)
        self.name = os.path.basename(self.path)

class C4(object):
    """ Preform C4 hashing operations.

    Example:
        c4 = C4()
        c4id = c4.from_file(myFile)
        print(c4id.format(show_metadata=True))

    Args:
        block_size (int, optional): Read and hash each file in byte chunks
            of this size. Defaults to 100MB chunks.

    Attributes:
        progress_callback (callable or None): This callable will be called
            for each data block processed. This can be used to provide progress
            reporting. The callable will be passed a int value between 0-100
            representing the progress of the hash generation.
        progress_bar_length (int): The size of the text progress bar printed
            when using the progress_default callback.
    """
    c4_id_length = 90

    def __init__(self, block_size=100 * (2**20)):
        # Magic number: 100 * 1MB blocks
        self.block_size = block_size
        self.progress_callback = None
        self.progress_bar_length = 50

    def __stopped__(self):
        """ Checked by calculate_hash_512. If True, it will raise HashIncomplete.

        Returns:
            bool: If calculating the hash should exit early.
        """
        return False

    @classmethod
    def b58encode(cls, bytes):
        """
        Base58 Encode bytes to string
        """
        # Use the bitcoin base58 character set.
        # This insures that sorting of C4 ID's produces the same order as sorting
        # the raw bytes. https://github.com/Avalanche-io/c4/issues/21
        __b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        __b58base = len(__b58chars)

        long_value = int(codecs.encode(bytes, "hex_codec"), 16)

        result = ''
        while long_value >= __b58base:
            div, mod = divmod(long_value, __b58base)
            result = __b58chars[mod] + result
            long_value = div

        result = __b58chars[long_value] + result

        return result

    def calculate_hash_512(self, path):
        """ SHA512 Hash Digest

        Args:
            path (str): The path to a file or directory to hash.

        Returns:
            digest (str): The sha512 digest for path.
            bytes (int): The total size of the file in bytes.

        Raises:
            HashIncomplete: If self.__stopped__() returns True. Used to stop
                the calculation early.
        """

        sha512_hash = hashlib.sha512()

        statinfo = os.stat(path)
        bytes = statinfo.st_size
        with open(path, 'rb') as f:
            # Calculate percent using ints in python 3
            # https://www.python.org/dev/peps/pep-0238/
            nb_blocks = (bytes // self.block_size) + 1
            cnt_blocks = 0

            while True:
                if self.__stopped__():
                    raise HashIncomplete('__stopped__ returned True')
                block = f.read(self.block_size)
                if not block: break
                sha512_hash.update(block)
                if self.progress_callback is not None:
                    cnt_blocks = cnt_blocks + 1
                    progress = 100 * cnt_blocks // nb_blocks
                    self.progress_callback(progress)

        return sha512_hash.digest(), bytes

    @classmethod
    def draw_progress_bar(cls, percent, barLen = 50):
        """ Simple command line progress bar

        This will clear the previous line before drawing the progress bar.

        Args:
            percent (int): Current value of the progress 0-100.
            barLen (int, optional): How long the bar is drawn in character.
        """
        sys.stdout.write("\r")
        progress = ""
        for i in range(barLen):
            if i < int(barLen * percent // 100):
                progress += "="
            else:
                progress += " "
        sys.stdout.write("[ %s ] %.2f%%" % (progress, percent))
        sys.stdout.flush()

    def from_file(self, path):
        """ Calculate a C4id object for the given path.

        Args:
            path (str): The path to a file or directory you want to hash.

        Returns:
            C4id: The C4id object for the given path.

        Raises:
            HashIncomplete: If self.__stopped__() returns True. Used to stop
                the calculation early.
        """
        #Calculate SHA512 Hash
        hash_sha512, bytes = self.calculate_hash_512(path)
        b58_hash = self.b58encode(hash_sha512)

        #Pad with '1's if needed
        padding = ''
        if len(b58_hash) < (self.c4_id_length - 2):
            padding = ('1' * (self.c4_id_length - 2 - len(b58_hash)))

        #Combine to form C4 ID
        c4id = 'c4' + padding + b58_hash
        return C4id(c4id, path=path, bytes=bytes)

    def progress_default(self, percent):
        """ Default progress reporting, prints a progress bar.

        Args:
            percent (int): How much of the progress bar to fill in.
                Passed values between 0-100.
        """
        self.draw_progress_bar(percent, self.progress_bar_length)

    @classmethod
    def versionString(cls):
        """ The current version spec of c4 and the version of pyc4.
        """
        msg = 'c4 version {c4} ({platform}) pyc4 version: {pyc4}'
        return msg.format(c4=__version_c4__, platform=sys.platform, pyc4=__version__)

class C4Queue(C4):
    """ Preform C4 hashing operations using multiple threads.

    Example:
        c4 = C4Queue()
        c4.files = files
        c4.start()
        c4.join()
        hashes = c4.hashes

    Args:
        block_size (int, optional): Read and hash each file in byte chunks
            of this size. Defaults to 100MB chunks.

    Attributes:
        files (list): A list of all file paths to process.
        hashes (dict): This dict will be updated to contain the file path
            and C4id object generated for each file path.
        queue (queue.Queue): The Queue object used to manage processing of
            files by the child threads.
        max_threads (int): Use this to limit the number of threads used to
            process C4 hashes. This class will use a thread per file up to
            this total. Defaults to 100.
        worker_finished_callback (callable or None): Called each time a c4id
            finishes processing. The callable will be passed the C4id object
            that was just generated.
        show_progress (bool): If using worker_finished_default, should a
            progress bar be drawn? Defaults to False.
        show_path (bool): If using worker_finished_default, this is passed to
            c4id.format. Defaults to False.
        show_metadata (bool): If using worker_finished_default, this is passed to
            c4id.format. Defaults to False.
        show_absolute (bool): If using worker_finished_default, this is passed to
            c4id.format. Defaults to False.
        show_formatting (bool): If using worker_finished_default, this is passed to
            c4id.format. Defaults to False.
    """

    def __init__(self, *args, **kwargs):
        super(C4Queue, self).__init__(*args, **kwargs)
        self.files = []
        self.hashes = {}
        self.queue = queue.Queue()
        self.max_threads = 100
        self.worker_finished_callback = None
        self.show_progress = False
        self.show_path = False
        self.show_metadata = False
        self.show_absolute = False
        self.show_formatting = 'id'
        self._stop_event = threading.Event()
        self._threads = []
        self._progress_shown = False

    def join(self):
        """ Blocks until all items in the queue have been processed.

        If progress_callback is set, it will be called with the percent
        of items remaining in the queue. Note, this is updated when a item
        starts processing in a thread, not when it finishes.
        """
        percent = 0
        # Note: at this point the qsize is less than len(self.files).
        # There may be a huge jump in percent at the start of processing.
        total = len(self.files)
        try:
            # using self.queue.join() will prevent detection of KeyboardInterrupt
            while not self.queue.empty():
                time.sleep(0.1)
                if total and self.progress_callback:
                    # If there are still items in the queue, provide progress reporting
                    newPercent = 100 - 100 * (self.queue.qsize() / total)
                    # Only emit the callback if the percent changes
                    if newPercent != percent:
                        percent = newPercent
                        self.progress_callback(percent)
            # Note: We are done processing queue items, but the threads
            # need to finish processing, so we still need to call join.
            if not self.__stopped__():
                # Finish processing all threads
                self.queue.join()
        except KeyboardInterrupt:
            # The user canceled the operation, stop processing and exit
            self.stop()
        # Wait for all threads to complete
        for thread in self._threads:
            thread.join()

    def start(self):
        """ Create worker threads and add all files to the queue for processing
        """
        # If less than max_threads, use a thread per file to hash.
        for i in range(min(len(self.files), self.max_threads)):
            t = threading.Thread(target=self._worker)
            t.start()
            self._threads.append(t)

        # Add all files we need to process to the queue
        for filename in self.files:
            self.queue.put(filename)

    def stop(self):
        """ Stop processing and close all threads before the queue is empty.

        See: https://stackoverflow.com/a/325528
        """
        self._stop_event.set()

    def __stopped__(self):
        return self._stop_event.is_set()

    def _worker(self):
        """ Method run by worker threads to process items in the queue.
        """
        # Create a new C4 object to hash per thread without progress_report
        c4 = C4(self.block_size)
        c4.progress_bar_length = self.progress_bar_length

        # process any remaining items in the queue
        while not self.__stopped__():
            try:
                filename = self.queue.get(timeout=0.1)
            except queue.Empty:
                # Nothing to do, the queue is empty
                break
            try:
                c4id = c4.from_file(filename)
            except HashIncomplete:
                break
            self.hashes[filename] = c4id
            self.queue.task_done()
            if self.worker_finished_callback is not None:
                self.worker_finished_callback(c4id)

    def worker_finished_default(self, c4id):
        """ Default progress reporting.

        Prints each c4id info as soon as it finishes processing.

        Args:
            c4id (C4id): The c4id that was just generated.
        """
        output = c4id.format(
            show_metadata=self.show_metadata,
            show_path=self.show_path,
            absolute=self.show_absolute,
            fmt=self.show_formatting
        )

        # prevent any other threads from printing while we update the console
        with _thread_lock:
            if self.show_progress and self._progress_shown:
                # Clear the progress bar we printed to the console only if it
                # was already shown.
                sys.stdout.write("\r")
            # Show the result of the current hash output.
            print(output)
            if self.show_progress:
                # Provide the user with progress feedback.
                total = len(self.files)
                if total:
                    # Calculate percent done, not remaining
                    percent = 100 - 100 * (self.queue.qsize() / total)
                    self.progress_default(percent)
                    # Enable clearing the progress bar we just printed.
                    self._progress_shown = True

def parseArguments():
    # Parse command line arguments
    parser = ArgumentParser(description=C4.versionString())
    parser.add_argument("-a", "--absolute", action="store_true",
        help="Output absolute paths, instead of relative paths.")
    parser.add_argument("-d", "--depth", type=int, default=-1,
        help="Only output ids for files and folders 'depth' directories deep.")
    parser.add_argument("-f", "--formatting", default="id", choices=('id', 'path'),
        help='Output formatting options. "id": c4id oriented.'
            ' "path": path oriented. (default "id")')
    parser.add_argument("-l", "--links", action="store_true",
        help="All symbolic links are followed.")
    parser.add_argument("-m", "--metadata", action="store_true",
        help='Include file system metadata. "path" is always included unless '
            'data is piped, or only a single file is specified.')
    parser.add_argument("-R", "--recursive", action="store_true",
        help="Recursively identify all files for the given path.")
    parser.add_argument("-p", "--progress", action="store_true",
        help="Show progress while generating each c4 id.")
    parser.add_argument("-v", "--version", action="version",
        help="Show version information.", version=C4.versionString())
    parser.add_argument("-t", "--target", action="append",
        help="Specify target directory to copy. Can be repeatedly used.")
    parser.add_argument("-T", "--threads", dest="max_threads", type=int, default=0,
        help="Number of threads used to generate hashes.")
    parser.add_argument('files', nargs='*',
        help='Generate C4 IDs for the provided files or folders.')
    return parser.parse_args()

if __name__ == '__main__':
    args = parseArguments()
    show_path = args.recursive or len(args.files) > 1

    # Configure hashing options
    if args.max_threads <= 1:
        c4 = C4()
        if args.progress:
            c4.progress_callback = c4.progress_default
    else:
        c4 = C4Queue()
        c4.max_threads = args.max_threads
        # Setup the worker_finished_callback so it prints the results of
        # hashes as they finish.
        c4.worker_finished_callback = c4.worker_finished_default
        c4.show_path = show_path
        c4.show_metadata = args.metadata
        c4.show_absolute = args.absolute
        c4.show_formatting = args.formatting
        if args.progress:
            c4.show_progress = True

    def print_hash(path):
        """ Hash and print path.
        """
        try:
            c4id = c4.from_file(path)
            output = c4id.format(
                show_metadata=args.metadata,
                show_path=show_path,
                absolute=args.absolute,
                fmt=args.formatting
            )
            print(output)
        except KeyboardInterrupt:
            sys.exit(0)

    for path in args.files:
        if os.path.isdir(path):
            # TODO: generate the same sort order as the go c4
            for root, dirs, files in os.walk(path, topdown=False, followlinks=args.links):
                if args.depth > 0 and root[len(path)+1:].count(os.sep) > args.depth:
                    # TODO: generate the directory c4 id's
                    continue
                for f in files:
                    if args.max_threads <= 1:
                        print_hash(os.path.join(root, f))
                    else:
                        c4.files.append(os.path.join(root, f))
        else:
            if args.max_threads <= 1:
                print_hash(path)
            else:
                c4.files.append(path)
    # If using threading, start processing the threads and wait for them to finish.
    if args.max_threads > 1:
        c4.start()
        c4.join()
