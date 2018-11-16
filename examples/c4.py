#!/usr/bin/python

# An example of how to generate c4 hashes of files.

import pyc4
import glob

def hash_progress(progress):
    print('Progress: {}'.format(progress))

# Create and configure the c4 hashing operation.
# Note: I'm lowering the block_size to show the progress_callback in most
# cases you will not nee to update it.
c4 = pyc4.C4(block_size=1000)
c4.progress_callback = hash_progress
for path in glob.glob(r'..\tests\*.*'):
	c4id = c4.from_file(path)
	print(c4id.format(show_path=True))
