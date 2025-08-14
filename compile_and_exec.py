from compiler import compile
from execute import exec



import argparse
import sys


def main():
    input_file = "input.txt"
    output_file = "result.txt"  
    error_file = "error.txt"

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', help='Path to the input file')
    parser.add_argument('-o', '--output_file', help='Path to the output file')
    parser.add_argument('-e', '--error_file', help='Path to the error file')

    args = parser.parse_args()

    if args.input_file:
        input_file = args.input_file
    if args.output_file:
        output_file = args.output_file
    if args.error_file:
        error_file = args.error_file
    compile(code_file_path=input_file)
    exec(result_path=output_file , error_path=error_file)
    
    

main()