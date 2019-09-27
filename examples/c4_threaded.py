#!/usr/bin/python

# A example of using C4Queue to process several files simultaneously.

import threading
import pyc4
import glob


_thread_lock = threading.Lock()


def hash_finished(c4id):
    # If two threads finish at the same time, they will step on each other's
    # print statements, force them to wait till the previous thread finishes.
    with _thread_lock:
        print(c4id.format(show_path=True))

# Create and configure the queue for processing.
c4 = pyc4.C4Queue()
c4.worker_finished_callback = hash_finished
# Add files to process
c4.files = glob.glob(r'..\tests\*.*')
# Start processing the files
c4.start()
# Wait for all files to finish processing.
c4.join()
