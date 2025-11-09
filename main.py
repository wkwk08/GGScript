import sys
import os
from lexer.lexer import Lexer
from lexer.token_types import TokenType

def print_tokens(tokens, show_details=True):
    """Pretty print tokens"""
    print("\n" + "="*80)
    print(f"{'TOKEN TYPE':<25} {'VALUE':<25} {'LINE':<10} {'COLUMN':<10}")
    print("="*80)
    
    for token in tokens:
        if token.type != TokenType.eof:
            value_str = str(token.value) if token.value is not None else ''
            if len(value_str) > 23:
                value_str = value_str[:20] + '...'
            print(f"{token.type:<25} {value_str:<25} {token.line:<10} {token.column:<10}")
    
    print("="*80)
    
    # Statistics
    token_count = len([t for t in tokens if t.type != TokenType.eof])
    error_count = len([t for t in tokens if t.type == TokenType.error])
    
    print("\nToken Statistics:")
    print(f"  Total tokens: {token_count}")
    print(f"  Errors: {error_count}")
    print(f"  Lines processed: {tokens[-1].line if tokens else 0}")

def main():
    """Main function"""
    print("=" * 80)
    print("GGScript Lexical Analyzer".center(80))
    print("=" * 80)
    
    # Check arguments
    if len(sys.argv) < 2:
        print("\nError: No input file specified")
        print("\nUsage:")
        print("  python main.py <source_file.gg>")
        print("  python main.py --interactive")
        sys.exit(1)
    
    # Interactive mode
    if sys.argv[1] == '--interactive':
        print("\nInteractive Mode")
        print("Enter your GGScript code (press Ctrl+Z then Enter on Windows when done):\n")
        try:
            source_code = sys.stdin.read()
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            sys.exit(0)
    # File mode
    else:
        filename = sys.argv[1]
        
        # Check if file exists
        if not os.path.exists(filename):
            print(f"\nError: File '{filename}' not found")
            sys.exit(1)
        
        # Read source file
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source_code = f.read()
            print(f"\nAnalyzing file: {filename}")
            print(f"File size: {len(source_code)} characters")
        except Exception as e:
            print(f"\nError reading file: {e}")
            sys.exit(1)
    
    # Lexical Analysis
    print("\n" + "=" * 80)
    print("Lexical Analysis")
    print("=" * 80)
    
    try:
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
    except Exception as e:
        print(f"\nLexer error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Print tokens
    print_tokens(tokens)
    
    # Check for lexical errors
    lex_errors = [t for t in tokens if t.type == TokenType.error]
    
    if lex_errors:
        print("\nLexical Errors Found:\n")
        for i, error in enumerate(lex_errors, 1):
            print(f"  {i}. Line {error.line}, Column {error.column}: {error.value}")
        print("\nLexical analysis failed.")
        sys.exit(1)
    else:
        print("\nLexical analysis completed successfully.")
        print("Compilation stopped after lexical analysis (parser not yet implemented)")
        print("=" * 80)
        sys.exit(0)

if __name__ == "__main__":
    main()