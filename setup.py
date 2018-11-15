from setuptools import setup
from codecs import open

# get pip version
__version__ = __import__("pyc4").__version__

# Get the long description from the README file
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyc4',
    version=__version__,
    description='Python module for the Cinema Content Creation Cloud frame work.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Avalanche-io/pyc4',
    download_url='https://github.com/Avalanche-io/pyc4',
    license='Apache-2.0',
    classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.7',
            'Operating System :: OS Independent',
            'License :: OSI Approved :: Apache Software License',
    ],
    keywords='c4',
    py_modules=["pyc4"],
    author='Blur Studio',
    author_email='github@blur.com'
)
