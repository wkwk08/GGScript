class TokenType:
    # Data Types (page 42)
    FRAG = "frag"          # int
    ELO = "elo"           # float
    IGN = "ign"           # string
    SUREBOL = "surebol"   # boolean
    TAG = "tag"           # char

    # Control Flow (page 42-43)
    CLUTCH = "clutch"         # if
    CHOKE = "choke"          # else
    CHOKE_CLUTCH = "choke_clutch"   # else if
    PICK = "pick"           # switch
    ROLE = "role"           # case
    NOOB = "noob"           # default
    GRIND = "grind"          # for
    RETRY = "retry"          # while
    TRY = "try"           # do
    AFK = "afk"            # break
    HOP = "hop"            # continue

    # I/O (page 43)
    COMSAT = "comsat"    # scanf/input
    SHOUT = "shout"     # printf/output

    # Functions (page 43-44)
    BUILD = "build"     # function declaration
    LOBBY = "lobby"     # main
    DODGE = "dodge"     # void
    GGWP = "ggwp"      # return

    # Modifiers (page 44)
    STUN = "stun"      # const

    # Boolean Literals (page 44)
    BUFF = "buff"      # true
    NERF = "nerf"      # false

    # Array Operations (page 44)
    STACK = "stack"     # append
    CRAFT = "craft"     # insert
    DROP = "drop"      # pop
    COUNT = "count"     # length
    SPLIT = "split"     # split

    # Arithmetic Operators (page 45)
    PLUS = "+"          # +
    MINUS = "-"         # -
    MUL = "*"           # *
    DIV = "/"           # /
    MOD = "%"           # %

    # Relational Operators (page 45)
    EQ = "=="            # ==
    NEQ = "!="           # !=
    LT = "<"            # <
    GT = ">"            # >
    LTE = "<="           # <=
    GTE = ">="           # >=

    # Assignment Operators (page 46)
    ASSIGN = "="        # =
    PLUS_ASSIGN = "+="   # +=
    MINUS_ASSIGN = "-="  # -=
    MUL_ASSIGN = "*="    # *=
    DIV_ASSIGN = "/="    # /
    MOD_ASSIGN = "%="    # %=

    # Logical Operators (page 46)
    AND = "&&"          # &&
    OR = "||"           # ||
    NOT = "!"          # !

    # Unary Operators (page 47)
    INCREMENT = "++"     # ++
    DECREMENT = "--"     # --

    # Delimiters (page 47)
    LPAREN = "("        # (
    RPAREN = ")"        # )
    LBRACE = "{"        # {
    RBRACE = "}"        # }
    LBRACKET = "["      # [
    RBRACKET = "]"      # ]
    COMMA = ","         # ,
    SEMICOLON = ";"     # ;
    COLON = ":"         # :
    DOT = "."           # .

    # Literals
    INTEGER = "INTEGER"       # frag literal
    FLOAT = "FLOAT"        # elo literal
    STRING = "STRING"        # ign literal
    CHAR = "CHAR"          # tag literal

    # Identifiers
    IDENTIFIER = "IDENTIFIER"    # variable names, function names

    # Special
    EOF = "EOF"           # End of file
    ERROR = "ERROR"         # Lexical error
    COMMENT = "COMMENT"       # Comments
    WHITESPACE = "WHITESPACE"    # Spaces, tabs, newlines
    NEWLINE = "NEWLINE"       # Newline character

# Symbol mapping
SYMBOL_TO_TOKEN = {
    '+': TokenType.PLUS,
    '-': TokenType.MINUS,
    '*': TokenType.MUL,
    '/': TokenType.DIV,
    '%': TokenType.MOD,
    '==': TokenType.EQ,
    '!=': TokenType.NEQ,
    '<': TokenType.LT,
    '>': TokenType.GT,
    '<=': TokenType.LTE,
    '>=': TokenType.GTE,
    '=': TokenType.ASSIGN,
    '+=': TokenType.PLUS_ASSIGN,
    '-=': TokenType.MINUS_ASSIGN,
    '*=': TokenType.MUL_ASSIGN,
    '/=': TokenType.DIV_ASSIGN,
    '%=': TokenType.MOD_ASSIGN,
    '&&': TokenType.AND,
    '||': TokenType.OR,
    '!': TokenType.NOT,
    '++': TokenType.INCREMENT,
    '--': TokenType.DECREMENT,
    '(': TokenType.LPAREN,
    ')': TokenType.RPAREN,
    '{': TokenType.LBRACE,
    '}': TokenType.RBRACE,
    '[': TokenType.LBRACKET,
    ']': TokenType.RBRACKET,
    ',': TokenType.COMMA,
    ';': TokenType.SEMICOLON,
    ':': TokenType.COLON,
    '.': TokenType.DOT,
}

# Keyword mapping
KEYWORD_TO_TOKEN = {
    'afk': TokenType.AFK,
    'buff': TokenType.BUFF,
    'build': TokenType.BUILD,
    'choke': TokenType.CHOKE,
    'choke_clutch': TokenType.CHOKE_CLUTCH,
    'clutch': TokenType.CLUTCH,
    'comsat': TokenType.COMSAT,
    'count': TokenType.COUNT,
    'craft': TokenType.CRAFT,
    'dodge': TokenType.DODGE,
    'drop': TokenType.DROP,
    'elo': TokenType.ELO,
    'frag': TokenType.FRAG,
    'ggwp': TokenType.GGWP,
    'grind': TokenType.GRIND,
    'hop': TokenType.HOP,
    'ign': TokenType.IGN,
    'lobby': TokenType.LOBBY,
    'nerf': TokenType.NERF,
    'noob': TokenType.NOOB,
    'pick': TokenType.PICK,
    'retry': TokenType.RETRY,
    'role': TokenType.ROLE,
    'shout': TokenType.SHOUT,
    'split': TokenType.SPLIT,
    'stack': TokenType.STACK,
    'stun': TokenType.STUN,
    'surebol': TokenType.SUREBOL,
    'tag': TokenType.TAG,
    'try': TokenType.TRY,
}