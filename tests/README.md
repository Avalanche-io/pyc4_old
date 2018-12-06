# Testing pyc4

All tests are written using pytest.

## Setup

Cd to the pyc4 repo folder and run `pip install -e .`. This will make python aware of your dev version of pyc4. This will make it so you can import pyc4 and it will use the code in your git checkout.

## Running tests

Cd to your the tests folder in your pyc4 checkout and run the command `pytest`.

You should see something similar to this.
```
============================= test session starts =============================
platform win32 -- Python 2.7.15, pytest-4.0.0, py-1.7.0, pluggy-0.8.0
rootdir: C:\blur\dev\pyc4, inifile:
collected 7 items

test_c4.py .....                                                         [ 71%]
test_c4queue.py ..                                                       [100%]

========================== 7 passed in 8.13 seconds ===========================
```

## Test Coverage

When writing new code I use [pytest-cov](https://pypi.org/project/pytest-cov/) to make sure my tests hit all the important code lines. It should be noted that just because your tests hit every line, that doesn't mean that your tests cover all cases, so the goal is not to have 100% coverage, it's to have test coverage of all the important branches of code execution.

I use this command to test `pytest --cov-report term-missing --cov pyc4` and here is a example output.

```
============================= test session starts =============================
platform win32 -- Python 2.7.15, pytest-4.0.0, py-1.7.0, pluggy-0.8.0
rootdir: C:\blur\dev\pyc4, inifile:
plugins: cov-2.6.0
collected 7 items

test_c4.py .....                                                         [ 71%]
test_c4queue.py ..                                                       [100%]

---------- coverage: platform win32, python 2.7.15-final-0 -----------
Name                       Stmts   Miss  Cover   Missing
--------------------------------------------------------
C:\blur\dev\pyc4\pyc4.py     227     54    76%   348-352, 450-475, 478-534


========================== 7 passed in 10.81 seconds ==========================
```

As of writing, the missing line numbers 450-475 and 478-534 are the `parseArguments` function and `if __name__ == '__main__':`. I don't think that these require the work making tests would take.

If there is a line or lines that don't require the amount of code it would take to test them, you can add `# pragma: no cover`. This will ignore the line in the coverage report. You should provide some comments on why its not being tested.
