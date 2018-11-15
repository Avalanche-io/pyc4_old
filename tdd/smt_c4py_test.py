#!/usr/bin/env python

"""

TDD python implementation for testing of C4 Asset Id. https://github.com/C4labs/c4python

"""
import os
import sys
import getopt

import hashlib
import base64

import unittest
from sys import platform as _platform

class TDD_C4Py(unittest.TestCase):

    def calculate_hash_512(self, filepath):
        """
        SHA512 Hash Digest
        """
        sha512_hash = hashlib.sha512()
    
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
    
        return sha512_hash.digest()

    def _as_hex_str(self, bytes, deliminator):
        """
        Pretty-prints bytes as hex values separated by a deliminator
        """
        return deliminator.join(map(lambda x: '%02x' % ord(x), bytes))

    def b58encode(self, bytes):
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

    def GenerateId_base10(self, hash_sha512, input_file):
        string_id = int(hash_sha512.encode("hex_codec"), 16)
        return string_id
 
    def GenerateId_base64(self, hash_sha512, input_file):
        string_id = base64.urlsafe_b64encode(hash_sha512)
        return string_id

    def GenerateId_base64old(self, hash_sha512, input_file):
        string_id = base64.b64encode(hash_sha512)
        return string_id

    def GenerateId_hex(self, hash_sha512, input_file):
        string_id = self._as_hex_str(hash_sha512, '')
        return string_id

    def GenerateId_HEX(self, hash_sha512, input_file):
        string_id = self._as_hex_str(hash_sha512, '').upper()
        return string_id

    def GenerateId_Hex(self, hash_sha512, input_file):
        string_id = self._as_hex_str(hash_sha512, ':')
        return string_id

    def GenerateId_c4(self, hash_sha512, input_file):
        c4_id_length = 90
        b58_hash = self.b58encode(hash_sha512)

        #Pad with '1's if needed
        padding = ''
        if len(b58_hash) < (c4_id_length - 2):
            padding = ('1' * (c4_id_length - 2 - len(b58_hash)))

        #Combine to form C4 ID
        string_id = 'c4' + padding + b58_hash
        return string_id
        
    def assertFormat(self, id_format, expected_asset_id):
        
        input_file = "test.mp4"

        hash_sha512 = self.calculate_hash_512(input_file)

        if id_format == 'base10':
            string_id = self.GenerateId_base10(hash_sha512, input_file)
        elif id_format == 'base64':
            string_id = self.GenerateId_base64(hash_sha512, input_file)
        elif id_format == 'base64old':
            string_id = self.GenerateId_base64old(hash_sha512, input_file)
        elif id_format == 'hex':
            string_id = self.GenerateId_hex(hash_sha512, input_file)
        elif id_format == 'HEX':
            string_id = self.GenerateId_HEX(hash_sha512, input_file)
        elif id_format == 'h:e:x':
            string_id = self.GenerateId_Hex(hash_sha512, input_file)
        else:
            string_id = self.GenerateId_c4(hash_sha512, input_file)
        
        string_id, expected_asset_id = str(string_id), str(expected_asset_id)
 
        self.assertEqual(string_id, expected_asset_id)    

    def test_FormatBase10(self):
        """
        Test Base10 Encode format
        """
        b10 = 'base10'
        b10_linux = '233803744545110310216306057753707795845281583608498622423108503755760419280388804756341751474437429928890813313183167255134686362059831191431182690902371'
        b10_win32 = '6947014733717681226256835403058930834079399222957454183858210757583931074980505374874844348815370498268314771601646399676527210506975306258778633692106760'

        if _platform.lower() == "linux" or _platform.lower() == "linux2":
            self.assertFormat(b10, b10_linux)
        elif _platform.lower() == "win32":
            self.assertFormat(b10, b10_win32)

    def test_FormatBase64(self):
        """
        Test Url safe Base64 Encode format
        """
        b64 = 'base64'
        b64_linux = 'BHbPE-1VXHz_X7jP60v74nhfRKH87c0GqmSC1_uXdyK83bG70JoJCT7rBLV76UREuwckcpa0z82j5VcrAbVhYw=='
        b64_win32 = 'hKRM-aiDeYafDs7vFjV18XxQtoOpANwfh85qO8uzJ_hUTqIA55QlsCooNtTRkMblu-lTZoekPvY34lVdG5XQCA=='

        if _platform.lower() == "linux" or _platform.lower() == "linux2":
            self.assertFormat(b64, b64_linux)
        elif _platform.lower() == "win32":
            self.assertFormat(b64, b64_win32)

    def test_FormatBase64old(self):
        """
        Test Base64 Encode format
        """
        b64old = 'base64old'
        b64old_linux = 'BHbPE+1VXHz/X7jP60v74nhfRKH87c0GqmSC1/uXdyK83bG70JoJCT7rBLV76UREuwckcpa0z82j5VcrAbVhYw=='
        b64old_win32 = 'hKRM+aiDeYafDs7vFjV18XxQtoOpANwfh85qO8uzJ/hUTqIA55QlsCooNtTRkMblu+lTZoekPvY34lVdG5XQCA=='

        if _platform.lower() == "linux" or _platform.lower() == "linux2":
            self.assertFormat(b64old, b64old_linux)
        elif _platform.lower() == "win32":
            self.assertFormat(b64old, b64old_win32)
    
    def test_FormatHex(self):
        """
        Test lower case Hex Encode format
        """
        hexL = 'hex'
        hexL_linux = '0476cf13ed555c7cff5fb8cfeb4bfbe2785f44a1fcedcd06aa6482d7fb977722bcddb1bbd09a09093eeb04b57be94444bb07247296b4cfcda3e5572b01b56163'
        hexL_win32 = '84a44cf9a88379869f0eceef163575f17c50b683a900dc1f87ce6a3bcbb327f8544ea200e79425b02a2836d4d190c6e5bbe9536687a43ef637e2555d1b95d008'

        if _platform.lower() == "linux" or _platform.lower() == "linux2":
            self.assertFormat(hexL, hexL_linux)
        elif _platform.lower() == "win32":
            self.assertFormat(hexL, hexL_win32)

    def test_FormatHEX(self):
        """
        Test upper case HEX encode format
        """
        hexU = 'HEX'
        hexU_linux = '0476CF13ED555C7CFF5FB8CFEB4BFBE2785F44A1FCEDCD06AA6482D7FB977722BCDDB1BBD09A09093EEB04B57BE94444BB07247296B4CFCDA3E5572B01B56163'
        hexU_win32 = '84A44CF9A88379869F0ECEEF163575F17C50B683A900DC1F87CE6A3BCBB327F8544EA200E79425B02A2836D4D190C6E5BBE9536687A43EF637E2555D1B95D008'

        if _platform.lower() == "linux" or _platform.lower() == "linux2":
            self.assertFormat(hexU, hexU_linux)
        elif _platform.lower() == "win32":
            self.assertFormat(hexU, hexU_win32)

    def test_FormatH_e_x(self):
        """
        Test lowercase hex formatting, with ':' delimination
        """
        hexD = 'h:e:x'
        hexD_linux = '04:76:cf:13:ed:55:5c:7c:ff:5f:b8:cf:eb:4b:fb:e2:78:5f:44:a1:fc:ed:cd:06:aa:64:82:d7:fb:97:77:22:bc:dd:b1:bb:d0:9a:09:09:3e:eb:04:b5:7b:e9:44:44:bb:07:24:72:96:b4:cf:cd:a3:e5:57:2b:01:b5:61:63'
        hexD_win32 = '84:a4:4c:f9:a8:83:79:86:9f:0e:ce:ef:16:35:75:f1:7c:50:b6:83:a9:00:dc:1f:87:ce:6a:3b:cb:b3:27:f8:54:4e:a2:00:e7:94:25:b0:2a:28:36:d4:d1:90:c6:e5:bb:e9:53:66:87:a4:3e:f6:37:e2:55:5d:1b:95:d0:08'

        if _platform.lower() == "linux" or _platform.lower() == "linux2":
            self.assertFormat(hexD, hexD_linux)
        elif _platform.lower() == "win32":
            self.assertFormat(hexD, hexD_win32)

    def test_FormatC4(self):
        """
        Test C4 Asset Id format
        """
        c4 = 'c4'
        c4_linux = 'c416bf4pkWQSfUfHizjSDzdtMqNLr93GWUQ1Pozu2gFqKyrfvXkge59yR4DHpQ6NodDHT48VwXMEXyfhigFXqFWUe2'
        c4_win32 = 'c43DP7efcKtXAfZknFiXi9u5QgRDErDNYymtKdgU1GQfZWM4LdLEnd6QnQ2v7gaFkRPPJ9CFq2jo2fRbgesD25Au8j'

        if _platform.lower() == "linux" or _platform.lower() == "linux2":
            self.assertFormat(c4, c4_linux)
        elif _platform.lower() == "win32":
            self.assertFormat(c4, c4_win32)

if __name__ == "__main__":
    unittest.main()
