#!/usr/bin/python

"""
Pythonic implementation of multi-target copy with c4id generation.

"""
import os, os.path
import sys
import shutil
import hashlib
from sys import platform as _platform

#Helpers
def draw_progress_bar(percent, barLen = 50):
    """
    Simple command line progress bar
    """
    sys.stdout.write("\r")
    progress = ""
    for i in range(barLen):
        if i < int(barLen * percent / 100):
            progress += "="
        else:
            progress += " "
    sys.stdout.write("[ %s ] %.2f%%" % (progress, percent))
    sys.stdout.flush()

def calculate_hash_512(src_filename, target_path):
    """
    SHA512 Hash Digest
    """
    sha512_hash = hashlib.sha512()
    src_filepath = os.path.join(os.getcwd(), src_filename)
    try:
        with open(src_filepath, "r") as sf:
            statinfo = os.stat(src_filepath)
            block_size = 100 * (2**20)  #Magic number: 100 * 1MB * 1MB blocks
            nb_blocks = (statinfo.st_size / block_size) + 1
            cnt_blocks = 0

            if _platform.lower() == "linux" or _platform.lower() == "linux2":
                l = len(src_filepath.split('/'))
                target_file_path = os.path.join(target_path, src_filepath.split('/')[l-1])
            elif _platform.lower() == "win32":
                l = len(src_filepath.split('\\'))
                target_file_path = os.path.join(target_path, src_filepath.split('\\')[l-1])
            print "\nTarget File path: %s" % target_file_path

            while True:
                block = sf.read(block_size) 
                if not block: break
                sha512_hash.update(block)
                with open(target_file_path, "a") as tf:
                    tf.write(block)
                cnt_blocks = cnt_blocks + 1
                progress = 100 * cnt_blocks / nb_blocks
                draw_progress_bar(progress)
                c4_id_length = 90
                b58_hash = b58encode(sha512_hash.digest())

                #Pad with '1's if needed
                padding = ''
                if len(b58_hash) < (c4_id_length - 2):
                    padding = ('1' * (c4_id_length - 2 - len(b58_hash)))

                #Combine to form C4 ID
                string_id = 'c4' + padding + b58_hash
                if progress == 100:
                    print "\n  %s" % str(string_id)
            sf.close()
            tf.close()
    except IOError:
        print "Error: cant find or read '%s' file" % (src_filename)

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

def compute_c4Id(source_path, target_path):
    """
    Computing the c4id of each file by traversing through directory
    @param source_path: Relative path of the source directory
    """
    # Computing the file-count recursively traversing the directory
    # Excludes the count of number of directories
    cnt = sum([len(f) for r,d,f in os.walk(source_path)])
    print "Total file count: %d, Generating c4id's..." % cnt

    delete_folder(target_path)

    # Traversing sub-folders for filenames
    for root, subfolder, filenames in os.walk(source_path):
        newDir = os.path.join(target_path, root[1+len(source_path):])
        if not os.path.exists(newDir):
            os.makedirs(newDir)
        for filename in filenames:
            src_file_path = str(os.path.join(root, filename))
            calculate_hash_512(src_file_path, newDir)

def recursive_copy(source_path, target_path):
    """
    Recursively copies source directory content to target directory
    @param source_path: Relative path of the source directory
    @param target_path: Relative path of the target directory
    """
    print "\nCopying file(s)..."
    try:
        shutil.copytree(source_path, target_path)
    except OSError as e:
        if e.errno == errno.ENOTDIR:
            shutil.copy(source_path, target_path)
        else:
            raise
    print "Copied %s to %s" % (source_path, target_path)

def delete_folder(target_path):
    """
    Deletes a folder, if it already exists
    @param target_path: Relative path of the directory to delete
    """
    if (os.path.exists(target_path) or os.path.isdir(target_path)):
        print "Directory %s already exists.. deleting..." % target_path
        try:
            shutil.rmtree(target_path)
        except OSError:
            os.remove(target_path)

def c4(argv):
    """
    Implementation to do multi-target copy (recursive) of directories & simultaneously generate C4 id's for each file
    @param argv: Arguments passed at command-line 
    """
    desc = "Recursively copies the files from source directory & simultaneously IDs them."
    syntax = "\nUsage:\n c4.py cp -R <src-dir> <target-dir>\n c4.py cp -R <src-dir> -t <target-dir1> <target-dir2>..."
    options = "\n\n    cp\t\t\tCopy operation to perform.\n    -R\t\t\tRecursively copy source files to target.\n    <src-dir>\t\tSpecify source directory to copy.\n    <target-dir>\tSpecify target directory to copy."
    win = "\n\n  Windows: c4.py cp -R d:\src-dir\*.* e:\dst-dir  (OR)  c4.py cp -R d:\src-dir\*.* -t d:\dst-dir1 e:\dst-dir2"
    linux = "\n  Linux: c4.py cp -R /src-dir/*.* /dst-dir  (OR)  c4.py cp -R /src-dir/*.* -t /dst-dir1 /dst-dir2"

    cmd_usage = desc + syntax + options + win + linux

    # Displays the command-usage incase of incorrect arguments specified 
    if len(argv) < 4:
        print cmd_usage
        sys.exit(2)

    # Perform single source to single target directory copy & c4id generation operation
    if ((len(argv) == 4) and (("-R" in argv[1]) or ("-r" in argv[1]))):
        src_path, dest_path = argv[2], argv[3]
        if src_path.endswith('/*') or src_path.endswith('\*'):
            src_path = src_path[:-2]
        if src_path.endswith('/*.*') or src_path.endswith('\*.*'):
            src_path = src_path[:-4]
        compute_c4Id(src_path, dest_path)

    # Perform single source to multiple target directory copy & c4id generation operation
    elif ((len(argv) > 4) and ("-t" in argv[3])):
        src_path = argv[2]
        if src_path.endswith('/*') or src_path.endswith('\*'):
            src_path = src_path[:-2]
        if src_path.endswith('/*.*') or src_path.endswith('\*.*'):
            src_path = src_path[:-4]
        for i in range(4, (len(argv))):
            dest_path = argv[i]
            compute_c4Id(src_path, dest_path)

    else:
        print "Incorrect arguments specified:\n", cmd_usage
        sys.exit(2)
    print "\n Copied '%s' to '%s' successfully..." % (src_path, dest_path)

if __name__ == '__main__':
    c4(sys.argv[1:])
