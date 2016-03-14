#!/usr/bin/python

"""
Python implementation of multi-target copy.

"""
import os, os.path
import sys
import shutil
import hashlib

def calculate_hash_512(filename):
    """
    SHA512 Hash Digest
    """
    sha512_hash = hashlib.sha512()
    filepath = os.path.join(os.environ["PROJECT_LOC"], filename)
    """
    PROJECT_LOC environmental variable to be set as respective to platforms
    """
    try:
        with open(filepath, 'r') as f:
            statinfo = os.stat(filepath)
            block_size = 100 * (2**20)  #Magic number: 100 * 1MB blocks
            nb_blocks = (statinfo.st_size / block_size) + 1
            cnt_blocks = 0
            
            while True:
                block = f.read(block_size) 
                if not block: break
                sha512_hash.update(block)
                cnt_blocks = cnt_blocks + 1
                progress = 100 * cnt_blocks / nb_blocks
            f.close()
    except IOError:
        print "Error: can\'t find file or read data"

    return sha512_hash.digest(), filepath

def b58encode(bytes):
    """
    Base58 Encode bytes to string
    """
    __b58chars = '123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
    __b58base = len(__b58chars)

    long_value = int(bytes.encode("hex_codec"), 16)

    result = ''
    while long_value >= __b58base:
        div, mod = divmod(long_value, __b58base)
        result = __b58chars[mod] + result
        long_value = div

    result = __b58chars[long_value] + result

    return result

def GenerateId_c4(hash_sha512, input_file):
    c4_id_length = 90
    b58_hash = b58encode(hash_sha512)

    #Pad with '1's if needed
    padding = ''
    if len(b58_hash) < (c4_id_length - 2):
        padding = ('1' * (c4_id_length - 2 - len(b58_hash)))

    #Combine to form C4 ID
    string_id = 'c4' + padding + b58_hash
    return string_id

def compute_c4Id(src):
    """
    Computing the c4id of each file by traversing through directory 'sec'
    """
    if src.endswith('/*') or src.endswith('\*'):
        src = src[:-2]
    if src.endswith('/*.*') or src.endswith('\*.*'):
        src = src[:-3]

    # Traversing sub-folders for filenames
    cnt = sum([len(f) for r,d,f in os.walk(src)])
    
    print "Total file count: %d, Generating c4id's...\n" % cnt
    for root, subfolder, filenames in os.walk(src):
        for filename in filenames:
            file_path = str(os.path.join(root, filename))
            hash_sha512, fpath = calculate_hash_512(file_path)
            sid = GenerateId_c4(hash_sha512, fpath)
            print "%s \n  %s" % (fpath, sid)

def recursive_copy(src, dest):
    if src.endswith('/*') or src.endswith('\*'):
        src = src[:-2]
    if src.endswith('/*.*') or src.endswith('\*.*'):
        src = src[:-3]

	if (os.path.exists(dest) or os.path.isdir(dest)):
		shutil.rmtree(dest)
		print "Directory %s already exists.. deleting..." % dest

    else:
        print "\nCopying file(s)..."
        try:
            shutil.copytree(src, dest)
        except OSError as e:
    	    if e.errno == errno.ENOTDIR:
    		     shutil.copy(src, dest)
    	    else:
    		     raise
        print "Copied %s to %s" % (src, dest)

def c4(argv):
    desc = "Usage:\nRecursively copies the files from source directory & simultaneously IDs them."
    syntax = "\n c4.py cp -R <src-dir> <target-dir>\n c4.py cp -R <src-dir> -t <target-dir1> <target-dir2>..."
    options = "\n\n    cp\t\t\tCopy operation to perform.\n    -R\t\t\tRecursively copy source files to target.\n    <src-dir>\t\tSpecify source directory to copy.\n    <target-dir>\tSpecify target directory to copy."
    win = "\n\n  Windows: c4.py cp -R d:\src-dir\* e:\dst-dir  (OR)  c4.py cp -R d:\src-dir\* -t d:\dst-dir1 e:\dst-dir2"
    linux = "\n  Linux: c4.py cp -R /src-dir/* /dst-dir  (OR)  c4.py cp -R /src-dir/* -t /dst-dir1 /dst-dir2"

    cmd_usage = desc + syntax + options + win + linux

    if len(argv) < 4:
	    print cmd_usage
	    sys.exit()

    if ((len(argv) == 4) and (("-R" in argv[1]) or ("-r" in argv[1]))):
        src_path, dest_path = argv[2], argv[3]
        compute_c4Id(src_path)
        recursive_copy(src_path, dest_path)
    elif ((len(argv) > 4) and ("-t" in argv[3])):
	    src_path = argv[2]
            compute_c4Id(src_path)
            for i in range(4, (len(argv))):
                dest_path = argv[i]
                recursive_copy(src_path, dest_path)
    else:
	    print "Incorrect arguments specified:\n",cmd_usage
	    sys.exit()

if __name__ == '__main__':
	c4(sys.argv[1:])
