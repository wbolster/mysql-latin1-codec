=================================================
Python string codec for MySQL's *latin1* encoding
=================================================

:Author: Wouter Bolsterlee
:License: 3-clause BSD
:URL: https://github.com/wbolster/mysql-latin1-codec

Overview
========

This project provides a Python string codec for MySQL's *latin1* encoding, and
an accompanying *iconv*-like command line script for use in shell pipes.


Rationale
=========

* MySQL defaults to using the *latin1* encoding for all its textual data, but
  its *latin1* encoding is not actually *latin1* but a MySQL-specific variant.

* Due to improperly written applications or wrongly configured databases, many
  existing databases keep data in MySQL *latin1* columns, even if that data is
  not actually *latin1* data.

* MySQL will *not* complain about this, so this often goes unnoticed. The
  problems only appear when you try to access the database from another
  application, or when you try to ``grep`` through database dumps produced by
  ``mysqldump``.

* Many libraries do not support this encoding properly, and using the real
  *latin1* encoding leads to corruption when processing data, especially when
  the database contains text that is not in a West-European language.

* This string codec makes it possible to reconstruct the exact bytes as they
  were stored in MySQL. This is a valuable tool for fixing text encoding issues
  with such databases. For convenience, a command line interface that behaves
  like *iconv* is also included.


Installation
============

::

    $ pip install mysql-latin1-codec

The package supports both Python 2 and Python 3.


Usage
=====

You can use this project in two ways: as a stand-alone command line tool and as
a Python module.

Command line tool
-----------------

The command line tool behaves like *iconv*::

    $ python -m mysql_latin1_codec --help
    usage: mysql_latin1_codec.py [-h] [-f encoding] [-t encoding] [-o filename]
                                 [-c]
                                 [inputs [inputs ...]]

    iconv-like tool to encode or decode data using MySQL's "latin1" dialect,
    which, despite the name, is a mix of cp1252 and ISO-8859-1.

    positional arguments:
      inputs                Input file(s) (defaults to stdin)

    optional arguments:
      -h, --help            show this help message and exit
      -f encoding, --from encoding
                            Source encoding (uses MySQL's "latin1" if omitted)
      -t encoding, --to encoding
                            Target encoding (uses MySQL's "latin1" if omitted)
      -o filename, --output filename
                            Output file (defaults to stdout)
      -c, --skip-invalid    Omit invalid characters from output (not the default)


Python API
----------

In Python code, simply import the module named ``mysql_latin1_codec`` and call
the ``register()`` function. A string codec named ``mysql_latin1`` will be
registered in Python's codec registry::

    import mysql_latin1_codec

    mysql_latin1_codec.register()

You can use it using the normal ``.decode()`` and ``.encode()`` methods on
(byte)strings, and you can also specify it as the ``encoding`` argument to
various I/O functions like ``io.open()``. Example::


    # String encoding/decoding round-trip
    s1 = u'foobar'
    s2 == text.encode('mysql_latin1').decode('mysql_latin1')
    assert s1 == s2

    # Reading files
    import io
    with io.open('/path/to/file', 'r', encoding='mysql_latin1') as fp:
        for line in fp:
            pass


Practical examples
==================

The example below ‘fixes’ dumps that contain doubly encoded UTF-8 data, i.e.
real UTF-8 data stored in a MySQL *latin1* table. By default ``mysqldump`` makes
UTF-8 dumps, but if MySQL thinks the data is *latin1*, it will convert it again,
resulting in double encoded data. ::

    $ cat backup-of-broken-database-produced-by-mysqldump.sql \
      | python -m mysql_latin1_codec -f UTF-8 \
      | iconv -c -f UTF-8 -t UTF-8 \
      > legible-text-in-utf8.sql

The *iconv* pipe in this example removes invalid UTF-8 sequences, while keeping
the valid parts as-is. MySQL truncates values whose size exceeds the column's
maximum size, but if MySQL doesn't know that it is handling UTF-8 data (because
the database schema and the broken application did not tell it to do so) it
truncates the byte sequence, not the character sequence. This may result in
incomplete UTF-8 sequences when a multi-byte sequence is truncated somewhere in
the middle. Since those characters cannot be recovered anyway, removing them is
the right solution in this case.

In code you can do something similar to the example above::

    original = b'...'  # byte string containing doubly-encoded UTF-8 data
    s = original.decode('UTF-8').encode('mysql_latin1').decode('UTF-8', 'replace')

Another example to ‘fix’ a dump that contains GB2312 (Simplified Chinese) data
stored in a MySQL *latin1* column, again misinterpreted and encoded to UTF-8 by
``mysqldump``::

    $ cat mojibake-crap.sql \
      | python -m mysql_latin1_codec -f UTF-8 \
      | iconv -f GB2312 -t UTF-8 \
      > legible-text-in-utf8.sql


Technical background
====================

How MySQL defines *latin1*
--------------------------

The character set that MySQL uses when *latin1* is specified, is not actually
the well-known *latin1* character set, officially known as ISO-8859-1. What
MySQL calls *latin1* is actually a custom encoding based on *cp-1252* (also
known as *windows-1252*).

The MySQL documentation on `West European Character Sets 9§ 10.1.14.2)
<http://dev.mysql.com/doc/refman/5.7/en/charset-we-sets.html>`_ contains:

    ``latin1`` is the default character set. MySQL's ``latin1`` is the same as
    the Windows ``cp1252`` character set. THis means it is the same as official
    ``ISO 8859-1`` or IANA (Internet Assigned Numbers Authority) ``latin1``,
    except that IANA ``latin1`` treats the code points between ``0x80`` and
    ``0x9f`` as “undefined”, whereas ``cp1252``, and therefore MySQL's
    ``latin``, assign characters for those positions. For example, ``0x80`` is
    the Euro sign. For the “undefined” entries in ``cp1252``, MySQL translates
    ``0x81`` to Unicode ``0x0081``, ``0x8d`` to ``0x008d``, ``0x8ff`` to
    ``0x008f``, ``0x90`` to ``0x0090``, and ``0x9d`` to ``0x009d``.

Some more details can be found in the MySQL source code in the file
``strings/ctype-latin1.c``::

    WL#1494 notes:

    We'll use cp1252 instead of iso-8859-1.
    cp1252 contains printable characters in the range 0x80-0x9F.
    In ISO 8859-1, these code points have no associated printable
    characters. Therefore, by converting from CP1252 to ISO 8859-1,
    one would lose the euro (for instance). Since most people are
    unaware of the difference, and since we don't really want a
    "Windows ANSI" to differ from a "Unix ANSI", we will:

     - continue to pretend the latin1 character set is ISO 8859-1
     - actually allow the storage of euro etc. so it's actually cp1252

    Also we'll map these five undefined cp1252 character:
      0x81, 0x8D, 0x8F, 0x90, 0x9D
    into corresponding control characters:
       U+0081, U+008D, U+008F, U+0090, U+009D.
    like ISO-8859-1 does. Otherwise, loading "mysqldump"
    output doesn't reproduce these undefined characters.

As you can see, this encoding is significantly different from ISO-8859-1 (the
real *latin1*), but MySQL misleadingly labels it as *latin* anyway.


Why this can be a problem
-------------------------

MySQL's *latin1* encoding allows for arbitrary data to be stored in database
columns, without any validation. This means *latin1* text columns can store any
byte sequence, for example UTF-8 encoded text (which uses a variable number of
bytes per character) or even JPEG images (which is not text at all).

This is of course not the proper use of *latin1* columns. Even in this modern
Unicode-aware world, in which all properly written software that handles text
should use UTF-8 (or another Unicode encoding), it is quite common to stumble
upon wrongly configured databases or badly written software. Most applications
use the same (incorrect) assumptions for both storing and retrieving data, so in
many setups this will still ‘just work’, and the problem can go unnoticed for a
long time.

What makes this problem worse, is that MySQL defaults to using the *latin1*
character encoding, mostly for historical and backward-compatibility reasons.
This means many databases in the real world are (perhaps mistakingly) configured
to store data in columns that use MySQL's *latin1* encoding, even though the
actual data stores in those columns is not encoding using *latin1* at all.

This can lead to a variety of problems, such as encoding or decoding errors,
double encoded text, malfunctioning string operations, or incorrect truncation
which can lead to data corruption. In many cases this manifests itself as
`mojibake <http://en.wikipedia.org/wiki/Mojibake>`_ text. This may be caused by
a misinterpretation of the characters that the bytes represent, or by double
encodings, e.g. UTF-8 in a *latin1* column that was converted to UTF-8 again by
a backup script.

Many tools, like Python's built-in text codecs and the *iconv* (both the command
line tool and the C library) cannot convert data encoding using this custom
MySQL encoding. This makes it quite hard to ‘recover’ e.g. UTF-8 data that was
stored in a *latin1* column, and subsequently dumped using *mysqldump*, even if
you know what you're doing and which actual encoding was used.

When invoked on the command line, this script converts the dump file(s)
specified on the command line (or standard input if no files were given). The
data is interpreted as UTF-8 and encoded as MySQL's *latin1* and written to the
standard output. The output is the raw data, which likely needs further
processing, e.g. using iconv to "reinterpret" the data correctly (e.g. as
UTF-8).


I have no idea what you are talking about!
==========================================

No worries, that's okay.
