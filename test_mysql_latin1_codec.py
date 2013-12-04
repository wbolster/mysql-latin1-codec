
from __future__ import unicode_literals

import pytest

import mysql_latin1_codec  # noqa


def test_codec_registration():
    """This test only passes if the codec registration was succesful."""
    assert b''.decode('mysql_latin1') == ''
    assert ''.encode('mysql_latin1') == b''


def test_code_points():
    """Test a few code points that differ between Latin1-like encodings."""

    # Byte 0x80 decodes to a control char in ISO-8859-1 (latin1)...
    assert b'\x80'.decode('ISO-8859-1') == '\u0080'
    assert b'\x80'.decode('latin1') == '\u0080'

    # ... but cp1252 and MySQL's "latin1" decode it to U+20AC EURO SIGN.
    assert b'\x80'.decode('cp1252') == '\u20ac'
    assert b'\x80'.decode('mysql_latin1') == '\u20ac'

    # Byte 0x81 decodes to U+0081 <control> in ISO-8859-1 (latin1)
    # and MySQL's "latin1"...
    assert b'\x81'.decode('ISO-8859-1') == '\u0081'
    assert b'\x81'.decode('latin1') == '\u0081'
    assert b'\x81'.decode('mysql_latin1') == '\u0081'

    # ... but in cp1252 this byte is not mapped at all.
    with pytest.raises(UnicodeDecodeError):
        b'\x81'.decode('cp1252')
