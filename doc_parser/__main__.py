import sys
import argparse
from pathlib import Path

from . import create_paeser

def valid_file(path):
    if not Path(path).is_file():
        raise argparse.ArgumentTypeError(f"'{path}' is not a valid file.")
    return path

def main():
    parser = argparse.ArgumentParser(description="Demostration of doc_parser package.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('path', type=valid_file, nargs='?', help="Path to file")
    group.add_argument('--mode', choices=['extract', 'chunk'], default='extract', help="Select mode")

    parser.add_argument('--size', type=int, help="Size of each chunk (required for 'chunk' mode)")
    parser.add_argument('--overlap', type=int, help="Overlap between chunks (required for 'chunk' mode)")

    args = parser.parse_args()
    
    file = args.path
    file_parser = create_paeser(file)

    if args.mode == 'extract':
        if args.size or args.overlap:
            parser.error("Additional arguments are not allowed in 'extract' mode.")
        print(file_parser.extract_raw_text())
    elif args.mode == 'chunk':
        if not args.size or not args.overlap:
            parser.error("Both 'size' and 'overlap' are required in 'chunk' mode.")
        print(file_parser.parse(args.size, args.overlap))

if __name__ == "__main__":
    main()
