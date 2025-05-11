"""
Main compiler entry point.

This module orchestrates the compiler pipeline, from lexical analysis through
parsing and semantic analysis to code generation.
"""
import os
import sys
import logging
import argparse
from typing import Dict, Any

from src.lexer.lexer import Lexer
from src.parser.parser import Parser


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def configure_parser() -> argparse.ArgumentParser:
    """
    Configure the command line argument parser.
    
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description='Compiler for the C-minus language'
    )
    
    parser.add_argument(
        '-i', '--input',
        default='input.txt',
        help='Input source code file (default: input.txt)'
    )
    
    parser.add_argument(
        '-t', '--tokens',
        default='tokens.txt',
        help='Output tokens file (default: tokens.txt)'
    )
    
    parser.add_argument(
        '-le', '--lexical-errors',
        default='lexical_errors.txt',
        help='Output lexical errors file (default: lexical_errors.txt)'
    )
    
    parser.add_argument(
        '-s', '--symbol-table',
        default='symbol_table.txt',
        help='Output symbol table file (default: symbol_table.txt)'
    )
    
    parser.add_argument(
        '-se', '--syntax-errors',
        default='syntax_errors.txt',
        help='Output syntax errors file (default: syntax_errors.txt)'
    )
    
    parser.add_argument(
        '-p', '--parse-tree',
        default='parse_tree.txt',
        help='Output parse tree file (default: parse_tree.txt)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser


def run_compiler(args: Dict[str, Any]) -> None:
    """
    Run the compiler with the given arguments.
    
    Args:
        args: Command line arguments
    """
    # Set log level based on verbosity
    if args.get('verbose'):
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check if input file exists
    input_file = args.get('input')
    if not os.path.exists(input_file):
        logger.error(f"Input file not found: {input_file}")
        sys.exit(1)
    
    try:
        # Phase 1: Lexical analysis
        logger.info("Starting lexical analysis...")
        
        lexer = Lexer(
            input_file_path=args.get('input'),
            tokens_file_path=args.get('tokens'),
            lexical_errors_file_path=args.get('lexical_errors'),
            symbol_table_file_path=args.get('symbol_table')
        )
        
        tokens = lexer.analyze()
        logger.info(f"Lexical analysis complete. Found {len(tokens)} tokens.")
        
        # Phase 2: Parsing
        logger.info("Starting parsing...")
        
        parser = Parser(
            tokens_file_path=args.get('tokens'),
            symbol_table_file_path=args.get('symbol_table'),
            syntax_errors_file_path=args.get('syntax_errors'),
            parse_tree_file_path=args.get('parse_tree')
        )
        
        parse_tree = parser.analyze(tokens=tokens, symbol_table=lexer.symbol_table)
        logger.info(f"Parsing complete. Parse tree has {len(parse_tree)} nodes.")
        
        # Phase 3: Semantic analysis (to be implemented)
        logger.info("Semantic analysis skipped (not implemented yet).")
        
        # Phase 4: Code generation (to be implemented)
        logger.info("Code generation skipped (not implemented yet).")
        
        logger.info("Compilation successful.")
    
    except Exception as e:
        logger.error(f"Compilation failed: {e}")
        if args.get('verbose'):
            import traceback
            traceback.print_exc()
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    # Parse command line arguments
    parser = configure_parser()
    args = vars(parser.parse_args())
    
    # Run the compiler
    run_compiler(args)


if __name__ == "__main__":
    main() 