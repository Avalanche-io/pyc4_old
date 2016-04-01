#!/usr/bin/python

"""
Pythonic implementation of multi-target copy with c4id generation(Parallel Copy).

"""

import Queue
import threading
import time
import os, os.path
import sys
import shutil
import hashlib

exitFlag = 0
repeat = ""


class myThread(threading.Thread):
    def __init__(self, threadID, name, queue, idFlag):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.queue = queue
        self.idFlag = idFlag

    def run(self):
        if debugFlag:
            print "**** Starting %s" % self.name
        process_data(self.name, self.queue, self.idFlag)
        if debugFlag:
            print "**** Ending %s" % self.name

# Helpers
def draw_progress_bar(percent, barLen=50):
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
    sys.stdout.flush()
    sys.stdout.write("[ %s ] %.2f%%" % (progress, percent))

def calculate_hash_512(src_filename, target_filename, idFlag):
    """
    SHA512 Hash Digest
    """
    sha512_hash = hashlib.sha512()
    src_filepath = os.path.join(os.getcwd(), src_filename)
    try:
        with open(src_filepath, "r") as sf:
            statinfo = os.stat(src_filepath)
            block_size = 100 * (2 ** 20)  # Magic number: 100 * 1MB blocks
            nb_blocks = (statinfo.st_size / block_size) + 1
            cnt_blocks = 0

            if _platform.lower() == "linux" or _platform.lower() == "linux2":
                l = len(src_filepath.split('/'))
                target_file_path = os.path.join(target_path, src_filepath.split('/')[l - 1])
            elif _platform.lower() == "win32":
                l = len(src_filepath.split('\\'))
                target_file_path = os.path.join(target_path, src_filepath.split('\\')[l - 1])

            while True:
                block = sf.read(block_size)
                sha512_hash.update(block)
                if not block: break
                cnt_blocks = cnt_blocks + 1
                with open(target_filename, "a") as tf:
                    tf.write(block)
                tf.close()

            print "\nCopying %s (to) %s" % (src_filepath, target_filename)
            progress = 100 * cnt_blocks / nb_blocks
            draw_progress_bar(progress)

            if idFlag:
                c4_id_length = 90
                b58_hash = b58encode(sha512_hash.digest())

                # Pad with '1's if needed
                padding = ''
                if len(b58_hash) < (c4_id_length - 2):
                    padding = ('1' * (c4_id_length - 2 - len(b58_hash)))

                # Combine to form C4 ID
                string_id = 'c4' + padding + b58_hash
                print "\n  %s" % str(string_id)
            sf.close()
            idFlag = True
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

    # Pad with '1's if needed
    padding = ''
    if len(b58_hash) < (c4_id_length - 2):
        padding = ('1' * (c4_id_length - 2 - len(b58_hash)))

    # Combine to form C4 ID
    string_id = 'c4' + padding + b58_hash
    return string_id

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

def process_data(threadName, queue, idFlag):
    global repeat
    while not exitFlag:
        if not workQueue.empty():
            (sfile, dfile) = queue.get()
            if sfile == repeat:
                idFlag = False
            if idFlag is True:
                repeat = sfile
            calculate_hash_512(sfile, dfile, idFlag)
        time.sleep(0.5)

def queue_mt(argv):
    """
    Implementation to do multi-target copy (recursive) of directories & simultaneously generate C4 id's for each file
    @param argv: Arguments passed at command-line 
    """
    desc = "Recursively copies the files from source directory & simultaneously IDs them."
    syntax = "\nUsage:\n c4.py cp -L -R <src-dir> <target-dir>\n c4.py cp -L -R <src-dir> -t <target-dir1> <target-dir2>..."
    options = "\n\n    cp\t\t\tCopy operation to perform.\n    -L\t\t\tDisplay running logs.(Optional)\n    -R\t\t\tRecursively copy source files to target.\n    <src-dir>\t\tSpecify source directory to copy.\n    <target-dir>\tSpecify target directory to copy."
    win = "\n\n  Windows: c4.py cp -R d:\src-dir\*.* e:\dst-dir  (OR)  c4.py cp -R d:\src-dir\*.* -t d:\dst-dir1 e:\dst-dir2"
    linux = "\n  Linux: c4.py cp -R /src-dir/*.* /dst-dir  (OR)  c4.py cp -R /src-dir/*.* -t /dst-dir1 /dst-dir2"

    cmd_usage = desc + syntax + options + win + linux

    # Displays the command-usage incase of incorrect arguments specified 
    if len(argv) < 4:
        print cmd_usage
        sys.exit(2)

    global threadID, workQueue, debugFlag
    threads, threadList, threadID, debugFlag, cnt = [], [], 1, False, 0
    stime = time.time()

    # Perform single source to single target directory copy & c4id generation operation
    if ((len(argv) == 4) and (("-R" in argv[1]) or ("-r" in argv[1]))) or ((len(argv) == 5) and (("-R" in argv[2]) or ("-r" in argv[2]))):
        if (len(argv) == 4):
            src_path, dest_path = argv[2], argv[3]
        if (len(argv) == 5) and ("-L" in argv[1]):
            debugFlag = True
            src_path, dest_path = argv[3], argv[4]
        if src_path.endswith('/*') or src_path.endswith('\*'):
            src_path = src_path[:-2]
        if src_path.endswith('/*.*') or src_path.endswith('\*.*'):
            src_path = src_path[:-4]

        # Computing the file-count recursively traversing the directory
        # Excludes the count of number of directories
        fcnt = sum([len(f) for r, d, f in os.walk(src_path)])
        print "File)s) count in source directory: %d" % fcnt
        cnt = fcnt * 1
        workQueue = Queue.Queue(cnt)

        # Fill the Queue
        for root, subfolder, filenames in os.walk(src_path):
            newDir = os.path.join(dest_path, root[1 + len(src_path):])
            if not os.path.exists(newDir):
                os.makedirs(newDir)
            else:
                delete_folder(newDir)
            for filename in filenames:
                sfpath = str(os.path.join(root, filename))
                dfpath = str(os.path.join(newDir, filename))
                workQueue.put((sfpath, dfpath))
                if debugFlag:
                    print "***** Added to Q... %s | %s" % (sfpath, dfpath)

    elif ((len(argv) > 4) and (("-t" in argv[3]) or ("-t" in argv[4]))):
        if ("-L" in argv[1]):
            debugFlag = True
            src_path, st = argv[3], 5
        else:
            src_path, st = argv[2], 4
        if src_path.endswith('/*') or src_path.endswith('\*'):
            src_path = src_path[:-2]
        if src_path.endswith('/*.*') or src_path.endswith('\*.*'):
            src_path = src_path[:-4]

        # Computing the file-count recursively traversing the directory
        # Excludes the count of number of directories
        fcnt = sum([len(f) for r, d, f in os.walk(src_path)])
        if ("-L" in argv[1]):
            dst = (len(argv) - 5)
        else:
            dst = (len(argv) - 4)
        print "File(s) count in source directory:%d | Destination directories count:%s" % (fcnt, dst)
        cnt = fcnt * dst
        workQueue = Queue.Queue(cnt)

        # Fill the Queue
        for root, subfolder, filenames in os.walk(src_path):
            for i in range(st, (len(argv))):
                dest_path = argv[i]
                newDir = os.path.join(dest_path, root[1 + len(src_path):])
                if not os.path.exists(newDir):
                    os.makedirs(newDir)
                else:
                    delete_folder(newDir)
                for filename in filenames:
                    sfpath = str(os.path.join(root, filename))
                    dfpath = str(os.path.join(newDir, filename))
                    workQueue.put((sfpath, dfpath))
                    if debugFlag:
                        print "***** Added to Q... %s | %s" % (sfpath, dfpath)

    print "\nGenerating c4id's for source directory files only...\n"
    # Create new threads
    max_threads = 100
    if cnt > max_threads:
        cnt = max_threads
    for i in range(1, cnt+1):
        s = 'Thread'+str(i)
        threadList.append(s)
    if debugFlag:
        print "***** ThreadsList: %s" % str(threadList)
    for tName in threadList:
        thread = myThread(threadID, tName, workQueue, idFlag=True)
        thread.start()
        threads.append(thread)
        threadID += 1

    # Wait for queue to empty
    while not workQueue.empty():
        pass

    # Notify threads its time to exit
    global exitFlag
    exitFlag = 1

    # Wait for all threads to complete
    for t in threads:
        t.join()

    if debugFlag:
        print "\nUtility Exec time: %s sec" %(time.time() - stime)

if __name__ == '__main__':
    queue_mt(sys.argv[1:])
