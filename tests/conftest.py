import py.path
import tempfile
import pytest

def createFile(tmpdir, size, *args):
	""" Generates a empty file of a given size using pytest's tmpdir fixture.
	"""
	# https://stackoverflow.com/a/8816144
	p = tmpdir.join(*args)
	with p.open('wb') as f:
		f.seek(size)
		f.write(b'\0')
	return p

@pytest.fixture(scope='session')
def testdir(request):
	""" Create a test directory with test files and remove it after the test is done.
	"""
	tDir = py.path.local(tempfile.mkdtemp())
	ret = {
		'p10': (str(createFile(tDir, 10*2**10, 'test10kb.txt')), 'c43KPfQswamKL6HZD6M4BtHXKDddQtBvd8a7M3UJvJxFpvicKHhJxeroCe1vG2xNbHFxoeWZkBzs4fuCuTPm8K48U5'),
		'p20': (str(createFile(tDir, 20*2**10, 'test20kb.txt')), 'c45Z9VXgaidCn4TMuXAYarEstRxouDJ662N7o7eAsLAGZwUnxc34mAfGvsSvUwxpy391dNWgH6qf5g83dVhgM24Dfv'),
		'p30': (str(createFile(tDir, 30*2**10, 'test30kb.txt')), 'c43qmXqMjEc1sf6Pcj6jzNDLxPRqLUFjYjqQzwrZifncGMSvsZxavLYJRiL5pk7Zs4U3mp46bhYa2juXhjr1J3jUQS'),
		'p40': (str(createFile(tDir, 40*2**10, 'test40kb.txt')), 'c45yGCeEiSmJYBdw5Zgqrr9NvsCLo7JdKd1ECvDm9PpCFvTabWGubgmNQMeRUohwLBnGYLgQ5DSD1APgpPwyQ6w3g1'),
	}
	# Remove the test directory after the test finishes
	# https://stackoverflow.com/a/25527537
	request.addfinalizer(lambda: tDir.remove(rec=1))
	return ret

