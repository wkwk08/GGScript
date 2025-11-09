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

def token_category(tt: str) -> str:
    KEYWORDS = {
        'afk', 'buff', 'build', 'choke', 'choke_clutch', 'clutch', 'comsat',
        'count', 'craft', 'dodge', 'drop', 'elo', 'frag', 'ggwp', 'grind',
        'hop', 'ign', 'lobby', 'nerf', 'noob', 'pick', 'retry', 'role',
        'shout', 'split', 'stack', 'stun', 'surebol', 'tag', 'try'
    }
    if tt in KEYWORDS:
        return "KEYWORD"
    if tt == "identifier":
        return "IDENTIFIER"
    if tt in ("integer", "float", "string", "char"):
        return "LITERAL"
    if tt in {
        '+', '-', '*', '/', '%', '=', '+=', '-=', '*=', '/=', '%=',
        '++', '--', '<', '>', '<=', '>=', '==', '!=', '!', '&&', '||'
    }:
        return "OPERATOR"
    if tt in {
        '(', ')', '[', ']', '{', '}', ',', ';', ':', '.',
    }:
        return "DELIMITER"
    return "OTHER"

def print_tokens_single_pass(tokens):
    """Print tokens (LEXEME, TOKEN, TYPE) and collect lexical error tokens in a single pass."""
    print("\n" + "="*80)
    print(f"{'LEXEME':<40} {'TOKEN':<25} {'TYPE':<12}")
    print("="*80)

    lex_errors = []
    count_visible = 0
    last_line = 0

    for token in tokens:
        tstr = _type_str(token)
        last_line = getattr(token, "line", last_line)

        # skip EOF entirely
        if tstr == TokenType.eof:
            continue

        # always collect error tokens
        if tstr == TokenType.error:
            lex_errors.append(token)

        # skip invisible tokens in the table (but errors already collected)
        if tstr in (TokenType.whitespace, TokenType.comment, TokenType.newline):
            continue

        # visible token
        count_visible += 1
        lexeme = token.value if token.value is not None else tstr
        lexeme = str(lexeme).replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r")
        if len(lexeme) > 38:
            lexeme = lexeme[:35] + "..."
        print(f"{lexeme:<40} {tstr:<25} {token_category(tstr):<12}")

    print("="*80)
    return {
        "visible_count": count_visible,
        "lex_errors": lex_errors,
        "last_line": last_line
    }

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

    stats = print_tokens_single_pass(tokens)

    # Combine token-produced lexical errors and lexer-reported errors, then print once
    token_errors = stats["lex_errors"]
    all_errors = []
    all_errors.extend(token_errors)
    all_errors.extend(errors or [])

    if all_errors:
        print("\nLexical Errors Found:\n")
        for i, err in enumerate(all_errors, 1):
            if hasattr(err, "line") and hasattr(err, "column"):
                print(f"  {i}. Line {err.line}, Column {err.column}: {err.value}")
            elif hasattr(err, "as_string"):
                print(f"  {i}. {err.as_string()}")
            else:
                print(f"  {i}. {err}")
        print("\nLexical analysis failed.")
        sys.exit(1)
    else:
        print("\nLexical analysis completed successfully.")
        print(f"  Visible tokens: {stats['visible_count']}")
        print(f"  Lines processed: {stats['last_line']}")
        print("Compilation stopped after lexical analysis (parser not yet implemented)")
        print("=" * 80)
        sys.exit(0)

if __name__ == "__main__":
    main()