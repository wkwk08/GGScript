from .token_types import TokenType
from .token import Token

class Lexer:
    def __init__(self, source_code):
        self.source = source_code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.source[0] if source_code else None
        
        # Reserved words
        self.keywords = {
            'frag': TokenType.FRAG,
            'elo': TokenType.ELO,
            'ign': TokenType.IGN,
            'surebol': TokenType.SUREBOL,
            'tag': TokenType.TAG,
            'clutch': TokenType.CLUTCH,
            'choke': TokenType.CHOKE,
            'pick': TokenType.PICK,
            'role': TokenType.ROLE,
            'noob': TokenType.NOOB,
            'grind': TokenType.GRIND,
            'retry': TokenType.RETRY,
            'try': TokenType.TRY,
            'afk': TokenType.AFK,
            'hop': TokenType.HOP,
            'ggwp': TokenType.GGWP,
            'comsat': TokenType.COMSAT,
            'shout': TokenType.SHOUT,
            'build': TokenType.BUILD,
            'lobby': TokenType.LOBBY,
            'dodge': TokenType.DODGE,
            'stun': TokenType.STUN,
            'buff': TokenType.BUFF,
            'nerf': TokenType.NERF,
            'stack': TokenType.STACK,
            'craft': TokenType.CRAFT,
            'drop': TokenType.DROP,
            'count': TokenType.COUNT,
            'split': TokenType.SPLIT,
        }
    
    def advance(self):
        """Move to next character"""
        if self.current_char == '\n':
            self.line += 1
            self.column = 0
        
        self.pos += 1
        self.column += 1
        
        if self.pos < len(self.source):
            self.current_char = self.source[self.pos]
        else:
            self.current_char = None
    
    def peek(self, offset=1):
        """Look ahead without advancing"""
        peek_pos = self.pos + offset
        if peek_pos < len(self.source):
            return self.source[peek_pos]
        return None
    
    def skip_whitespace(self):
        """Skip spaces, tabs, newlines"""
        while self.current_char and self.current_char.isspace():
            self.advance()
    
    def skip_comment(self):
        """Handle comments: /* single-line and /* */ multi-line (page 12)"""
        # Single-line: / followed by space then *
        if self.current_char == '/' and self.peek() == ' ' and self.peek(2) == '*':
            self.advance()  # skip /
            self.advance()  # skip space
            self.advance()  # skip *
            while self.current_char and self.current_char != '\n':
                self.advance()
            return True
            
        # Multi-line comment: /* ... */
        if self.current_char == '/' and self.peek() == '*':
            self.advance()  # skip /
            self.advance()  # skip *
            while self.current_char:
                if self.current_char == '*' and self.peek() == '/':
                    self.advance()
                    self.advance()
                    return True
                self.advance()
            return True

    def read_number(self):
        """Read integer or float (pages 16-17, 52)"""
        start_line = self.line
        start_col = self.column
        num_str = ''
        
        # Handle negative numbers
        if self.current_char == '-':
            num_str += self.current_char
            self.advance()
        
        # Read integer part (max 15 digits per page 7, rule 16)
        digit_count = 0
        while self.current_char and self.current_char.isdigit():
            num_str += self.current_char
            digit_count += 1
            self.advance()
        
        # Check for decimal point
        if self.current_char == '.':
            num_str += self.current_char
            self.advance()
            
            # Read fractional part (max 6 digits per page 7, rule 17)
            frac_count = 0
            while self.current_char and self.current_char.isdigit():
                num_str += self.current_char
                frac_count += 1
                self.advance()
            
            try:
                return Token(TokenType.FLOAT, float(num_str), start_line, start_col)
            except ValueError:
                return Token(TokenType.ERROR, f"Invalid float: {num_str}", start_line, start_col)
        
        try:
            return Token(TokenType.INTEGER, int(num_str), start_line, start_col)
        except ValueError:
            return Token(TokenType.ERROR, f"Invalid integer: {num_str}", start_line, start_col)
    
    def read_string(self):
        """Read string literal (page 17, rule 19)"""
        start_line = self.line
        start_col = self.column
        
        self.advance()  # skip opening "
        string_value = ''
        
        while self.current_char and self.current_char != '"':
            if self.current_char == '\n':
                return Token(TokenType.ERROR, "Unterminated string (newline)", start_line, start_col)
            string_value += self.current_char
            self.advance()
        
        if self.current_char == '"':
            self.advance()  # skip closing "
            return Token(TokenType.STRING, string_value, start_line, start_col)
        else:
            return Token(TokenType.ERROR, "Unterminated string", start_line, start_col)
    
    def read_char(self):
        """Read character literal (page 19, rule 20)"""
        start_line = self.line
        start_col = self.column
        
        self.advance()  # skip opening '
        
        if not self.current_char:
            return Token(TokenType.ERROR, "Empty character literal", start_line, start_col)
        
        if self.current_char == "'":
            return Token(TokenType.ERROR, "Empty character literal", start_line, start_col)
        
        char_value = self.current_char
        self.advance()
        
        if self.current_char == "'":
            self.advance()  # skip closing '
            return Token(TokenType.CHAR, char_value, start_line, start_col)
        else:
            return Token(TokenType.ERROR, "Character literal must contain exactly one character", start_line, start_col)
    
    def read_identifier(self):
        """Read identifier or keyword (page 15, rules 3-6)"""
        start_line = self.line
        start_col = self.column
        identifier = ''
        underscore_count = 0
        
        # Must start with letter (rule 4)
        if not self.current_char.isalpha():
            return Token(TokenType.ERROR, "Identifier must start with a letter", start_line, start_col)
        
        # Read identifier (max 19 chars per page 7, rule 6)
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            if self.current_char == '_':
                underscore_count += 1
                if underscore_count > 19:  # Max 19 underscores (updated rule)
                    return Token(TokenType.ERROR, "Identifier cannot have more than 19 underscores", start_line, start_col)
            
            identifier += self.current_char
            self.advance()
            
            if len(identifier) > 20:  # Max length 20 characters (updated rule)
                return Token(TokenType.ERROR, "Identifier too long (max 20 characters)", start_line, start_col)
        
        # Check if it's a reserved word
        token_type = self.keywords.get(identifier, TokenType.IDENTIFIER)
        return Token(token_type, identifier, start_line, start_col)
    
    def get_next_token(self):
        """Main tokenization method"""
        while self.current_char:
            start_line = self.line
            start_col = self.column
            
            # Skip whitespace
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # Handle comments
            if self.skip_comment():
                continue
            
            # Numbers (including negative)
            if self.current_char.isdigit():
                return self.read_number()
            
            # Check for negative number vs minus operator
            if self.current_char == '-' and self.peek() and self.peek().isdigit():
                # Check if previous token suggests this is negation
                return self.read_number()
            
            # Strings
            if self.current_char == '"':
                return self.read_string()
            
            # Characters  
            if self.current_char == "'":
                return self.read_char()
            
            # Identifiers and keywords
            if self.current_char.isalpha():
                return self.read_identifier()
            
            # Two-character operators
            if self.current_char == '+':
                self.advance()
                if self.current_char == '+':
                    self.advance()
                    return Token(TokenType.INCREMENT, '++', start_line, start_col)
                elif self.current_char == '=':
                    self.advance()
                    return Token(TokenType.PLUS_ASSIGN, '+=', start_line, start_col)
                return Token(TokenType.PLUS, '+', start_line, start_col)
            
            if self.current_char == '-':
                self.advance()
                if self.current_char == '-':
                    self.advance()
                    return Token(TokenType.DECREMENT, '--', start_line, start_col)
                elif self.current_char == '=':
                    self.advance()
                    return Token(TokenType.MINUS_ASSIGN, '-=', start_line, start_col)
                return Token(TokenType.MINUS, '-', start_line, start_col)
            
            if self.current_char == '*':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.MULT_ASSIGN, '*=', start_line, start_col)
                return Token(TokenType.MULTIPLY, '*', start_line, start_col)
            
            if self.current_char == '/':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.DIV_ASSIGN, '/=', start_line, start_col)
                return Token(TokenType.DIVIDE, '/', start_line, start_col)
            
            if self.current_char == '%':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.MOD_ASSIGN, '%=', start_line, start_col)
                return Token(TokenType.MODULO, '%', start_line, start_col)
            
            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.EQUAL, '==', start_line, start_col)
                return Token(TokenType.ASSIGN, '=', start_line, start_col)
            
            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.NOT_EQUAL, '!=', start_line, start_col)
                return Token(TokenType.NOT, '!', start_line, start_col)
            
            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.LESS_EQUAL, '<=', start_line, start_col)
                return Token(TokenType.LESS_THAN, '<', start_line, start_col)
            
            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.GREATER_EQUAL, '>=', start_line, start_col)
                return Token(TokenType.GREATER_THAN, '>', start_line, start_col)
            
            if self.current_char == '&':
                self.advance()
                if self.current_char == '&':
                    self.advance()
                    return Token(TokenType.AND, '&&', start_line, start_col)
                return Token(TokenType.ERROR, "Invalid character '&'", start_line, start_col)
            
            if self.current_char == '|':
                self.advance()
                if self.current_char == '|':
                    self.advance()
                    return Token(TokenType.OR, '||', start_line, start_col)
                return Token(TokenType.ERROR, "Invalid character '|'", start_line, start_col)
            
            # Single-character tokens
            single_char_tokens = {
                ';': TokenType.SEMICOLON,
                ',': TokenType.COMMA,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET,
                ':': TokenType.COLON,
            }
            
            if self.current_char in single_char_tokens:
                char = self.current_char
                token_type = single_char_tokens[char]
                self.advance()
                return Token(token_type, char, start_line, start_col)
            
            # Unknown character
            char = self.current_char
            self.advance()
            return Token(TokenType.ERROR, f"Invalid character '{char}'", start_line, start_col)
        
        return Token(TokenType.EOF, None, self.line, self.column)
    
    def tokenize(self):
        """Return all tokens as a list"""
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens