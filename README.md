# PyC4 - Python C4
Python module for the Cinema Content Creation Cloud frame work.

## Python Classes

### C4

The `pyc4.C4` class can be used to generate c4 id hashes of file names. All operations are done in the main thread.
```python
>>> import pyc4
>>> c4 = pyc4.C4()
>>> c4id = c4.from_file('tests/conftest.py')
>>> str(c4id)
'c42M9bHvXEt7dX78AvxXVwA9FzadXeNGYyLEiDV4UJMbjsi3VoMLLooWwog88VegG4W4R6m1d5Mj6UozNqk2HkKZyd'
>>> c4id.format()
'c42M9bHvXEt7dX78AvxXVwA9FzadXeNGYyLEiDV4UJMbjsi3VoMLLooWwog88VegG4W4R6m1d5Mj6UozNqk2HkKZyd'
>>> print(c4id.format(show_metadata=True, absolute=True))
c42M9bHvXEt7dX78AvxXVwA9FzadXeNGYyLEiDV4UJMbjsi3VoMLLooWwog88VegG4W4R6m1d5Mj6UozNqk2HkKZyd:
  path: "tests/conftest.py"
  name:  "conftest.py"
  folder:  false
  link:  false
  bytes:  1263
```

If you want to report progress you can store a callback function on the c4 instance. The progress callback takes a single argument that is a int from 0 to 100 that represents the percentage of the file hash completed. If the file is smaller than c4.block_size, this function may not be called. The command line interface uses the `C4.progress_default` function.
```python
>>> c4 = pyc4.C4()
>>> c4.block_size = 1000 # Set a custom block size so we can see progress on a small file
>>> def progress_report(percent):
...     print('Hash progress: {}'.format(percent))
...
>>> c4.progress_callback = progress_report
>>> c4id = c4.from_file('tests/test_c4.py')
Hash progress: 25
Hash progress: 50
Hash progress: 75
Hash progress: 100
```

### C4Queue

The `pyc4.C4Queue` class can be used to generate c4 id hashes in multiple threads using python's threading and queue system.
```python
>>> import pyc4
>>> import glob
>>> c4 = pyc4.C4Queue()
>>> c4.max_threads = 10 # limit the number of threads used to process
>>> c4.files = glob.glob('tests/*.*')
>>> c4.files
['tests/test_c4queue.py', 'tests/README.md', 'tests/test_c4.py', 'tests/conftest.py']
>>> c4.start() # start processing c4.files
>>> c4.join() # wait for all files to be processed
>>> for c4id in c4.hashes.values(): # view the results
...     print(c4id.format(show_path=True))
...
c45eU7ER3yEH8XTQARpvqXmis7xACMDGxc5Js57adRdkgqWzBPrUHW5Lr3duA7eZfQAHn8zbX7uiqGuTAfnVKExg3w:
  path: "tests/test_c4queue.py"
c41SEWLV2BU5thHvo68gkiYKxkxNgpJ9gjboeWyYbMNmNcabEZEpT3FXSbqiVG3SidzSZxT83nnSyihfe6SduS3m8b:
  path: "tests/README.md"
c43Nw48VmxSF8w9Nzxz3CffVPVVrKkiA8qPqexboMGq5EDncxHXiayPTX2zHo6cxJY2mqnCxAw7tRuQn2pDMEe1omv:
  path: "tests/test_c4.py"
c4627mr9eneAJSgEEDPQgTYa8Qecu5mp6To649fj1CBUyGEmzpEr7HGRghnqrJmR7FUv8f1o9ieX5qR7BR1WAcknzh:
  path: "tests/conftest.py"
```

`C4Queue.join` **may** call `C4Queue.progress_callback` if there are more files than max_threads. The percent represents the total number of items processed, not how much of a individual file has been processed.

When using `C4Queue`, you can store a callback function on the `C4Queue.worker_finished_callback` method. This will be called every time a worker thread finishes processing a file in its queue. The worker finished callback should take a C4id object.
```python
>>> import pyc4
>>> import glob
>>> def hash_finished(c4id):
...     print(c4id.format(show_path=True))
...
>>> c4 = pyc4.C4Queue()
>>> c4.worker_finished_callback = hash_finished
>>> c4.files = glob.glob('tests/*.*')
>>> c4.start()
c45eU7ER3yEH8XTQARpvqXmis7xACMDGxc5Js57adRdkgqWzBPrUHW5Lr3duA7eZfQAHn8zbX7uiqGuTAfnVKExg3w:
  path: "tests/test_c4queue.py"
c41SEWLV2BU5thHvo68gkiYKxkxNgpJ9gjboeWyYbMNmNcabEZEpT3FXSbqiVG3SidzSZxT83nnSyihfe6SduS3m8b:
  path: "tests/README.md"
c43Nw48VmxSF8w9Nzxz3CffVPVVrKkiA8qPqexboMGq5EDncxHXiayPTX2zHo6cxJY2mqnCxAw7tRuQn2pDMEe1omv:
  path: "tests/test_c4.py"
c4627mr9eneAJSgEEDPQgTYa8Qecu5mp6To649fj1CBUyGEmzpEr7HGRghnqrJmR7FUv8f1o9ieX5qR7BR1WAcknzh:
  path: "tests/conftest.py"
```

### C4id

This class contains the metadata for a given c4 id and file. It contains the file path and c4id string, and can be used to generate c4 id metadata strings.

## Command line use

The main pyc4.py file can be used to generate c4 hashes from the command line.

```
$ python /usr/lib/python2.7/site-packages/pyc4.py tests
c454KKaE2vUn4PqkwthZwcWBqgySyGWBKbZ74k1JRJM59spUbGU6bTRMEbP2hsUuA1u11ipYBfUodNtWxQEGp53CwW
c44762SPbNNtwpa9GmTcGf5tFj1de9xbU52Ai25eQNNRT85D9J9XkLuKCS2DsT4fuMBop97jCfsV7QKd7tPxLGsKTQ
...
```

```
 $ python /usr/lib/python2.7/site-packages/pyc4.py tests/conftest.py -m
c42M9bHvXEt7dX78AvxXVwA9FzadXeNGYyLEiDV4UJMbjsi3VoMLLooWwog88VegG4W4R6m1d5Mj6UozNqk2HkKZyd:
  path: "tests/conftest.py"
  name:  "conftest.py"
  folder:  false
  link:  false
  bytes:  1263
```

However, if you are using the command line, a better option would be [c4 cli written in go](https://github.com/Avalanche-io/c4/tree/master/cmd/c4).
