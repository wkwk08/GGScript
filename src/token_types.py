class TokenType:
    # Data Types (page 42)
    frag = "frag"          # int
    elo = "elo"           # float
    ign = "ign"           # string
    surebol = "surebol"   # boolean
    tag = "tag"           # char

    # Control Flow (page 42-43)
    clutch = "clutch"         # if
    choke = "choke"          # else
    choke_clutch = "choke_clutch"   # else if
    pick = "pick"           # switch
    role = "role"           # case
    noob = "noob"           # default
    grind = "grind"          # for
    retry = "retry"          # while
    try_ = "try"           # do
    afk = "afk"            # break
    hop = "hop"            # continue

    # I/O (page 43)
    comsat = "comsat"    # scanf/input
    shout = "shout"     # printf/output

    # Functions (page 43-44)
    build = "build"     # function declaration
    lobby = "lobby"     # main
    dodge = "dodge"     # void
    ggwp = "ggwp"      # return

    # Modifiers (page 44)
    stun = "stun"      # const

    # Boolean Literals (page 44)
    buff = "buff"      # true
    nerf = "nerf"      # false

    # Array Operations (page 44)
    stack = "stack"     # append
    craft = "craft"     # insert
    drop = "drop"      # pop
    count = "count"     # length
    split = "split"     # split

    # Arithmetic Operators (page 45)
    plus = "+"          # +
    minus = "-"         # -
    mul = "*"           # *
    div = "/"           # /
    mod = "%"           # %

    # Relational Operators (page 45)
    eq = "=="            # ==
    neq = "!="           # !=
    lt = "<"            # <
    gt = ">"            # >
    lte = "<="           # <=
    gte = ">="           # >=

    # Assignment Operators (page 46)
    assign = "="        # =
    plus_assign = "+="   # +=
    minus_assign = "-="  # -=
    mul_assign = "*="    # *=
    div_assign = "/="    # /=
    mod_assign = "%="    # %=

    # Logical Operators (page 46)
    and_ = "&&"          # &&
    or_ = "||"           # ||
    not_ = "!"          # !

    # Unary Operators (page 47)
    increment = "++"     # ++
    decrement = "--"     # --

    # Delimiters (page 47)
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

    # New unified delimiter types
    terminator = "terminator"  # ;
    separator = "separator"    # ,
    bracket = "bracket"        # (), {}, [], "

    # Literals
    integer = "integer"       # frag literal
    float = "float"        # elo literal
    string = "string"        # ign literal
    char = "char"          # tag literal

    # Identifiers
    identifier = "identifier"    # variable names, function names

    # Special
    eof = "eof"           # End of file
    error = "error"         # Lexical error
    comment = "comment"       # Comments
    whitespace = "whitespace"    # Spaces, tabs, newlines
    newline = "newline"       # Newline character

# Symbol mapping
SYMBOL_TO_TOKEN = {
    '+': TokenType.plus,
    '-': TokenType.minus,
    '*': TokenType.mul,
    '/': TokenType.div,
    '%': TokenType.mod,
    '==': TokenType.eq,
    '!=': TokenType.neq,
    '<': TokenType.lt,
    '>': TokenType.gt,
    '<=': TokenType.lte,
    '>=': TokenType.gte,
    '=': TokenType.assign,
    '+=': TokenType.plus_assign,
    '-=': TokenType.minus_assign,
    '*=': TokenType.mul_assign,
    '/=': TokenType.div_assign,
    '%=': TokenType.mod_assign,
    '&&': TokenType.and_,
    '||': TokenType.or_,
    '!': TokenType.not_,
    '++': TokenType.increment,
    '--': TokenType.decrement,
    '(': TokenType.lparen,
    ')': TokenType.rparen,
    '{': TokenType.lbrace,
    '}': TokenType.rbrace,
    '[': TokenType.lbracket,
    ']': TokenType.rbracket,
    ':': TokenType.colon,
    '.': TokenType.dot,

    # New unified mappings
    ';': TokenType.terminator,
    ',': TokenType.separator,
}

# Keyword mapping
KEYWORD_TO_TOKEN = {
    'afk': TokenType.afk,
    'buff': TokenType.buff,
    'build': TokenType.build,
    'choke': TokenType.choke,
    'choke_clutch': TokenType.choke_clutch,
    'clutch': TokenType.clutch,
    'comsat': TokenType.comsat,
    'count': TokenType.count,
    'craft': TokenType.craft,
    'dodge': TokenType.dodge,
    'drop': TokenType.drop,
    'elo': TokenType.elo,
    'frag': TokenType.frag,
    'ggwp': TokenType.ggwp,
    'grind': TokenType.grind,
    'hop': TokenType.hop,
    'ign': TokenType.ign,
    'lobby': TokenType.lobby,
    'nerf': TokenType.nerf,
    'noob': TokenType.noob,
    'pick': TokenType.pick,
    'retry': TokenType.retry,
    'role': TokenType.role,
    'shout': TokenType.shout,
    'split': TokenType.split,
    'stack': TokenType.stack,
    'stun': TokenType.stun,
    'surebol': TokenType.surebol,
    'tag': TokenType.tag,
    'try': TokenType.try_,
}

# Literal mapping
LITERAL_TO_TOKEN = {
    'integer': TokenType.integer,
    'float': TokenType.float,
    'string': TokenType.string,
    'char': TokenType.char
}

# Special token mapping
SPECIAL_TO_TOKEN = {
    'identifier': TokenType.identifier,
    'eof': TokenType.eof,
    'error': TokenType.error,
    'comment': TokenType.comment,
    'whitespace': TokenType.whitespace,
    'newline': TokenType.newline
}