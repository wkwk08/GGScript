import sys
import os
from lexer.lexer import Lexer
from lexer.token_types import TokenType

def _type_str(token):
    t = token.type
    if isinstance(t, str):
        return t
    if hasattr(t, "value"):
        return t.value
    if hasattr(t, "name"):
        return t.name
    return str(t)

def print_tokens(tokens):
    """Pretty print tokens"""
    print("\n" + "="*80)
    print(f"{'TOKEN TYPE':<25} {'VALUE':<25} {'LINE':<10} {'COLUMN':<10}")
    print("="*80)
    for token in tokens:
        tstr = _type_str(token)
        if tstr == TokenType.eof:
            continue
        if tstr in (TokenType.whitespace, TokenType.comment):
            continue
        value_str = str(token.value) if token.value is not None else ''
        if len(value_str) > 23:
            value_str = value_str[:20] + '...'
        print(f"{tstr:<25} {value_str:<25} {token.line:<10} {token.column:<10}")
    print("="*80)

def main():
    print("=" * 80)
    print("GGScript Lexical Analyzer".center(80))
    print("=" * 80)

    if len(sys.argv) < 2:
        print("\nError: No input file specified")
        print("\nUsage:")
        print("  python main.py <source_file.gg>")
        print("  python main.py --interactive")
        sys.exit(1)

    if sys.argv[1] == '--interactive':
        print("\nInteractive Mode")
        print("Enter your GGScript code (press Ctrl+Z then Enter on Windows when done):\n")
        try:
            source_code = sys.stdin.read()
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            sys.exit(0)
    else:
        filename = sys.argv[1]
        if not os.path.exists(filename):
            print(f"\nError: File '{filename}' not found")
            sys.exit(1)
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source_code = f.read()
            print(f"\nAnalyzing file: {filename}")
            print(f"File size: {len(source_code)} characters")
        except Exception as e:
            print(f"\nError reading file: {e}")
            sys.exit(1)

    print("\n" + "=" * 80)
    print("Lexical Analysis")
    print("=" * 80)

    try:
        lexer = Lexer(source_code)
        result = lexer.make_tokens() if hasattr(lexer, "make_tokens") else lexer.tokenize()
        if isinstance(result, tuple) and len(result) == 2:
            tokens, errors = result
        else:
            tokens = result
            errors = []
    except Exception as e:
        print(f"\nLexer error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print_tokens(tokens)

    lex_errors = [t for t in tokens if _type_str(t) == TokenType.error]

    if lex_errors or errors:
        print("\nLexical Errors Found:\n")
        for i, error in enumerate(lex_errors, 1):
            print(f"  {i}. Line {error.line}, Column {error.column}: {error.value}")
        for i, err in enumerate(errors, 1):
            print(f"  E{i}. {err.as_string()}")
        print("\nLexical analysis failed.")
        sys.exit(1)
    else:
        print("\nLexical analysis completed successfully.")
        print("Compilation stopped after lexical analysis (parser not yet implemented)")
        print("=" * 80)
        sys.exit(0)

if __name__ == "__main__":
    main()