from enum import Enum, auto

class TokenType(Enum):
    # Data Types (page 42)
    FRAG = auto()      # int
    ELO = auto()       # float
    IGN = auto()       # string
    SUREBOL = auto()   # boolean
    TAG = auto()       # char
    
    # Control Flow (page 42-43)
    CLUTCH = auto()         # if
    CHOKE = auto()          # else
    CHOKE_CLUTCH = auto()   # else if (NEW: two-word keyword)
    PICK = auto()           # switch
    ROLE = auto()           # case
    NOOB = auto()           # default
    GRIND = auto()          # for
    RETRY = auto()          # while
    TRY = auto()            # do
    AFK = auto()            # break
    HOP = auto()            # continue
    
    # I/O (page 43)
    COMSAT = auto()    # scanf/input
    SHOUT = auto()     # printf/output
    
    # Functions (page 43-44)
    BUILD = auto()     # function declaration
    LOBBY = auto()     # main
    DODGE = auto()     # void
    GGWP = auto()      # return
    
    # Modifiers (page 44)
    STUN = auto()      # const
    
    # Boolean Literals (page 44)
    BUFF = auto()      # true
    NERF = auto()      # false
    
    # Array Operations (page 44)
    STACK = auto()     # append
    CRAFT = auto()     # insert
    DROP = auto()      # pop
    COUNT = auto()     # length
    SPLIT = auto()     # split
    
    # Arithmetic Operators (page 45)
    PLUS = auto()          # +
    MINUS = auto()         # -
    MULTIPLY = auto()      # *
    DIVIDE = auto()        # /
    MODULO = auto()        # %
    
    # Relational Operators (page 45)
    EQUAL = auto()         # ==
    NOT_EQUAL = auto()     # !=
    LESS_THAN = auto()     # <
    GREATER_THAN = auto()  # >
    LESS_EQUAL = auto()    # <=
    GREATER_EQUAL = auto() # >=
    
    # Assignment Operators (page 46)
    ASSIGN = auto()        # =
    PLUS_ASSIGN = auto()   # +=
    MINUS_ASSIGN = auto()  # -=
    MULTIPLY_ASSIGN = auto()  # *=
    DIVIDE_ASSIGN = auto()    # /=
    MODULO_ASSIGN = auto()    # %=
    
    # Logical Operators (page 46)
    AND = auto()           # &&
    OR = auto()            # ||
    NOT = auto()           # !
    
    # Unary Operators (page 47)
    INCREMENT = auto()     # ++
    DECREMENT = auto()     # --
    
    # Delimiters (page 47)
    LPAREN = auto()        # (
    RPAREN = auto()        # )
    LBRACE = auto()        # {
    RBRACE = auto()        # }
    LBRACKET = auto()      # [
    RBRACKET = auto()      # ]
    COMMA = auto()         # ,
    SEMICOLON = auto()     # ;
    COLON = auto()         # :
    
    # Literals
    INTEGER = auto()       # frag literal
    FLOAT = auto()         # elo literal
    STRING = auto()        # ign literal
    CHAR = auto()          # tag literal
    
    # Identifiers
    IDENTIFIER = auto()    # variable names, function names
    
    # Special
    EOF = auto()           # End of file
    ERROR = auto()         # Lexical error
    COMMENT = auto()       # Comments
    WHITESPACE = auto()    # Spaces, tabs, newlines
    NEWLINE = auto()       # Newline character
    
    def __str__(self):
        """String representation for debugging"""
        return self.name