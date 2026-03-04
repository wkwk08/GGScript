class TokenType:
    # Data Types
    frag = "frag"         # int
    elo = "elo"           # float
    ign = "ign"           # string
    surebol = "surebol"   # boolean
    tag = "tag"           # char

    # Control Flow
    clutch = "clutch"       # if
    choke = "choke"         # else
    choke_clutch = "choke_clutch"   # else if
    pick = "pick"           # switch
    role = "role"           # case
    noob = "noob"           # default
    grind = "grind"         # for
    retry = "retry"         # while
    try_ = "try"            # do
    afk = "afk"             # break
    hop = "hop"             # continue

    # I/O
    comsat = "comsat"    # scanf/input
    shout = "shout"      # printf/output

    # Functions
    build = "build"     # function declaration
    lobby = "lobby"     # main
    dodge = "dodge"     # void
    ggwp = "ggwp"       # return

    # Modifiers
    stun = "stun"      # const

    # Boolean Literals 
    buff = "buff"      # true
    nerf = "nerf"      # false

    # Array Operations
    stack = "stack"     # append
    craft = "craft"     # insert
    drop = "drop"       # pop
    count = "count"     # length
    split = "split"     # split

    # Arithmetic Operators 
    plus = "+"          # +
    minus = "-"         # -
    mul = "*"           # *
    div = "/"           # /
    mod = "%"           # %

    # Relational Operators 
    eq = "=="            # ==
    neq = "!="           # !=
    lt = "<"             # <
    gt = ">"             # >
    lte = "<="           # <=
    gte = ">="           # >=

    # Assignment Operators 
    assign = "="         # =
    plus_assign = "+="   # +=
    minus_assign = "-="  # -=
    mul_assign = "*="    # *=
    div_assign = "/="    # /=
    mod_assign = "%="    # %=

    # Logical Operators 
    and_ = "&&"          # &&
    or_ = "||"           # ||
    not_ = "!"           # !

    # Unary Operators 
    increment = "++"     # ++
    decrement = "--"     # --

    # Delimiters 
    lparen = "("        # (
    rparen = ")"        # )
    lbrace = "{"        # {
    rbrace = "}"        # }
    lbracket = "["      # [
    rbracket = "]"      # ]
    comma = ","         # ,
    semicolon = ";"     # ;
    colon = ":"         # :
    dot = "."           # .
    terminator = "terminator"  # ;
    separator = "separator"    # ,
    bracket = "bracket"        # (), {}, [], "

    # Literals
    integer = "integer"    # frag literal
    float = "float"        # elo literal
    string = "string"      # ign literal
    char = "char"          # tag literal

    # Identifiers
    identifier = "identifier"   # variable names, function names

    # Special
    eof = "eof"                 # End of file
    error = "error"             # Lexical error
    comment = "comment"         # Comments
    whitespace = "whitespace"   # Spaces, tabs, newlines
    newline = "newline"         # Newline character