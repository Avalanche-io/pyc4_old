# Testing pyc4

All tests are written using pytest.

## Setup

1. Make sure pytest is installed by running: `pip install pytest`.
2. Install your development version of pyc4. Cd to the pyc4 checkout and run `pip install -e .`. This will make python aware of your dev version of pyc4. This will make it so you can import pyc4 and use your development checkout.

## Running tests

Cd to your the tests folder in your pyc4 checkout and run the command `pytest`.

You should see something similar to this.
```
platform win32 -- Python 2.7.3, pytest-3.8.2, py-1.5.2, pluggy-0.7.1
rootdir: C:\blur\dev\pyc4, inifile:
collected 7 items

test_c4.py .....                                                         [ 71%]
test_c4queue.py ..                                                       [100%]

========================== 7 passed in 8.13 seconds ===========================
```
