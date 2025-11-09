from .token_types import TokenType
from .token import Token

# Constants
ALPHA_LOWER = 'abcdefghijklmnopqrstuvwxyz'
ALPHA_UPPER = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ALPHA = ALPHA_LOWER + ALPHA_UPPER
ZERO = '0'
DIGITS = '123456789'
NUM = ZERO + DIGITS
ALPHANUM = ALPHA + NUM
PUNCTUATIONS = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
ASCII = ALPHANUM + PUNCTUATIONS
OPER = '+-/*%<>=!&|'
WHTSPC = ' \t\n'

# Delimiters
WHTSPC_DLM = ' \t\n' 
TERMI_DLM = WHTSPC_DLM
BRCKT_DLM = WHTSPC_DLM + '()[]{}'
OPRTR_DLM = ALPHANUM + WHTSPC_DLM
CMPLX_DLM = WHTSPC_DLM + ',;) }'
COMMT_DLM = WHTSPC_DLM
IDFR_DLM = WHTSPC_DLM + OPER + ';,.:()[]{}'
INT_DLM = ' ' + OPER
FLT_LIT_DLM = ' ' + PUNCTUATIONS + OPER + ALPHA
STRG_DLM = WHTSPC_DLM + '; ,'
BRC_DLM = WHTSPC_DLM + '{'
COLON_DLM = WHTSPC_DLM + ':'
DOT_DLM = '.();\n'
PRN_BLCK_DLM = WHTSPC_DLM + '(){ }'
PRN_BRC_DLM = WHTSPC_DLM + '({'
PRN_DLM = WHTSPC_DLM + '();'
SEMI_DLM = ';' + WHTSPC_DLM

# Group delimiters
DATATYPE_DLM = WHTSPC_DLM  # dodge, elo, frag, ign, surebol, stun, tag
COND_DLM = PRN_BRC_DLM  # choke clutch, clutch, pick
LOOP_FUNC_DLM = PRN_BLCK_DLM  # build, grind, lobby, retry
JUMP_DLM = SEMI_DLM  # afk, ggwp, hop
BOOL_DLM = CMPLX_DLM  # buff, nerf
DO_ELSE_DLM = BRC_DLM  # choke, try
IO_ARRAY_DLM = PRN_DLM  # comsat, craft, drop, shout, stack
METHOD_DLM = DOT_DLM  # count, split
CASE_DLM = COLON_DLM  # noob, role
SYMBOL_DLM = OPRTR_DLM # plus, minus, mul, div, mod, assign, lt, gt, eq, neq, and, or
QUOTE_DLM = STRG_DLM # string and char literals
SEMI_SYM_DLM = TERMI_DLM # for semicolon and symbols
PAREN_DLM = BRCKT_DLM # for parentheses

# Validation constants
MAX_INTEGER = 999999999999999
MIN_INTEGER = -999999999999999
MAX_INTEGER_DIGITS = 15
MAX_FRACTIONAL_DIGITS = 6
MAX_ID_LENGTH = 20
MIN_ID_LENGTH = 1
MAX_UNDERSCORES = 19

class Position:
    def __init__(self, index, ln, col):
        self.index = index
        self.ln = ln
        self.col = col

    def advance(self, current_char):
        self.index += 1
        self.col += 1
        if current_char == '\n':
            self.ln += 1
            self.col = 1
        return self

    def copy(self):
        return Position(self.index, self.ln, self.col)

class LexicalError:
    def __init__(self, pos, details):
        self.pos = pos
        self.details = details

    def as_string(self):
        self.details = self.details.replace('\n', '\\n')
        return f"Ln {self.pos.ln}, Col {self.pos.col} Lexical Error: {self.details}"

class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code + '\n'
        self.pos = Position(-1, 1, 0)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.source_code[self.pos.index] if self.pos.index < len(self.source_code) else None

    def peek(self, offset=1):
        peek_pos = self.pos.index + offset
        if peek_pos < len(self.source_code):
            return self.source_code[peek_pos]
        return None

    def peek_word(self):
        pos = self.pos.index
        while pos < len(self.source_code) and self.source_code[pos].isspace():
            pos += 1
        word = ''
        while pos < len(self.source_code) and (self.source_code[pos].isalnum() or self.source_code[pos] == '_'):
            word += self.source_code[pos]
            pos += 1
        return word

    def make_tokens(self):
        tokens = []
        errors = []
        while self.current_char is not None:
            if self.current_char.isspace():
                if self.current_char == '\n':
                    tokens.append(Token(TokenType.newline, '\\n', self.pos.ln, self.pos.col))
                self.advance()
                continue

            if self.current_char in ALPHA:
                self.make_identifier_or_keyword(tokens, errors)
                continue

            if self.current_char in NUM:
                self.make_number(tokens, errors, positive=True)
                continue

            if self.current_char in '+-':
                self.make_signed_number_or_operator(tokens, errors)
                continue

            if self.current_char == '"':
                self.make_string(tokens, errors)
                continue

            if self.current_char == "'":
                self.make_char(tokens, errors)
                continue

            if self.current_char == '/':
                self.make_comment_or_div_or_div_assign(tokens, errors)
                continue

            if self.current_char == '*':
                self.make_mul_or_mul_assign(tokens, errors)
                continue

            if self.current_char == '%':
                self.make_mod_or_mod_assign(tokens, errors)
                continue

            if self.current_char == '=':
                self.make_assign_or_eq(tokens, errors)
                continue

            if self.current_char == '<':
                self.make_lt_or_lte(tokens, errors)
                continue

            if self.current_char == '>':
                self.make_gt_or_gte(tokens, errors)
                continue

            if self.current_char == '!':
                self.make_not_or_neq(tokens, errors)
                continue

            if self.current_char == '&':
                self.make_and(tokens, errors)
                continue

            if self.current_char == '|':
                self.make_or(tokens, errors)
                continue

            if self.current_char == ',':
                self.make_comma(tokens, errors)
                continue

            if self.current_char == ';':
                self.make_semicolon(tokens, errors)
                continue

            if self.current_char == ':':
                self.make_colon(tokens, errors)
                continue

            if self.current_char == '.':
                self.make_dot_or_fractional(tokens, errors)
                continue

            if self.current_char == '(':
                self.make_lparen(tokens, errors)
                continue

            if self.current_char == ')':
                self.make_rparen(tokens, errors)
                continue

            if self.current_char == '[':
                self.make_lbracket(tokens, errors)
                continue

            if self.current_char == ']':
                self.make_rbracket(tokens, errors)
                continue

            if self.current_char == '{':
                self.make_lbrace(tokens, errors)
                continue

            if self.current_char == '}':
                self.make_rbrace(tokens, errors)
                continue

            errors.append(LexicalError(self.pos.copy(), f"Invalid character '{self.current_char}'"))
            self.advance()

        tokens.append(Token(TokenType.eof, None, self.pos.ln, self.pos.col))
        return tokens, errors

    def make_identifier_or_keyword(self, tokens, errors):
        start_pos = self.pos.copy()
        ident_str = ''
        underscore_count = 0
        consecutive_underscore = False
        previous_char = None

        if not self.current_char.isalpha():
            errors.append(LexicalError(start_pos, "Identifier must start with a letter"))
            self.advance()
            return

        matched = False

        if self.current_char == 'a':
            ident_str += self.current_char
            previous_char = self.current_char
            self.advance()
            if self.current_char == 'f':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'k':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char is None or self.current_char in JUMP_DLM:
                        tokens.append(Token(TokenType.afk, ident_str, start_pos.ln, start_pos.col))
                        matched = True
                    # No else for invalid dlm here, handled below if not matched
        elif self.current_char == 'b':
            ident_str += self.current_char
            previous_char = self.current_char
            self.advance()
            if self.current_char == 'u':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'f':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 'f':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char is None or self.current_char in BOOL_DLM:
                            tokens.append(Token(TokenType.buff, ident_str, start_pos.ln, start_pos.col))
                            matched = True
                elif self.current_char == 'i':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 'l':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char == 'd':
                            ident_str += self.current_char
                            previous_char = self.current_char
                            self.advance()
                            if self.current_char is None or self.current_char in LOOP_FUNC_DLM:
                                tokens.append(Token(TokenType.build, ident_str, start_pos.ln, start_pos.col))
                                matched = True
        elif self.current_char == 'c':
            ident_str += self.current_char
            previous_char = self.current_char
            self.advance()
            if self.current_char == 'h':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'o':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 'k':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char == 'e':
                            ident_str += self.current_char
                            previous_char = self.current_char
                            self.advance()
                            next_word = self.peek_word()
                            if next_word == 'clutch':
                                while self.current_char and self.current_char.isspace():
                                    self.advance()
                                clutch_str = ''
                                while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
                                    clutch_str += self.current_char
                                    self.advance()
                                if clutch_str == 'clutch':
                                    if self.current_char is None or self.current_char in COND_DLM:
                                        tokens.append(Token(TokenType.choke_clutch, 'choke clutch', start_pos.ln, start_pos.col))
                                        matched = True
                                    else:
                                        errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after 'choke clutch'"))
                                        matched = True
                                else:
                                    errors.append(LexicalError(start_pos, f"Invalid after 'choke': '{clutch_str}'"))
                                    matched = True
                            else:
                                if self.current_char is None or self.current_char in DO_ELSE_DLM:
                                    tokens.append(Token(TokenType.choke, ident_str, start_pos.ln, start_pos.col))
                                    matched = True
                elif self.current_char == 'u':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 't':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char == 'c':
                            ident_str += self.current_char
                            previous_char = self.current_char
                            self.advance()
                            if self.current_char == 'h':
                                ident_str += self.current_char
                                previous_char = self.current_char
                                self.advance()
                                if self.current_char is None or self.current_char in COND_DLM:
                                    tokens.append(Token(TokenType.clutch, ident_str, start_pos.ln, start_pos.col))
                                    matched = True
            elif self.current_char == 'o':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'm':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 's':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char == 'a':
                            ident_str += self.current_char
                            previous_char = self.current_char
                            self.advance()
                            if self.current_char == 't':
                                ident_str += self.current_char
                                previous_char = self.current_char
                                self.advance()
                                if self.current_char is None or self.current_char in IO_ARRAY_DLM:
                                    tokens.append(Token(TokenType.comsat, ident_str, start_pos.ln, start_pos.col))
                                    matched = True
                elif self.current_char == 'u':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 'n':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char == 't':
                            ident_str += self.current_char
                            previous_char = self.current_char
                            self.advance()
                            if self.current_char is None or self.current_char in METHOD_DLM:
                                tokens.append(Token(TokenType.count, ident_str, start_pos.ln, start_pos.col))
                                matched = True
            elif self.current_char == 'r':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'a':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 'f':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char == 't':
                            ident_str += self.current_char
                            previous_char = self.current_char
                            self.advance()
                            if self.current_char is None or self.current_char in IO_ARRAY_DLM:
                                tokens.append(Token(TokenType.craft, ident_str, start_pos.ln, start_pos.col))
                                matched = True
        elif self.current_char == 'd':
            ident_str += self.current_char
            previous_char = self.current_char
            self.advance()
            if self.current_char == 'o':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'd':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 'g':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char == 'e':
                            ident_str += self.current_char
                            previous_char = self.current_char
                            self.advance()
                            if self.current_char is None or self.current_char in DATATYPE_DLM:
                                tokens.append(Token(TokenType.dodge, ident_str, start_pos.ln, start_pos.col))
                                matched = True
            elif self.current_char == 'r':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'o':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 'p':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char is None or self.current_char in IO_ARRAY_DLM:
                            tokens.append(Token(TokenType.drop, ident_str, start_pos.ln, start_pos.col))
                            matched = True
        elif self.current_char == 'e':
            ident_str += self.current_char
            previous_char = self.current_char
            self.advance()
            if self.current_char == 'l':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'o':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char is None or self.current_char in DATATYPE_DLM:
                        tokens.append(Token(TokenType.elo, ident_str, start_pos.ln, start_pos.col))
                        matched = True
        elif self.current_char == 'f':
            ident_str += self.current_char
            previous_char = self.current_char
            self.advance()
            if self.current_char == 'r':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'a':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 'g':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char is None or self.current_char in DATATYPE_DLM:
                            tokens.append(Token(TokenType.frag, ident_str, start_pos.ln, start_pos.col))
                            matched = True
        elif self.current_char == 'g':
            ident_str += self.current_char
            previous_char = self.current_char
            self.advance()
            if self.current_char == 'r':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'i':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 'n':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char == 'd':
                            ident_str += self.current_char
                            previous_char = self.current_char
                            self.advance()
                            if self.current_char is None or self.current_char in LOOP_FUNC_DLM:
                                tokens.append(Token(TokenType.grind, ident_str, start_pos.ln, start_pos.col))
                                matched = True
            elif self.current_char == 'g':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'w':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 'p':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char is None or self.current_char in JUMP_DLM:
                            tokens.append(Token(TokenType.ggwp, ident_str, start_pos.ln, start_pos.col))
                            matched = True
        elif self.current_char == 'h':
            ident_str += self.current_char
            previous_char = self.current_char
            self.advance()
            if self.current_char == 'o':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'p':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char is None or self.current_char in JUMP_DLM:
                        tokens.append(Token(TokenType.hop, ident_str, start_pos.ln, start_pos.col))
                        matched = True
        elif self.current_char == 'i':
            ident_str += self.current_char
            previous_char = self.current_char
            self.advance()
            if self.current_char == 'g':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'n':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char is None or self.current_char in DATATYPE_DLM:
                        tokens.append(Token(TokenType.ign, ident_str, start_pos.ln, start_pos.col))
                        matched = True
        elif self.current_char == 'l':
            ident_str += self.current_char
            previous_char = self.current_char
            self.advance()
            if self.current_char == 'o':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'b':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 'b':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char == 'y':
                            ident_str += self.current_char
                            previous_char = self.current_char
                            self.advance()
                            if self.current_char is None or self.current_char in LOOP_FUNC_DLM:
                                tokens.append(Token(TokenType.lobby, ident_str, start_pos.ln, start_pos.col))
                                matched = True
        elif self.current_char == 'n':
            ident_str += self.current_char
            previous_char = self.current_char
            self.advance()
            if self.current_char == 'e':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'r':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 'f':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char is None or self.current_char in BOOL_DLM:
                            tokens.append(Token(TokenType.nerf, ident_str, start_pos.ln, start_pos.col))
                            matched = True
            elif self.current_char == 'o':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'o':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 'b':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char is None or self.current_char in CASE_DLM:
                            tokens.append(Token(TokenType.noob, ident_str, start_pos.ln, start_pos.col))
                            matched = True
        elif self.current_char == 'p':
            ident_str += self.current_char
            previous_char = self.current_char
            self.advance()
            if self.current_char == 'i':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'c':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 'k':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char is None or self.current_char in COND_DLM:
                            tokens.append(Token(TokenType.pick, ident_str, start_pos.ln, start_pos.col))
                            matched = True
        elif self.current_char == 'r':
            ident_str += self.current_char
            previous_char = self.current_char
            self.advance()
            if self.current_char == 'o':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'l':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 'e':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char is None or self.current_char in CASE_DLM:
                            tokens.append(Token(TokenType.role, ident_str, start_pos.ln, start_pos.col))
                            matched = True
            elif self.current_char == 'e':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 't':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 'r':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char == 'y':
                            ident_str += self.current_char
                            previous_char = self.current_char
                            self.advance()
                            if self.current_char is None or self.current_char in LOOP_FUNC_DLM:
                                tokens.append(Token(TokenType.retry, ident_str, start_pos.ln, start_pos.col))
                                matched = True
        elif self.current_char == 's':
            ident_str += self.current_char
            previous_char = self.current_char
            self.advance()
            if self.current_char == 'u':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'r':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 'e':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char == 'b':
                            ident_str += self.current_char
                            previous_char = self.current_char
                            self.advance()
                            if self.current_char == 'o':
                                ident_str += self.current_char
                                previous_char = self.current_char
                                self.advance()
                                if self.current_char == 'l':
                                    ident_str += self.current_char
                                    previous_char = self.current_char
                                    self.advance()
                                    if self.current_char is None or self.current_char in DATATYPE_DLM:
                                        tokens.append(Token(TokenType.surebol, ident_str, start_pos.ln, start_pos.col))
                                        matched = True
            elif self.current_char == 'h':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'o':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 'u':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char == 't':
                            ident_str += self.current_char
                            previous_char = self.current_char
                            self.advance()
                            if self.current_char is None or self.current_char in IO_ARRAY_DLM:
                                tokens.append(Token(TokenType.shout, ident_str, start_pos.ln, start_pos.col))
                                matched = True
            elif self.current_char == 't':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'u':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 'n':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char is None or self.current_char in DATATYPE_DLM:
                            tokens.append(Token(TokenType.stun, ident_str, start_pos.ln, start_pos.col))
                            matched = True
            elif self.current_char == 't':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'a':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 'c':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char == 'k':
                            ident_str += self.current_char
                            previous_char = self.current_char
                            self.advance()
                            if self.current_char is None or self.current_char in IO_ARRAY_DLM:
                                tokens.append(Token(TokenType.stack, ident_str, start_pos.ln, start_pos.col))
                                matched = True
            elif self.current_char == 'p':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'l':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char == 'i':
                        ident_str += self.current_char
                        previous_char = self.current_char
                        self.advance()
                        if self.current_char == 't':
                            ident_str += self.current_char
                            previous_char = self.current_char
                            self.advance()
                            if self.current_char is None or self.current_char in METHOD_DLM:
                                tokens.append(Token(TokenType.split, ident_str, start_pos.ln, start_pos.col))
                                matched = True
        elif self.current_char == 't':
            ident_str += self.current_char
            previous_char = self.current_char
            self.advance()
            if self.current_char == 'a':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'g':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char is None or self.current_char in DATATYPE_DLM:
                        tokens.append(Token(TokenType.tag, ident_str, start_pos.ln, start_pos.col))
                        matched = True
            elif self.current_char == 'r':
                ident_str += self.current_char
                previous_char = self.current_char
                self.advance()
                if self.current_char == 'y':
                    ident_str += self.current_char
                    previous_char = self.current_char
                    self.advance()
                    if self.current_char is None or self.current_char in DO_ELSE_DLM:
                        tokens.append(Token(TokenType.try_, ident_str, start_pos.ln, start_pos.col))
                        matched = True
        # For letters without keywords (e.g., 'q', 'v', etc.), just build identifier
        else:
            ident_str += self.current_char
            previous_char = self.current_char
            self.advance()

        if not matched:
            # Continue collecting valid identifier characters
            while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
                ident_str += self.current_char
                self.advance()

            # Validate identifier rules
            if (
                ident_str[0] in ALPHA and
                all(c in ALPHANUM + '_' for c in ident_str) and
                MIN_ID_LENGTH <= len(ident_str) <= MAX_ID_LENGTH and
                ident_str.count('_') <= MAX_UNDERSCORES
            ):
                tokens.append(Token(TokenType.identifier, ident_str, start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid identifier '{ident_str}'"))
       
    def make_number(self, tokens, errors, positive=True):
        start_pos = self.pos.copy()
        num_str = '' if positive else '-'
        digit_count = 0
        is_float = False

        while self.current_char and self.current_char.isdigit():
            num_str += self.current_char
            digit_count += 1
            self.advance()
            if digit_count > MAX_INTEGER_DIGITS:
                errors.append(LexicalError(start_pos, f"Integer part too long (max {MAX_INTEGER_DIGITS} digits)"))
                return

        if self.current_char == '.':
            is_float = True
            num_str += '.'
            self.advance()
            frac_count = 0
            while self.current_char and self.current_char.isdigit():
                num_str += self.current_char
                frac_count += 1
                self.advance()
                if frac_count > MAX_FRACTIONAL_DIGITS:
                    errors.append(LexicalError(start_pos, f"Fractional part too long (max {MAX_FRACTIONAL_DIGITS} digits)"))
                    return

        if is_float and self.current_char and self.current_char.lower() == 'e':
            num_str += self.current_char
            self.advance()
            if self.current_char in '+-':
                num_str += self.current_char
                self.advance()
            if not self.current_char or not self.current_char.isdigit():
                errors.append(LexicalError(start_pos, "Expected digits after 'e' in scientific notation"))
                return
            while self.current_char and self.current_char.isdigit():
                num_str += self.current_char
                self.advance()

        dlm = FLT_LIT_DLM if is_float else INT_DLM
        if self.current_char is None or self.current_char in dlm:
            if is_float:
                try:
                    value = float(num_str)
                    tokens.append(Token(TokenType.float_, value, start_pos.ln, start_pos.col))
                except ValueError:
                    errors.append(LexicalError(start_pos, f"Invalid float literal '{num_str}'"))
            else:
                try:
                    value = int(num_str)
                    if value < MIN_INTEGER or value > MAX_INTEGER:
                        errors.append(LexicalError(start_pos, f"Integer out of range (±{MAX_INTEGER}): '{num_str}'"))
                    else:
                        tokens.append(Token(TokenType.integer, value, start_pos.ln, start_pos.col))
                except ValueError:
                    errors.append(LexicalError(start_pos, f"Invalid integer literal '{num_str}'"))
        else:
            errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after number '{num_str}'"))
            
    def validate_number_limits(num_str, is_integer, start_pos, errors):
        if is_integer:
            if len(num_str.lstrip('-')) > MAX_INTEGER_DIGITS:
                errors.append(LexicalError(start_pos, f"frag value exceeds {MAX_INTEGER_DIGITS} digits"))
            else:
                int_part, _, frac_part = num_str.partition('.')
                if len(frac_part) > MAX_FRACTIONAL_DIGITS:
                    errors.append(LexicalError(start_pos, f"elo fractional part exceeds {MAX_FRACTIONAL_DIGITS} digits"))

    def make_signed_number_or_operator(self, tokens, errors):
        start_pos = self.pos.copy()
        sign = self.current_char
        self.advance()
        if sign == '+':
            if self.current_char == '+':
                self.advance()
                if self.current_char is None or self.current_char in SYMBOL_DLM:
                    tokens.append(Token(TokenType.increment, '++', start_pos.ln, start_pos.col))
                else:
                    errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '++'"))
                return
            elif self.current_char == '=':
                self.advance()
                if self.current_char is None or self.current_char in SYMBOL_DLM:
                    tokens.append(Token(TokenType.plus_assign, '+=', start_pos.ln, start_pos.col))
                else:
                    errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '+='"))
                return
            elif self.current_char.isdigit():
                self.make_number(tokens, errors, positive=True)
                return
            elif self.current_char == '.' and self.peek() and self.peek().isdigit():
                num_str = '+0.'
                self.advance()  # .
                frac_count = 0
                while self.current_char and self.current_char.isdigit():
                    num_str += self.current_char
                    frac_count += 1
                    self.advance()
                    if frac_count > MAX_FRACTIONAL_DIGITS:
                        errors.append(LexicalError(start_pos, f"Fractional part too long (max {MAX_FRACTIONAL_DIGITS} digits)"))
                        return
                if self.current_char and self.current_char.lower() == 'e':
                    num_str += self.current_char
                    self.advance()
                    if self.current_char in '+-':
                        num_str += self.current_char
                        self.advance()
                    if not self.current_char or not self.current_char.isdigit():
                        errors.append(LexicalError(start_pos, "Expected digits after 'e'"))
                        return
                    while self.current_char and self.current_char.isdigit():
                        num_str += self.current_char
                        self.advance()
                if self.current_char is None or self.current_char in FLT_LIT_DLM:
                    try:
                        value = float(num_str)
                        tokens.append(Token(TokenType.float_, value, start_pos.ln, start_pos.col))
                    except ValueError:
                        errors.append(LexicalError(start_pos, f"Invalid float '{num_str}'"))
                else:
                    errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after float '{num_str}'"))
                return
            else:
                if self.current_char is None or self.current_char in SYMBOL_DLM:
                    tokens.append(Token(TokenType.plus, '+', start_pos.ln, start_pos.col))
                else:
                    errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '+'"))
                return
        elif sign == '-':
            if self.current_char == '-':
                self.advance()
                if self.current_char is None or self.current_char in SYMBOL_DLM:
                    tokens.append(Token(TokenType.decrement, '--', start_pos.ln, start_pos.col))
                else:
                    errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '--'"))
                return
            elif self.current_char == '=':
                self.advance()
                if self.current_char is None or self.current_char in SYMBOL_DLM:
                    tokens.append(Token(TokenType.minus_assign, '-=', start_pos.ln, start_pos.col))
                else:
                    errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '-='"))
                return
            elif self.current_char.isdigit():
                self.make_number(tokens, errors, positive=False)
                return
            elif self.current_char == '.' and self.peek() and self.peek().isdigit():
                num_str = '-0.'
                self.advance()  # .
                frac_count = 0
                while self.current_char and self.current_char.isdigit():
                    num_str += self.current_char
                    frac_count += 1
                    self.advance()
                    if frac_count > MAX_FRACTIONAL_DIGITS:
                        errors.append(LexicalError(start_pos, f"Fractional part too long (max {MAX_FRACTIONAL_DIGITS} digits)"))
                        return
                if self.current_char and self.current_char.lower() == 'e':
                    num_str += self.current_char
                    self.advance()
                    if self.current_char in '+-':
                        num_str += self.current_char
                        self.advance()
                    if not self.current_char or not self.current_char.isdigit():
                        errors.append(LexicalError(start_pos, "Expected digits after 'e'"))
                        return
                    while self.current_char and self.current_char.isdigit():
                        num_str += self.current_char
                        self.advance()
                if self.current_char is None or self.current_char in FLT_LIT_DLM:
                    try:
                        value = float(num_str)
                        tokens.append(Token(TokenType.float_, value, start_pos.ln, start_pos.col))
                    except ValueError:
                        errors.append(LexicalError(start_pos, f"Invalid float '{num_str}'"))
                else:
                    errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after float '{num_str}'"))
                return
            else:
                if self.current_char is None or self.current_char in SYMBOL_DLM:
                    tokens.append(Token(TokenType.minus, '-', start_pos.ln, start_pos.col))
                else:
                    errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '-'"))
                return

    def make_string(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # "
        string_value = ''
        while self.current_char and self.current_char != '"':
            if self.current_char == '\\':
                self.advance()
                if self.current_char in 'ntr"\\':
                    escape_map = {'n': '\n', 't': '\t', 'r': '\r', '"': '"', '\\': '\\'}
                    string_value += escape_map.get(self.current_char, self.current_char)
                    self.advance()
                else:
                    errors.append(LexicalError(start_pos, f"Invalid escape sequence \\{self.current_char}"))
                    return
            elif self.current_char == '\n':
                errors.append(LexicalError(start_pos, "String literal cannot span multiple lines without \\n"))
                return
            else:
                string_value += self.current_char
                self.advance()
        if self.current_char == '"':
            self.advance()
            if self.current_char is None or self.current_char in STRG_DLM:
                tokens.append(Token(TokenType.string, string_value, start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after string"))
        else:
            errors.append(LexicalError(start_pos, "Unterminated string literal"))

    def make_char(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # '
        char_value = ''
        if not self.current_char:
            errors.append(LexicalError(start_pos, "Unterminated character literal"))
            return
        if self.current_char == "'":
            self.advance()
            errors.append(LexicalError(start_pos, "Empty character literal"))
            return
        if self.current_char == '\\':
            self.advance()
            if self.current_char in 'ntr\'\\':
                escape_map = {'n': '\n', 't': '\t', 'r': '\r', "'": "'", '\\': '\\'}
                char_value += escape_map.get(self.current_char, self.current_char)
                self.advance()
            else:
                errors.append(LexicalError(start_pos, f"Invalid escape sequence \\{self.current_char}"))
                return
        else:
            char_value += self.current_char
            self.advance()
        if self.current_char == "'":
            self.advance()
            if len(char_value) != 1:
                errors.append(LexicalError(start_pos, "Character literal must be a single character"))
                return
            if self.current_char is None or self.current_char in STRG_DLM:  # Reuse STRG_DLM for char
                tokens.append(Token(TokenType.char, char_value, start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after character literal"))
        else:
            errors.append(LexicalError(start_pos, "Unterminated character literal"))

    def make_comment_or_div_or_div_assign(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # /
        if self.current_char == '*':
            self.advance()  # *
            while self.current_char:
                if self.current_char == '*' and self.peek() == '/':
                    self.advance()  # *
                    self.advance()  # /
                    break
                elif self.current_char == '\n':
                    break
                self.advance()
        elif self.current_char == '=':
            self.advance()
            if self.current_char is None or self.current_char in SYMBOL_DLM:
                tokens.append(Token(TokenType.div_assign, '/=', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '/='"))
        else:
            if self.current_char is None or self.current_char in SYMBOL_DLM:
                tokens.append(Token(TokenType.div, '/', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '/'"))

    def make_mul_or_mul_assign(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # *
        if self.current_char == '=':
            self.advance()
            if self.current_char is None or self.current_char in SYMBOL_DLM:
                tokens.append(Token(TokenType.mul_assign, '*=', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '*='"))
        else:
            if self.current_char is None or self.current_char in SYMBOL_DLM:
                tokens.append(Token(TokenType.mul, '*', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '*'"))

    def make_mod_or_mod_assign(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # %
        if self.current_char == '=':
            self.advance()
            if self.current_char is None or self.current_char in SYMBOL_DLM:
                tokens.append(Token(TokenType.mod_assign, '%=', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '%='"))
        else:
            if self.current_char is None or self.current_char in SYMBOL_DLM:
                tokens.append(Token(TokenType.mod, '%', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '%'"))

    def make_assign_or_eq(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # =
        if self.current_char == '=':
            self.advance()
            if self.current_char is None or self.current_char in SYMBOL_DLM:
                tokens.append(Token(TokenType.eq, '==', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '=='"))
        else:
            if self.current_char is None or self.current_char in SYMBOL_DLM:
                tokens.append(Token(TokenType.assign, '=', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '='"))

    def make_lt_or_lte(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # <
        if self.current_char == '=':
            self.advance()
            if self.current_char is None or self.current_char in SYMBOL_DLM:
                tokens.append(Token(TokenType.lte, '<=', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '<='"))
        else:
            if self.current_char is None or self.current_char in SYMBOL_DLM:
                tokens.append(Token(TokenType.lt, '<', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '<'"))

    def make_gt_or_gte(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # >
        if self.current_char == '=':
            self.advance()
            if self.current_char is None or self.current_char in SYMBOL_DLM:
                tokens.append(Token(TokenType.gte, '>=', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '>='"))
        else:
            if self.current_char is None or self.current_char in SYMBOL_DLM:
                tokens.append(Token(TokenType.gt, '>', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '>'"))

    def make_not_or_neq(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # !
        if self.current_char == '=':
            self.advance()
            if self.current_char is None or self.current_char in SYMBOL_DLM:
                tokens.append(Token(TokenType.neq, '!=', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '!='"))
        else:
            if self.current_char is None or self.current_char in SYMBOL_DLM:
                tokens.append(Token(TokenType.not_, '!', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '!'"))

    def make_and(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # &
        if self.current_char == '&':
            self.advance()
            if self.current_char is None or self.current_char in SYMBOL_DLM:
                tokens.append(Token(TokenType.and_, '&&', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '&&'"))
        else:
            errors.append(LexicalError(start_pos, "Invalid '&' (expected '&&')"))

    def make_or(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # |
        if self.current_char == '|':
            self.advance()
            if self.current_char is None or self.current_char in SYMBOL_DLM:
                tokens.append(Token(TokenType.or_, '||', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '||'"))
        else:
            errors.append(LexicalError(start_pos, "Invalid '|' (expected '||')"))

    def make_comma(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # ,
        if self.current_char is None or self.current_char in SYMBOL_DLM:
            tokens.append(Token(TokenType.comma, ',', start_pos.ln, start_pos.col))
        else:
            errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after ','"))

    def make_semicolon(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # ;
        if self.current_char is None or self.current_char in SEMI_SYM_DLM:
            tokens.append(Token(TokenType.semicolon, ';', start_pos.ln, start_pos.col))
        else:
            errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after ';'"))

    def make_colon(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # :
        if self.current_char is None or self.current_char in COLON_DLM:
            tokens.append(Token(TokenType.colon, ':', start_pos.ln, start_pos.col))
        else:
            errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after ':'"))

    def make_dot_or_fractional(self, tokens, errors):
        start_pos = self.pos.copy()
        if self.peek() and self.peek().isdigit():
            num_str = '0.'
            self.advance()  # .
            frac_count = 0
            while self.current_char and self.current_char.isdigit():
                num_str += self.current_char
                frac_count += 1
                self.advance()
                if frac_count > MAX_FRACTIONAL_DIGITS:
                    errors.append(LexicalError(start_pos, f"Fractional part too long (max {MAX_FRACTIONAL_DIGITS} digits)"))
                    return
            if self.current_char and self.current_char.lower() == 'e':
                num_str += self.current_char
                self.advance()
                if self.current_char in '+-':
                    num_str += self.current_char
                    self.advance()
                if not self.current_char or not self.current_char.isdigit():
                    errors.append(LexicalError(start_pos, "Expected digits after 'e'"))
                    return
                while self.current_char and self.current_char.isdigit():
                    num_str += self.current_char
                    self.advance()
            if self.current_char is None or self.current_char in FLT_LIT_DLM:
                try:
                    value = float(num_str)
                    tokens.append(Token(TokenType.float_, value, start_pos.ln, start_pos.col))
                except ValueError:
                    errors.append(LexicalError(start_pos, f"Invalid float '{num_str}'"))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after float '{num_str}'"))
        else:
            self.advance()  # .
            if self.current_char is None or self.current_char in DOT_DLM:
                tokens.append(Token(TokenType.dot, '.', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '.'"))

    def make_lparen(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # (
        if self.current_char is None or self.current_char in PAREN_DLM:
            tokens.append(Token(TokenType.lparen, '(', start_pos.ln, start_pos.col))
        else:
            errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '('"))

    def make_rparen(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # )
        if self.current_char is None or self.current_char in PAREN_DLM:
            tokens.append(Token(TokenType.rparen, ')', start_pos.ln, start_pos.col))
        else:
            errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after ')'"))

    def make_lbracket(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # [
        if self.current_char is None or self.current_char in PAREN_DLM:
            tokens.append(Token(TokenType.lbracket, '[', start_pos.ln, start_pos.col))
        else:
            errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '['"))

    def make_rbracket(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # ]
        if self.current_char is None or self.current_char in PAREN_DLM:
            tokens.append(Token(TokenType.rbracket, ']', start_pos.ln, start_pos.col))
        else:
            errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after ']'"))

    def make_lbrace(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # {
        if self.current_char is None or self.current_char in PAREN_DLM:
            tokens.append(Token(TokenType.lbrace, '{', start_pos.ln, start_pos.col))
        else:
            errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '{{'"))

    def make_rbrace(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # }
        if self.current_char is None or self.current_char in PAREN_DLM:
            tokens.append(Token(TokenType.rbrace, '}', start_pos.ln, start_pos.col))
        else:
            errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '}}'"))