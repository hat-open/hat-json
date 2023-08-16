from pathlib import Path
import argparse
import sys

from hat.json.encoder import (Format,
                              decode_file, decode_stream,
                              encode_file, encode_stream)


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-o', '--output', metavar='PATH', type=Path, default=Path('-'),
        help="output path or '-' for stdout (default '-')")
    parser.add_argument(
        '--in-format', metavar='FORMAT', type=Format, default=None,
        help="input format 'json', 'yaml' or 'toml'")
    parser.add_argument(
        '--out-format', metavar='FORMAT', type=Format, default=None,
        help="output format 'json', 'yaml' or 'toml'")
    parser.add_argument(
        'input', metavar='PATH', type=Path, default=Path('-'), nargs='?',
        help="input path or '-' for stdin (default '-')")
    return parser


def main():
    parser = create_argument_parser()
    args = parser.parse_args()

    if args.input == Path('-'):
        in_format = args.in_format or Format.JSON
        data = decode_stream(sys.stdin, in_format)

    else:
        data = decode_file(args.input, args.in_format)

    if args.output == Path('-'):
        out_format = args.out_format or Format.JSON

        if out_format == Format.TOML:
            stdout, sys.stdout = sys.stdout.detach(), None

        else:
            stdout = sys.stdout

        encode_stream(data, stdout, out_format)

    else:
        encode_file(data, args.output, args.out_format)


if __name__ == '__main__':
    sys.argv[0] = 'hat-json-convert'
    sys.exit(main())
