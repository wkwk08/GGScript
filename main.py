import sys
import os
from lexer.lexer import Lexer
from lexer.token_types import TokenType

# ------------------------------------------------------------------
#  Token → string helper
# ------------------------------------------------------------------
def _token_str(tok):
    t = tok.type
    if isinstance(t, str):
        return t
    if hasattr(t, "value"):
        return t.value
    if hasattr(t, "name"):
        return t.name
    return str(t)

# ------------------------------------------------------------------
#  Token categories
# ------------------------------------------------------------------
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
    if tt == "comment":
        return "COMMENT"
    if tt in {
        '+', '-', '*', '/', '%', '=', '+=', '-=', '*=', '/=', '%=',
        '++', '--', '<', '>', '<=', '>=', '==', '!=', '!', '&&', '||'
    }:
        return "OPERATOR"
    if tt in { '(', ')', '[', ']', '{', '}', ',', ';', ':', '.' }:
        return "DELIMITER"
    return "OTHER"

# ------------------------------------------------------------------
#  Print token table
# ------------------------------------------------------------------
def print_token_table(tokens):
    print("\n" + "═" * 90)
    print(f"{'LEXEME':<40} {'TOKEN':<25} {'TYPE':<12}")
    print("─" * 90)

    visible = 0
    last_line = 0

    for t in tokens:
        tstr = _token_str(t)
        last_line = getattr(t, "line", last_line)

        # Skip invisible tokens
        if tstr in (TokenType.eof, TokenType.newline, TokenType.whitespace):
            continue
        if tstr == TokenType.comment:
            continue

        visible += 1
        lexeme = t.value if t.value is not None else tstr
        lexeme = str(lexeme).replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r")
        if len(lexeme) > 38:
            lexeme = lexeme[:35] + "..."

        token_display = tstr if tstr != "comment" else lexeme
        print(f"{lexeme:<40} {token_display:<25} {token_category(tstr):<12}")

    print("═" * 90)
    return {"visible": visible, "lines": last_line}

# ------------------------------------------------------------------
#  Print lexical errors
# ------------------------------------------------------------------
def print_errors(errors):
    if not errors:
        return
    print("\nLexical Errors Found:\n")
    for i, e in enumerate(errors, 1):
        if hasattr(e, "as_string"):
            print(f"  {i}. {e.as_string()}")
        elif hasattr(e, "line") and hasattr(e, "column"):
            print(f"  {i}. Line {e.line}, Col {e.column}: {e.value}")
        else:
            print(f"  {i}. {e}")
    print()

# ------------------------------------------------------------------
#  Main – lexical analysis only
# ------------------------------------------------------------------
def main():
    # ----- header -----
    print("═" * 90)
    print("GGScript Lexical Analyzer".center(90))
    print("Automata Theory and Formal Languages".center(90))
    print("═" * 90)

    # ----- input handling -----
    if len(sys.argv) < 2:
        print("\nError: No input file specified")
        print("\nUsage:")
        print("  python main.py <source_file.gg>")
        print("  python main.py --interactive")
        sys.exit(1)

    if sys.argv[1] == "--interactive":
        print("\nInteractive Mode")
        print("Enter GGScript code (Ctrl+D / Ctrl+Z+Enter to finish):\n")
        source = sys.stdin.read()
    else:
        path = sys.argv[1]
        if not os.path.exists(path):
            print(f"\nError: File '{path}' not found")
            sys.exit(1)
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
        print(f"\nAnalyzing: {path}")
        print(f"Size: {len(source)} characters")

    # ----- run lexer -----
    print("\n" + "═" * 90)
    print("Lexical Analysis")
    print("═" * 90)

    try:
        lexer = Lexer(source)
        result = lexer.make_tokens() if hasattr(lexer, "make_tokens") else lexer.tokenize()
        tokens, lexer_errors = (result, []) if not isinstance(result, tuple) else result
    except Exception as exc:
        print(f"\nLexer crashed: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # ----- collect all errors (token stream + lexer-reported) -----
    token_errors = [t for t in tokens if _token_str(t) == TokenType.error]
    all_errors = token_errors + (lexer_errors or [])

    # ----- output -----
    if all_errors:
        print_errors(all_errors)
        print_token_table(tokens)          # show table for context
        print("Lexical analysis failed.")
        sys.exit(1)
    else:
        stats = print_token_table(tokens)
        print(f"\nLexical analysis successful!")
        print(f"  Visible tokens : {stats['visible']}")
        print(f"  Lines processed: {stats['lines']}")
        print("═" * 90)
        sys.exit(0)


if __name__ == "__main__":
    main()