import re
import os
import pyc4
import pytest


metadata_format = """{key}:
  {fmt}: {value}
  name:  "test40kb.txt"
  folder:  false
  link:  false
  bytes:  40961"""


def test_versionString():
    version = pyc4.C4.versionString()
    regex = re.compile('c4 version (?P<c4>\d+\.\d+\.\d+) \((?P<platform>\w+)\) pyc4 version: (?P<pyc4>\d+\.\d+\.\d+)')
    match = regex.match(version)
    assert match.group('c4') ==  pyc4.__version_c4__
    assert match.group('pyc4') ==  pyc4.__version__

def test_c4Hash(testdir):
    # test c4 hashing of various files.
    c4 = pyc4.C4()
    for path, c4_check in testdir.values():
        c4id = c4.from_file(path)
        msg = '"{path}" did not generate the expected id.'
        assert str(c4.from_file(path)) == c4_check, msg.format(path=path)
    # TODO: test generating a hash that requires padding with 1's
    # I'm not sure how to generate a c4 hash that requires padding.

def test_stopping_hash(testdir):
    class StoppedC4(pyc4.C4):
        """ Forces HashIncomplete to be raised in calculate_hash_512 calls.
        """
        def __init__(self, *args, **kwargs):
            super(StoppedC4, self).__init__(*args, **kwargs)
            self.stopped_called = False

        def __stopped__(self):
            ret = self.stopped_called
            self.stopped_called = True
            return ret

    c4 = StoppedC4()
    path, c4_check = testdir['p10']
    with pytest.raises(pyc4.HashIncomplete):
        c4.from_file(path), 'HashIncomplete was not raised as expected.'

def test_progress_default(testdir, capsys):
    c4 = pyc4.C4()
    c4.progress_callback = c4.progress_default
    path, c4_check = testdir['p40']

    # This file is too small for detailed progress reporting, so we just get 100%
    c4id = c4.from_file(path)
    captured = capsys.readouterr()
    check = u'\r[ ================================================== ] 100.00%'
    assert captured.out == check

    # Reduce our block size so we get better progress reporting.
    c4.block_size = 30*2**10 # 30KB
    c4id = c4.from_file(path)
    captured = capsys.readouterr()
    check = u'\r[ =========================                          ] 50.00%'\
        u'\r[ ================================================== ] 100.00%'
    assert captured.out == check

def test_c4_format(testdir):
    c4 = pyc4.C4()
    path, c4_check = testdir['p40']
    c4id = c4.from_file(path)
    relative = os.path.relpath(path)

    # Check the default format options
    output = c4id.format()
    assert output == c4_check

    output = c4id.format(show_path=True)
    check = '{}:\n  path: "{}"'.format(c4id, relative)
    assert output == check

    output = c4id.format(show_path=True, absolute=True)
    check = '{}:\n  path: "{}"'.format(c4id, path)
    assert output == check

    output = c4id.format(show_path=True, absolute=True, fmt='path')
    check = '{}:\n  c4id: {}'.format(path, c4id)
    assert output == check

    # Check the metadata formatting
    output = c4id.format(show_metadata=True)
    check = metadata_format.format(key=c4id, fmt='path', value='"{}"'.format(relative))
    assert output == check

    output = c4id.format(show_metadata=True, absolute=True)
    check = metadata_format.format(key=c4id, fmt='path', value='"{}"'.format(path))
    assert output == check

    output = c4id.format(show_metadata=True, fmt='path')
    check = metadata_format.format(key=relative, fmt='c4id', value=c4id)
    assert output == check
