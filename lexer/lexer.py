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

RESERVED_KEYWORDS = {
    'afk', 'buff', 'build', 'choke', 'choke clutch', 'clutch', 'comsat',
    'count', 'craft', 'dodge', 'drop', 'elo', 'frag', 'ggwp', 'grind',
    'hop', 'ign', 'lobby', 'nerf', 'noob', 'pick', 'retry',
    'role', 'shout', 'split', 'stack', 'stun', 'surebol', 'tag', 'try'
}

# Delimiters
WHTSPC_DLM = ' \t\n' 
TERMI_DLM = WHTSPC_DLM
OPBRCKT_DLM = WHTSPC_DLM + ALPHANUM + '('  # open brackets
CLBRCKT_DLM = WHTSPC_DLM + ALPHANUM + ')' + '}'   # close brackets
OPRTR_DLM = ALPHANUM + WHTSPC_DLM
CMPLX_DLM = WHTSPC_DLM + ',;)]}'
COMM_STRt_DLM = WHTSPC_DLM + ASCII
COMM_END_DLM = WHTSPC_DLM
ARITH_OPRTR = '+-*/%'
REL_OPRTR   = '<>!='   # raw chars; compound handled in make_* methods
ASSGN_OPRTR = '='      # compound handled in make_* methods
LOGIC_OPRTR = '!&|'
IDFR_DLM = WHTSPC_DLM + ARITH_OPRTR + REL_OPRTR + LOGIC_OPRTR
INT_FLT_DLM = WHTSPC_DLM + ARITH_OPRTR + REL_OPRTR + LOGIC_OPRTR + ';' + ',' + ')]}'
STRG_DLM = WHTSPC_DLM + ';,)'
BRC_DLM = WHTSPC_DLM + '{'
COLON_DLM = WHTSPC_DLM + ':'
DOT_DLM = '.();\n'
PRN_BLCK_DLM = WHTSPC_DLM + '(){ }'
PRN_BRC_DLM = WHTSPC_DLM + '({'
PRN_DLM = WHTSPC_DLM + '('
SEMI_DLM = ';' + WHTSPC_DLM

# Group delimiters
DATATYPE_DLM = WHTSPC_DLM              # frag, elo, ign, surebol, tag, stun
COND_DLM = WHTSPC_DLM + '({'           # clutch, choke clutch, pick, dodge
LOOP_FUNC_DLM = WHTSPC_DLM + '(){}'    # build, grind, lobby, retry
JUMP_DLM = SEMI_DLM                    # afk, ggwp, hop
BOOL_DLM = CMPLX_DLM                   # buff, nerf
DO_ELSE_DLM = WHTSPC_DLM + '{'         # choke, try
OP_PRN_DLM = WHTSPC_DLM + ALPHANUM + '()"' # comsat, craft, drop, shout, stack
METHOD_DLM = WHTSPC_DLM + '.'          # count, split
CASE_DLM = WHTSPC_DLM + ':'            # noob, role
SYMBOL_DLM = OPRTR_DLM # plus, minus, mul, div, mod, assign, lt, gt, eq, neq, and, or
QUOTE_DLM = STRG_DLM # string and char literals
SEMI_SYM_DLM = TERMI_DLM # for semicolon and symbols
PAREN_DLM = OPBRCKT_DLM + CLBRCKT_DLM # for parentheses and brackets

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

            if self.current_char in '+':
                self.make_plus_or_increment(tokens, errors)
                continue

            if self.current_char == '-':
                self.make_minus_or_decrement(tokens, errors)
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
    
    def make_plus_or_increment(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # consume '+'
        if self.current_char == '+':  # increment
            self.advance()
            if self.current_char is None or self.current_char in CMPLX_DLM:
                tokens.append(Token(TokenType.increment, '++', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '++'"))
        elif self.current_char == '=':  # plus-assign
            self.advance()
            if self.current_char is None or self.current_char in OPRTR_DLM:
                tokens.append(Token(TokenType.plus_assign, '+=', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '+='"))
        elif self.current_char in NUM or self.current_char == '.':  # positive number literal
            self.make_number(tokens, errors, positive=True)
        else:  # plain '+'
            if self.current_char is None or self.current_char in OPRTR_DLM:
                tokens.append(Token(TokenType.plus, '+', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '+'"))
                self.advance()

    def make_minus_or_decrement(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # consume '-'
        if self.current_char == '-':  # decrement
            self.advance()
            if self.current_char is None or self.current_char in CMPLX_DLM:
                tokens.append(Token(TokenType.decrement, '--', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '--'"))
        elif self.current_char == '=':  # minus-assign
            self.advance()
            if self.current_char is None or self.current_char in OPRTR_DLM:
                tokens.append(Token(TokenType.minus_assign, '-=', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '-='"))
        elif self.current_char in NUM or self.current_char == '.':  # negative number literal
            self.make_number(tokens, errors, positive=False)
        else:  # plain '-'
            if self.current_char is None or self.current_char in OPRTR_DLM:
                tokens.append(Token(TokenType.minus, '-', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '-'"))
                self.advance()

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

            # clutch branch (starts with 'cl')
            if self.current_char == 'l':
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

            # choke branch (starts with 'ch')
            elif self.current_char == 'h':
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

                            # peek ahead for compound 'choke clutch'
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
                                if self.current_char is None or self.current_char in OP_PRN_DLM:
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
                            if self.current_char is None or self.current_char in OP_PRN_DLM:
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
                            if self.current_char is None or self.current_char in COND_DLM:
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
                        if self.current_char is None or self.current_char in OP_PRN_DLM:
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
                        if self.current_char is None or self.current_char in CASE_DLM + SEMI_DLM:
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
                            if self.current_char is None or self.current_char in OP_PRN_DLM:
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

                elif self.current_char == 'a':
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
                            if self.current_char is None or self.current_char in OP_PRN_DLM:
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

            # Reserved keyword protection
            if ident_str in RESERVED_KEYWORDS:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                matched = True

            # Validate identifier rules
            elif not ident_str[0].isalpha():
                errors.append(LexicalError(start_pos, f"Identifier '{ident_str}' must start with a letter"))
                matched = True

            elif len(ident_str) < MIN_ID_LENGTH or len(ident_str) > MAX_ID_LENGTH:
                errors.append(LexicalError(start_pos, f"Identifier '{ident_str}' length must be between {MIN_ID_LENGTH} and {MAX_ID_LENGTH} characters"))
                matched = True

            elif ident_str.count('_') > MAX_UNDERSCORES:
                errors.append(LexicalError(start_pos, f"Identifier '{ident_str}' has too many underscores (max {MAX_UNDERSCORES})"))
                matched = True

            elif not all(c in ALPHANUM + '_' for c in ident_str):
                errors.append(LexicalError(start_pos, f"Identifier '{ident_str}' contains invalid characters"))
                matched = True

            else:
                tokens.append(Token(TokenType.identifier, ident_str, start_pos.ln, start_pos.col))
                matched = True
       
    def make_number(self, tokens, errors, positive=True):
        start_pos = self.pos.copy()
        num_str = ''
        is_float = False

        # Preserve sign from previous character
        prev_char = self.source_code[self.pos.index - 1]
        if not positive:
            num_str = '-'
        elif prev_char == '+':
            num_str = '+'

        # Integer part
        digit_count = 0
        while self.current_char and self.current_char.isdigit():
            digit_count += 1
            num_str += self.current_char
            self.advance()

            if digit_count == MAX_INTEGER_DIGITS:
                # Raise error at 15 digits
                errors.append(LexicalError(
                    start_pos,
                    f"Integer part too long (max {MAX_INTEGER_DIGITS} digits)"
                ))
                # Reset counters
                num_str = ''
                digit_count = 0

                # Tokenize the next digit separately
                if self.current_char and self.current_char.isdigit():
                    tokens.append(Token(TokenType.integer, self.current_char,
                                        self.pos.ln, self.pos.col))
                    self.advance()

                # Restart counting for the next run
                continue

        # Fractional part
        if self.current_char == '.':
            is_float = True
            self.advance()
            frac_count = 0
            frac_digits = ''
            while self.current_char and self.current_char.isdigit():
                frac_count += 1
                if frac_count <= MAX_FRACTIONAL_DIGITS:
                    frac_digits += self.current_char
                    self.advance()
                else:
                    # Raise error at overflow
                    errors.append(LexicalError(
                        start_pos,
                        f"Fractional part too long (max {MAX_FRACTIONAL_DIGITS} digits)"
                    ))
                    # Emit the valid fractional part once
                    if frac_digits:
                        tokens.append(Token(TokenType.float, num_str + '.' + frac_digits,
                                            start_pos.ln, start_pos.col))
                        frac_digits = ''
                    # Emit each overflow digit separately
                    while self.current_char and self.current_char.isdigit():
                        tokens.append(Token(TokenType.float, self.current_char,
                                            self.pos.ln, self.pos.col))
                        self.advance()
                    break

            # Emit if we collected digits but didn’t overflow
            if frac_digits:
                tokens.append(Token(TokenType.float, num_str + '.' + frac_digits,
                                    start_pos.ln, start_pos.col))
            return

        # Invalid trailing identifier check
        if self.current_char is not None and (self.current_char.isalpha() or self.current_char == '_'):
            errors.append(LexicalError(
                start_pos,
                f"Invalid character '{self.current_char}' after number '{num_str}'"
            ))
            self.advance()
            return

        # Validate delimiter for completed number
        if self.current_char is None or self.current_char in INT_FLT_DLM:
            if is_float:
                try:
                    float(num_str)
                    tokens.append(Token(TokenType.float, num_str,
                                        start_pos.ln, start_pos.col))
                except ValueError:
                    errors.append(LexicalError(start_pos,
                                            f"Invalid float literal '{num_str}'"))
            else:
                try:
                    value = int(num_str)
                    if value < MIN_INTEGER or value > MAX_INTEGER:
                        errors.append(LexicalError(
                            start_pos,
                            f"Integer out of range (±{MAX_INTEGER}): '{num_str}'"
                        ))
                    elif num_str:  # only emit if not empty
                        tokens.append(Token(TokenType.integer, num_str,
                                            start_pos.ln, start_pos.col))
                except ValueError:
                    errors.append(LexicalError(start_pos,
                                            f"Invalid integer literal '{num_str}'"))


    def validate_number_limits(num_str, is_integer, start_pos, errors):
        int_part, _, frac_part = num_str.partition('.')

        if is_integer and len(int_part.lstrip('-')) > MAX_INTEGER_DIGITS:
            errors.append(LexicalError(
                start_pos,
                f"Integer part too long (max {MAX_INTEGER_DIGITS} digits)"
            ))

        if frac_part and len(frac_part) > MAX_FRACTIONAL_DIGITS:
            errors.append(LexicalError(
                start_pos,
                f"Fractional part too long (max {MAX_FRACTIONAL_DIGITS} digits)"
            ))

    def make_signed_number_or_operator(self, tokens, errors):
        start_pos = self.pos.copy()
        sign = self.current_char
        self.advance()
        if sign == '+':
            if self.current_char == '+':
                self.advance()
                if self.current_char is None or self.current_char in OPRTR_DLM:
                    tokens.append(Token(TokenType.increment, '++', start_pos.ln, start_pos.col))
                else:
                    errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '++'"))
                return
            elif self.current_char == '=':
                self.advance()
                if self.current_char is None or self.current_char in OPRTR_DLM:
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
                if self.current_char is None or self.current_char in INT_FLT_DLM:
                    try:
                        value = float(num_str)
                        tokens.append(Token(TokenType.float, value, start_pos.ln, start_pos.col))
                    except ValueError:
                        errors.append(LexicalError(start_pos, f"Invalid float '{num_str}'"))
                else:
                    errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after float '{num_str}'"))
                return
            else:
                if self.current_char is None or self.current_char in OPRTR_DLM:
                    tokens.append(Token(TokenType.plus, '+', start_pos.ln, start_pos.col))
                else:
                    errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '+'"))
                return
        elif sign == '-':
            if self.current_char == '-':
                self.advance()
                if self.current_char is None or self.current_char in OPRTR_DLM:
                    tokens.append(Token(TokenType.decrement, '--', start_pos.ln, start_pos.col))
                else:
                    errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '--'"))
                return
            elif self.current_char == '=':
                self.advance()
                if self.current_char is None or self.current_char in OPRTR_DLM:
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
                if self.current_char is None or self.current_char in INT_FLT_DLM:
                    try:
                        value = float(num_str)
                        tokens.append(Token(TokenType.float, value, start_pos.ln, start_pos.col))
                    except ValueError:
                        errors.append(LexicalError(start_pos, f"Invalid float '{num_str}'"))
                else:
                    errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after float '{num_str}'"))
                return
            else:
                if self.current_char is None or self.current_char in OPRTR_DLM:
                    tokens.append(Token(TokenType.minus, '-', start_pos.ln, start_pos.col))
                else:
                    errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '-'"))
                return

    def make_string(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # "

        # Handle standalone or unterminated quote
        if self.current_char is None or self.current_char == '\n':
            errors.append(LexicalError(start_pos, "Unterminated string literal"))
            return
        
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
                tokens.append(Token(TokenType.string, f'"{string_value}"', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after string"))
        else:
            errors.append(LexicalError(start_pos, "Unterminated string literal"))

    def make_char(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # skip opening '

        if self.current_char is None or self.current_char == '\n':
            errors.append(LexicalError(start_pos, "Unterminated character literal"))
            return

        if self.current_char == "'":
            self.advance()
            errors.append(LexicalError(start_pos, "Empty character literal is not allowed"))
            return

        char_value = self.current_char
        self.advance()

        if self.current_char != "'":
            errors.append(LexicalError(start_pos, "Unterminated character literal"))
            while self.current_char and self.current_char != "'":
                self.advance()
            if self.current_char == "'":
                self.advance()
            return

        self.advance()

        if not char_value.isalpha() or not char_value.isupper():
            errors.append(LexicalError(start_pos, "Character literal must be a single uppercase letter A–Z"))
            while self.current_char and self.current_char != "'":
                self.advance()
            if self.current_char == "'":
                self.advance()
            return

        if self.current_char is None or self.current_char in STRG_DLM:
            # Valid character literal
            tokens.append(Token(TokenType.char, f"'{char_value}'", start_pos.ln, start_pos.col))
        else:
            errors.append(LexicalError(start_pos, "Invalid delimiter after character literal"))

    def make_comment_or_div_or_div_assign(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # consume '/'

        if self.current_char == '*':
            # Comment detected: either single-line or multi-line
            self.advance()  # consume '*'
            comment_str = "/*"
            has_content_on_first_line = False
            seen_first_newline = False
            
            while self.current_char is not None:
                # Check for nested comment start (not allowed)
                if self.current_char == '/' and self.peek() == '*':
                    errors.append(LexicalError(start_pos, "Nested comments are not allowed"))
                    return
                
                # Check for closing */
                if self.current_char == '*' and self.peek() == '/':
                    comment_str += "*/"
                    self.advance()  # consume '*'
                    self.advance()  # consume '/'
                    # Multi-line comment (has closing */)
                    tokens.append(Token(TokenType.comment, comment_str, start_pos.ln, start_pos.col))
                    return
                
                # Check for newline
                if self.current_char == '\n':
                    if not seen_first_newline:
                        # First newline encountered
                        seen_first_newline = True
                        
                        if has_content_on_first_line:
                            # Single-line: /* content with no */ before newline
                            tokens.append(Token(TokenType.comment, comment_str, start_pos.ln, start_pos.col))
                            return
                        else:
                            # Multi-line: /* with no content on first line
                            # Continue looking for */
                            comment_str += self.current_char
                            self.advance()
                            continue
                    else:
                        # Already saw first newline, this is a continuation of multi-line
                        comment_str += self.current_char
                        self.advance()
                        continue
                
                # Track non-whitespace content on first line only
                if not seen_first_newline and not self.current_char.isspace():
                    has_content_on_first_line = True
                
                comment_str += self.current_char
                self.advance()
            
            # Reached end of file without finding */
            if has_content_on_first_line and not seen_first_newline:
                # Had content on same line as /*, never hit newline, treat as single-line
                tokens.append(Token(TokenType.comment, comment_str, start_pos.ln, start_pos.col))
            elif not has_content_on_first_line and seen_first_newline:
                # /* with no content, expected */ but reached EOF
                errors.append(LexicalError(start_pos, "Unterminated multi-line comment"))
            else:
                # Other edge cases - treat as single-line
                tokens.append(Token(TokenType.comment, comment_str, start_pos.ln, start_pos.col))
            return

        elif self.current_char == '=':
            # Division assignment /=
            self.advance()
            if self.current_char is None or self.current_char in OPRTR_DLM:
                tokens.append(Token(TokenType.div_assign, '/=', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '/='"))
            return

        elif self.current_char == '/': # invalid '//'
            errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '/'"))
            return

        else:
            # Division operator /
            if self.current_char is None or self.current_char in OPRTR_DLM:
                tokens.append(Token(TokenType.div, '/', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '/'"))
                self.advance()
            return


    def make_mul_or_mul_assign(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # consume '*'
        if self.current_char == '=':  # mul-assign
            self.advance()
            if self.current_char is None or self.current_char in OPRTR_DLM:
                tokens.append(Token(TokenType.mul_assign, '*=', start_pos.ln, start_pos.col))
            else:
                # Invalid delimiter after '*='
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '*='"))
        elif self.current_char == '*':  # invalid '**'
            errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '*'"))
        elif self.current_char == '/':  # invalid '*/' outside comment
            errors.append(LexicalError(start_pos, "Unexpected '*/' outside of comment"))
            self.advance()
        else:  # plain multiplication
            if self.current_char is None or self.current_char in OPRTR_DLM:
                tokens.append(Token(TokenType.mul, '*', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '*'"))
                self.advance()

    def make_mod_or_mod_assign(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # %
        if self.current_char == '=':
            self.advance()
            if self.current_char is None or self.current_char in OPRTR_DLM:
                tokens.append(Token(TokenType.mod_assign, '%=', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '%='"))
        else:
            if self.current_char is None or self.current_char in OPRTR_DLM:
                tokens.append(Token(TokenType.mod, '%', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '%'"))

    def make_assign_or_eq(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # consume '='

        if self.current_char == '=':
            self.advance()
            if self.current_char is None or self.current_char in OPRTR_DLM:
                tokens.append(Token(TokenType.eq, '==', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '=='"))
        else:  # assignment operator
            if self.current_char is None or self.current_char in OPRTR_DLM:
                tokens.append(Token(TokenType.assign, '=', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '='"))

    def make_lt_or_lte(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # consume '<'

        if self.current_char == '=':  # <=
            self.advance()
            if self.current_char is None or self.current_char in OPRTR_DLM:
                tokens.append(Token(TokenType.lte, '<=', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '<='"))
        else:  # <
            if self.current_char is None or self.current_char in OPRTR_DLM:
                tokens.append(Token(TokenType.lt, '<', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '<'"))

    def make_gt_or_gte(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # >
        if self.current_char == '=':
            self.advance()
            if self.current_char is None or self.current_char in OPRTR_DLM:
                tokens.append(Token(TokenType.gte, '>=', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '>='"))
        else:
            if self.current_char is None or self.current_char in OPRTR_DLM:
                tokens.append(Token(TokenType.gt, '>', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '>'"))

    def make_not_or_neq(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # !
        if self.current_char == '=':
            self.advance()
            if self.current_char is None or self.current_char in OPRTR_DLM:
                tokens.append(Token(TokenType.neq, '!=', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '!='"))
        else:
            if self.current_char is None or self.current_char in OPRTR_DLM:
                tokens.append(Token(TokenType.not_, '!', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '!'"))

    def make_and(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # consume first '&'

        if self.current_char == '&':  # saw '&&'
            self.advance()  # consume second '&'
            if self.current_char is None or self.current_char in OPRTR_DLM:
                tokens.append(Token(TokenType.and_, '&&', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, "Invalid operator '&&'"))
        else:  # single '&' is invalid
            if self.current_char is None or self.current_char in OPRTR_DLM:
                errors.append(LexicalError(start_pos, "Invalid '&' (expected '&&')"))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '&'"))
                self.advance()

    def make_or(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # consume first '|'
        if self.current_char == '|':  # saw '||'
            self.advance()  # consume second '|'
            if self.current_char is None or self.current_char in OPRTR_DLM:
                tokens.append(Token(TokenType.or_, '||', start_pos.ln, start_pos.col))
            else:
                errors.append(LexicalError(start_pos, "Invalid operator '||'"))
        else:  # single '|' is invalid
            if self.current_char is None or self.current_char in OPRTR_DLM:
                errors.append(LexicalError(start_pos, "Invalid '|' (expected '||')"))
            else:
                errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after '|'"))
                self.advance()

    def make_comma(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # ,
        if self.current_char is None or self.current_char in OPRTR_DLM:
            tokens.append(Token(TokenType.separator, ',', start_pos.ln, start_pos.col))
        else:
            errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after ','"))

    def make_semicolon(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # ;
        if self.current_char is None or self.current_char in SEMI_SYM_DLM:
            tokens.append(Token(TokenType.terminator, ';', start_pos.ln, start_pos.col))
        else:
            errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after ';'"))

    def make_colon(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # :
        if self.current_char is None or self.current_char in COLON_DLM:
            tokens.append(Token(TokenType.separator, ':', start_pos.ln, start_pos.col))
        else:
            errors.append(LexicalError(start_pos, f"Invalid delimiter '{self.current_char}' after ':'"))

    def make_dot_or_fractional(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # consume '.'

        if self.current_char and self.current_char.isdigit():
            # It's a float literal continuation (e.g., 3.14)
            self.pos.index -= 1  # backtrack so make_number can handle it
            self.current_char = '.'
            self.make_number(tokens, errors, positive=True)
            return

        if self.current_char and self.current_char.isalpha():
            # It's a method call like .split or .count
            method_str = ''
            while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
                method_str += self.current_char
                self.advance()

            if method_str in {'split', 'count'}:
                tokens.append(Token(TokenType.separator, '.', start_pos.ln, start_pos.col))
                tokens.append(Token(getattr(TokenType, method_str), method_str, start_pos.ln, start_pos.col + 1))
            else:
                errors.append(LexicalError(start_pos, f"Unknown method '{method_str}' after '.'"))
            return

        # If it's not a digit or letter, treat as standalone dot
        tokens.append(Token(TokenType.separator, '.', start_pos.ln, start_pos.col))

    def make_lparen(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # consume '('
        # If immediately followed by a string, handle it
        if self.current_char == '"':
            tokens.append(Token(TokenType.bracket, '(', start_pos.ln, start_pos.col))
            self.make_string(tokens, errors)
            return
        # Validate next char
        if self.current_char is not None and self.current_char not in OP_PRN_DLM:
            errors.append(LexicalError(
                self.pos.copy(),
                f"Invalid character '{self.current_char}' after '('"
            ))
            return
        tokens.append(Token(TokenType.bracket, '(', start_pos.ln, start_pos.col))
        return

    def make_rparen(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # consume ')'
        if self.current_char is not None and self.current_char not in CLBRCKT_DLM:
            errors.append(LexicalError(
                self.pos.copy(),
                f"Invalid character '{self.current_char}' after ')'"
            ))
            return
        tokens.append(Token(TokenType.bracket, ')', start_pos.ln, start_pos.col))
        return

    def make_lbracket(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # consume '['
        if self.current_char is not None and self.current_char not in OPBRCKT_DLM:
            errors.append(LexicalError(start_pos,
                f"Invalid delimiter '{self.current_char}' after '['"))
            return
        tokens.append(Token(TokenType.bracket, '[', start_pos.ln, start_pos.col))
        return 

    def make_rbracket(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # consume ']'
        if self.current_char is not None and self.current_char not in CLBRCKT_DLM:
            errors.append(LexicalError(start_pos,
                f"Invalid delimiter '{self.current_char}' after ']'"))
            return
        tokens.append(Token(TokenType.bracket, ']', start_pos.ln, start_pos.col))
        return  

    def make_lbrace(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # consume '{'
        if self.current_char is not None and self.current_char not in OPBRCKT_DLM:
            errors.append(LexicalError(start_pos,
                f"Invalid delimiter '{self.current_char}' after '{{'"))
            return
        tokens.append(Token(TokenType.bracket, '{', start_pos.ln, start_pos.col))
        return

    def make_rbrace(self, tokens, errors):
        start_pos = self.pos.copy()
        self.advance()  # consume '}'
        if self.current_char is not None and self.current_char not in CLBRCKT_DLM:
            errors.append(LexicalError(start_pos,
                f"Invalid delimiter '{self.current_char}' after '}}'"))
            return
        tokens.append(Token(TokenType.bracket, '}', start_pos.ln, start_pos.col))
        return 