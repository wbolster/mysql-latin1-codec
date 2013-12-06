import os

from setuptools import setup


def here(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)


setup(
    name='mysql-latin1-codec',
    description='Python string codec for MySQL\'s latin1 encoding',
    long_description=open(here('README.rst')).read(),
    version="1.0",
    py_modules=['mysql_latin1_codec'],
    author="Wouter Bolsterlee",
    author_email="uws@xs4all.nl",
    url="https://github.com/wbolster/mysql-latin1-codec",
    license="BSD License",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: System :: Recovery Tools",
        "Topic :: Text Processing",
    ],
)
