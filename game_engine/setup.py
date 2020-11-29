import os
import re
import codecs
import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

HERE = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()

def get_version(package):
    ver_file = read(os.path.join(package, '__init__.py'))
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", ver_file).group(1)

version = get_version("game_engine")

setuptools.setup(
    name="game_engine", 
    version=version,
    author="GoosenA",
    author_email="",
    description="Game engine for 2020 Offerzen Investec Programmabla Banking hackathon",
    url="https://github.com/pgoosen/ziggy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)