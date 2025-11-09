from enum import Enum, auto

class TokenType(Enum):
    # Data Types (page 42)
    frag = auto()      # int
    elo = auto()       # float
    ign = auto()       # string
    surebol = auto()   # boolean
    tag = auto()       # char

    # Control Flow (page 42-43)
    clutch = auto()         # if
    choke = auto()          # else
    choke_clutch = auto()   # else if
    pick = auto()           # switch
    role = auto()           # case
    noob = auto()           # default
    grind = auto()          # for
    retry = auto()          # while
    try_ = auto()           # do
    afk = auto()            # break
    hop = auto()            # continue

    # I/O (page 43)
    comsat = auto()    # scanf/input
    shout = auto()     # printf/output

    # Functions (page 43-44)
    build = auto()     # function declaration
    lobby = auto()     # main
    dodge = auto()     # void
    ggwp = auto()      # return

    # Modifiers (page 44)
    stun = auto()      # const

    # Boolean Literals (page 44)
    buff = auto()      # true
    nerf = auto()      # false

    # Array Operations (page 44)
    stack = auto()     # append
    craft = auto()     # insert
    drop = auto()      # pop
    count = auto()     # length
    split = auto()     # split

    # Arithmetic Operators (page 45)
    plus = auto()          # +
    minus = auto()         # -
    mul = auto()           # *
    div = auto()           # /
    mod = auto()           # %

    # Relational Operators (page 45)
    eq = auto()            # ==
    neq = auto()           # !=
    lt = auto()            # <
    gt = auto()            # >
    lte = auto()           # <=
    gte = auto()           # >=

    # Assignment Operators (page 46)
    assign = auto()        # =
    plus_assign = auto()   # +=
    minus_assign = auto()  # -=
    mul_assign = auto()    # *=
    div_assign = auto()    # /=
    mod_assign = auto()    # %=

    # Logical Operators (page 46)
    and_ = auto()          # &&
    or_ = auto()           # ||
    not_ = auto()          # !

    # Unary Operators (page 47)
    increment = auto()     # ++
    decrement = auto()     # --

    # Delimiters (page 47)
    lparen = auto()        # (
    rparen = auto()        # )
    lbrace = auto()        # {
    rbrace = auto()        # }
    lbracket = auto()      # [
    rbracket = auto()      # ]
    comma = auto()         # ,
    semicolon = auto()     # ;
    colon = auto()         # :
    dot = auto()           # .

    # Literals
    integer = auto()       # frag literal
    float_ = auto()        # elo literal
    string = auto()        # ign literal
    char = auto()          # tag literal

    # Identifiers
    identifier = auto()    # variable names, function names

    # Special
    eof = auto()           # End of file
    error = auto()         # Lexical error
    comment = auto()       # Comments
    whitespace = auto()    # Spaces, tabs, newlines
    newline = auto()       # Newline character

    def __str__(self):
        """String representation for debugging"""
        return self.name