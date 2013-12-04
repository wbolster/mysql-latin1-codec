"""
Python codec module implementing MySQL's non-standard "latin1" codec.
"""

from __future__ import unicode_literals

import codecs
import encodings.cp1252
import sys

ENCODING_NAME = "mysql_latin1"


#
# The section below is a copy/paste from Python's built-in cp1252.py,
# except for the codec name in getregentry() and some stylistic changes.
#

class Codec(codecs.Codec):
    def encode(self, input, errors='strict'):
        return codecs.charmap_encode(input, errors, encoding_table)

    def decode(self, input, errors='strict'):
        return codecs.charmap_decode(input, errors, decoding_table)


class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=False):
        return codecs.charmap_encode(input, self.errors, encoding_table)[0]


class IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input, final=False):
        return codecs.charmap_decode(input, self.errors, decoding_table)[0]


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


def getregentry():
    return codecs.CodecInfo(
        name=ENCODING_NAME,
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )


# (Copy/paste ends here)


#
# Adapt the built-in cp1252 tables to match MySQL's implementation.
#

table = list(encodings.cp1252.decoding_table)
table[0x81] = '\u0081'
table[0x8d] = '\u008d'
table[0x8f] = '\u008f'
table[0x90] = '\u0090'
table[0x9d] = '\u009d'
decoding_table = ''.join(table)
encoding_table = codecs.charmap_build(decoding_table)


#
# Register the new encoding with the Python codec registry.
#

def search(name):
    if name == ENCODING_NAME:
        return getregentry()

    return None  # signals no match

codecs.register(search)


#
# When invoked as a script this file acts as a filter that can be also
# used in shell pipe lines, just like iconv.
#

def main():
    import argparse
    import shutil
    parser = argparse.ArgumentParser(
        description="iconv-like tool to encode or decode data using "
                    "MySQL's \"latin1\" dialect, which, despite the "
                    "name, is a mix of cp1252 and ISO-8859-1.")
    parser.add_argument(
        '-f', '--from',
        dest='from_',
        metavar='encoding',
        default=ENCODING_NAME,
        help="Source encoding (uses MySQL's \"latin1\" if omitted)")
    parser.add_argument(
        '-t', '--to',
        metavar='encoding',
        default=ENCODING_NAME,
        help="Target encoding (uses MySQL's \"latin1\" if omitted)")
    parser.add_argument(
        '-o', '--output',
        metavar='filename',
        type=argparse.FileType('w'),
        default=sys.stdout,
        help="Output file (defaults to stdout)")
    parser.add_argument(
        '-c', '--skip-invalid',
        action="store_true", default=False,
        help="Omit invalid characters from output (not the default)")
    parser.add_argument(
        "inputs", nargs='*', default=[sys.stdin],
        type=argparse.FileType('r'),
        help="Input file(s) (defaults to stdin)")
    args = parser.parse_args()

    errors = 'ignore' if args.skip_invalid else 'strict'
    out_fp = codecs.getwriter(args.to)(args.output, errors)
    for input in args.inputs:
        in_fp = codecs.getreader(args.from_)(input, errors)
        shutil.copyfileobj(in_fp, out_fp)


if __name__ == '__main__':
    sys.exit(main())
