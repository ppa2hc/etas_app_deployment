#!/usr/bin/env python3
import sys
import argparse
from intelhex import IntelHex

def main():
    parser = argparse.ArgumentParser(
        description='Convert an Intel HEX file to a binary file, filling gaps with 0.'
    )
    parser.add_argument('input_hex', help='Path to input Intel HEX file')
    parser.add_argument('start_address', help='Start address (e.g., 0x80100000)')
    parser.add_argument('end_address', help='End address (e.g., 0x80200000)')
    parser.add_argument('output_bin', help='Path to output binary file')

    args = parser.parse_args()

    # Convert start and end addresses to integers. The base 0 allows hex values (e.g., 0x80100000)
    try:
        start_addr = int(args.start_address, 0)
        end_addr = int(args.end_address, 0)
    except ValueError as e:
        print("Error: Could not convert addresses to numbers.", e)
        sys.exit(1)

    if start_addr > end_addr:
        print("Error: Start address must be less than or equal to end address.")
        sys.exit(1)

    # Create an instance of IntelHex and load the HEX file.
    ih = IntelHex()
    try:
        ih.loadhex(args.input_hex)
    except Exception as e:
        print("Error: Could not load HEX file:", e)
        sys.exit(1)

    # Write the binary file using the 'start' and 'end' keywords and pad with 0.
    try:
        ih.tobinfile(args.output_bin, start=start_addr, end=end_addr, pad=0)
        print(f"Successfully wrote binary file: {args.output_bin}")
    except Exception as e:
        print("Error: Could not write binary file:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
