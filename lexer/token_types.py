from enum import Enum

class TokenType(Enum):
    # Data Types
    FRAG = "frag"           # int
    ELO = "elo"             # float
    IGN = "ign"             # string
    SUREBOL = "surebol"     # boolean
    TAG = "tag"             # char
    
    # Control Flow
    CLUTCH = "clutch"       # if
    CHOKE = "choke"         # else
    CHOKE_CLUTCH = "choke clutch"  # else if
    PICK = "pick"           # switch
    ROLE = "role"           # case
    NOOB = "noob"           # default
    
    # Loops
    GRIND = "grind"         # for
    RETRY = "retry"         # while
    TRY = "try"             # do
    
    # Control Statements
    AFK = "afk"             # break
    HOP = "hop"             # continue
    GGWP = "ggwp"           # return
    
    # I/O
    COMSAT = "comsat"       # scanf
    SHOUT = "shout"         # printf
    
    # Function/Program
    BUILD = "build"         # function
    LOBBY = "lobby"         # main
    DODGE = "dodge"         # void
    
    # Other Keywords
    STUN = "stun"           # const
    BUFF = "buff"           # true
    NERF = "nerf"           # false
    STACK = "stack"         # append
    CRAFT = "craft"         # insert
    DROP = "drop"           # pop
    COUNT = "count"         # length
    SPLIT = "split"         # split
    
    # Operators
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"
    
    EQUAL = "=="
    NOT_EQUAL = "!="
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    
    ASSIGN = "="
    PLUS_ASSIGN = "+="
    MINUS_ASSIGN = "-="
    MULT_ASSIGN = "*="
    DIV_ASSIGN = "/="
    MOD_ASSIGN = "%="
    
    AND = "&&"
    OR = "||"
    NOT = "!"
    
    INCREMENT = "++"
    DECREMENT = "--"
    
    # Delimiters
    SEMICOLON = ";"
    COMMA = ","
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    QUOTE = '"'
    COLON = ":"
    
    # Literals & Identifiers
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    STRING = "STRING"
    CHAR = "CHAR"
    IDENTIFIER = "IDENTIFIER"
    
    # Comments
    COMMENT = "COMMENT"
    
    # Special
    EOF = "EOF"
    ERROR = "ERROR"