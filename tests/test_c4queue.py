import sys
import pyc4
import pytest


def worker_started_callback(c4, filename):
    # prevent any other threads from printing while we update the console
    with c4.lock:
        if c4.show_progress and c4._progress_shown:
            # Clear the progress bar we printed to the console only if it
            # was already shown.
            sys.stdout.write("\r")
        print('Worker_started: {}'.format(filename))

def buildChecks(testdir):
    return {path:c4_check for path, c4_check in testdir.values()}

def test_c4Hash(testdir):
    checks = buildChecks(testdir)
    # test c4 hashing of various files.
    c4 = pyc4.C4Queue()
    # Give c4 something to process in the queue.
    c4.files = checks.keys()

    # Start hashing files
    c4.start()
    # Wait for the threads to process all files.
    c4.join()
    # Verify that the calculated hashes are correct
    for path, c4id in c4.hashes.items():
        assert str(c4id) == checks[path]

def test_worker_finished_default(testdir, capsys):
    checks = buildChecks(testdir)
    c4 = pyc4.C4Queue()
    c4.max_threads = 2
    c4.show_progress = True
    c4.worker_started_callback = worker_started_callback
    c4.worker_finished_callback = c4.worker_finished_default
    # Give c4 something to process in the queue.
    c4.files = checks.keys()

    # Start hashing files
    c4.start()
    # Wait for the threads to process all files and verify.
    c4.join()

    # We can't guarantee the order the hashes are returned in, so just verify
    # that we got all of our ids and nothing else.
    captured = capsys.readouterr()
    output = captured.out
    # Replace windows new line characters with normal new lines
    output = captured.out.replace('\n\r', '\n')

    hashes = []
    started = []
    # parse the output for all c4 hashes that were printed
    lines = output.split('\n')
    for line in lines:
        split = line.split('\r')
        for item in split:
            if item.startswith('c4'):
                hashes.append(item)
            elif item.startswith('Worker_started:'):
                started.append(item)

    # and check that all expected hashes were generated
    for c4id in checks.values():
        assert str(c4id) in hashes
    assert len(checks.values()) == len(hashes)

    # Check that the worker_started_callback output was generated.
    assert len(started) == len(checks)
