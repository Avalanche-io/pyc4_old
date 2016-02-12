#!/usr/bin/env python
"""

0Python implementation of C4 Asset Id.

"""

import os
import sys
import getopt

import hashlib
import base64
import base58

def calculate_hash_512(filename):
    """
    SHA512 Hash Digest
    """
    sha512_hash = hashlib.sha512()
    filepath = os.path.join(os.environ["PROJECT_LOC"], filename)

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
    else:
        print "Read content in the file successfully"
    
    return sha512_hash.digest(), filepath

def _as_hex_str(bytes, deliminator):
    """
    Pretty-prints bytes as hex values separated by a deliminator
    """
    return deliminator.join(map(lambda x: '%02x' % ord(x), bytes))

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

def GenerateId_base10(hash_sha512, input_file):
    string_id = int(hash_sha512.encode("hex_codec"), 16)
    return string_id

def GenerateId_base64(hash_sha512, input_file):
    string_id = base64.urlsafe_b64encode(hash_sha512)
    return string_id

def GenerateId_base64old(hash_sha512, input_file):
    string_id = base64.b64encode(hash_sha512)
    return string_id

def GenerateId_hex(hash_sha512, input_file):
    string_id = _as_hex_str(hash_sha512, '')
    return string_id

def GenerateId_HEX(hash_sha512, input_file):
    string_id = _as_hex_str(hash_sha512, '').upper()
    return string_id

def GenerateId_Hex(hash_sha512, input_file):
    string_id = _as_hex_str(hash_sha512, ':')
    return string_id

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
 

def generate_c4id():

    input_file = 'test.mp4'

    #Calculate SHA512 Hash
    hash_sha512, file_path = calculate_hash_512(input_file)

    print "Generating c4id's" + "\n" + "-------------------"
    print "Filepath: "  + str(file_path)
    
    print "\nFormat \t\t c4id"
    print "--------------------------------------------------------------------------------------------------------------------------------------------------------"

    #Base10
    id_format = 'base10'
    print "%-12s %s" % (id_format, GenerateId_base10(hash_sha512, input_file))

    #Base64
    id_format = 'base64old'
    print "%-12s %s" % (id_format, GenerateId_base64old(hash_sha512, input_file))

    #URL Safe Base64
    id_format = 'base64'
    print "%-12s %s" % (id_format, GenerateId_base64(hash_sha512, input_file))
    
    #lower case hex formatting
    id_format = 'hex'
    print "%-12s %s" % (id_format, GenerateId_hex(hash_sha512, input_file))
    
    #upper case hex formatting
    id_format = 'HEX'
    print "%-12s %s" % (id_format, GenerateId_HEX(hash_sha512, input_file))
    
    #lowercase hex formatting, with ':' delimination
    id_format = 'h:e:x'
    print "%-12s %s" % (id_format, GenerateId_Hex(hash_sha512, input_file))

    #C4
    id_format = 'c4'
    print "%-12s %s" % (id_format, GenerateId_c4(hash_sha512, input_file))


if __name__ == "__main__":
    generate_c4id()
