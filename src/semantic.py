from token_types import TokenType

class SemanticError:
    def __init__(self, line, column, details):
        self.line = line
        self.column = column
        self.details = details

    def as_string(self):
        return f"Semantic Error at Ln {self.line}, Col {self.column}: {self.details}"

class SemanticAnalyzer:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t.type not in [TokenType.comment, TokenType.whitespace, TokenType.newline, TokenType.eof]]
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None
        self.symbol_table = []  # {'type':, 'datatype':, 'identifier':, 'scope':, 'dimension':, 'parent':, 'level':}
        self.parameter_table = []  # {'func_id':, 'args': [{'datatype':, 'id':}], 'total_args':}
        self.scope_stack = ['global']
        self.current_scope = 'global'
        self.level = 0
        self.errors = []

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def peek(self):
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return None

    def current_type(self):
        return self.current_token.type if self.current_token else None

    def current_value(self):
        return self.current_token.value if self.current_token else None

    def error(self, details):
        line = self.current_token.ln if self.current_token else 0
        col = self.current_token.col if self.current_token else 0
        self.errors.append(SemanticError(line, col, details))

    def analyze(self):
        if not self.tokens:
            self.error("No tokens to analyze")
            return False, "Semantic analysis failed: No tokens"
        self.program()
        if self.errors:
            error_msgs = "\n".join([e.as_string() for e in self.errors])
            return False, error_msgs
        return True, "Semantic analysis successful ✓ No errors."

    def enter_scope(self, scope_name):
        self.level += 1
        self.current_scope = f"{scope_name}_{self.level}"
        self.scope_stack.append(self.current_scope)

    def exit_scope(self):
        if self.scope_stack:
            self.scope_stack.pop()
            self.current_scope = self.scope_stack[-1] if self.scope_stack else 'global'
        if self.level > 0:
            self.level -= 1

    def add_symbol(self, sym_type, datatype, identifier, dimension=0):
        if self.is_declared(identifier):
            self.error(f"Redeclaration of '{identifier}' in scope '{self.current_scope}'")
            return
        self.symbol_table.append({
            'type': sym_type,
            'datatype': datatype,
            'identifier': identifier,
            'scope': self.current_scope,
            'dimension': dimension,
            'parent': self.scope_stack[-2] if len(self.scope_stack) > 1 else 'global',
            'level': self.level
        })

    def is_declared(self, identifier):
        for sym in reversed(self.symbol_table):
            if sym['identifier'] == identifier and sym['scope'] in self.scope_stack:
                return True
        return False

    def get_datatype(self, identifier):
        for sym in reversed(self.symbol_table):
            if sym['identifier'] == identifier and sym['scope'] in self.scope_stack:
                return sym['datatype']
        self.error(f"Undeclared identifier '{identifier}'")
        return None

    def get_type(self, identifier):
        for sym in reversed(self.symbol_table):
            if sym['identifier'] == identifier and sym['scope'] in self.scope_stack:
                return sym['type']
        return None

    def get_dimension(self, identifier):
        for sym in reversed(self.symbol_table):
            if sym['identifier'] == identifier and sym['scope'] in self.scope_stack:
                return sym['dimension']
        return 0

    def is_const(self, identifier):
        t = self.get_type(identifier)
        return t and ('const' in t)

    def map_token_to_datatype(self, token_type):
        mapping = {
            TokenType.frag: 'int',
            TokenType.elo: 'float',
            TokenType.ign: 'string',
            TokenType.surebol: 'bool',
            TokenType.tag: 'char',
            TokenType.integer: 'int',
            TokenType.float: 'float',
            TokenType.string: 'string',
            TokenType.char: 'char',
            TokenType.buff: 'bool',
            TokenType.nerf: 'bool'
        }
        return mapping.get(token_type, None)

    def is_numeric_type(self, datatype):
        return datatype in ['int', 'float']

    def is_bool_type(self, datatype):
        return datatype == 'bool'

    def check_type_compatible(self, t1, t2):
        if t1 == t2:
            return True
        if t1 == 'float' and t2 == 'int':
            return True
        if t1 == 'string' and t2 == 'char':
            return True
        return False

    def add_function_params(self, func_id, params):
        self.parameter_table.append({
            'func_id': func_id,
            'args': params,
            'total_args': len(params)
        })

    def check_function_call(self, func_id, actual_args):
        for entry in self.parameter_table:
            if entry['func_id'] == func_id:
                if len(actual_args) != entry['total_args']:
                    self.error(f"Argument count mismatch for '{func_id}'. Expected {entry['total_args']}, got {len(actual_args)}")
                    return
                for i, (exp, act) in enumerate(zip([a['datatype'] for a in entry['args']], actual_args)):
                    if not self.check_type_compatible(exp, act):
                        self.error(f"Type mismatch for arg {i+1} in '{func_id}'. Expected {exp}, got {act}")
                return
        self.error(f"Undefined function '{func_id}'")

    def program(self):
        self.global_section()
        self.main_function()
        if self.current_type() is not None:
            self.error("Extra code after main function")

    def global_section(self):
        while self.current_type() in [TokenType.frag, TokenType.elo, TokenType.ign, TokenType.surebol, TokenType.tag, TokenType.stun, TokenType.build]:
            if self.current_type() == TokenType.build:
                self.function_definition()
            else:
                self.declaration()

    def main_function(self):
        if self.current_type() != TokenType.lobby:
            self.error("Expected main function 'lobby'")
            return
        self.advance()
        self.add_symbol('function', 'void', 'lobby')
        self.enter_scope('lobby')
        if self.current_type() != TokenType.lparen:
            self.error("Expected '(' after 'lobby'")
        self.advance()
        params = self.parameter_list()
        if params:
            self.error("Main 'lobby' should have no parameters")
        self.add_function_params('lobby', [])
        if self.current_type() != TokenType.rparen:
            self.error("Expected ')' after params")
        self.advance()
        if self.current_type() != TokenType.lbrace:
            self.error("Expected '{' for main body")
        self.advance()
        self.local_declaration_list()
        self.statement_list()
        if self.current_type() != TokenType.rbrace:
            self.error("Expected '}' to close main")
        self.advance()
        self.exit_scope()

    def function_definition(self):
        datatype = self.map_token_to_datatype(self.current_type())
        if not datatype:
            self.error("Invalid return type")
        self.advance()
        if self.current_type() != TokenType.identifier:
            self.error("Expected function name")
        func_id = self.current_value()
        self.advance()
        self.add_symbol('function', datatype, func_id)
        self.enter_scope(func_id)
        if self.current_type() != TokenType.lparen:
            self.error("Expected '(' for params")
        self.advance()
        params = self.parameter_list()
        self.add_function_params(func_id, params)
        if self.current_type() != TokenType.rparen:
            self.error("Expected ')' after params")
        self.advance()
        if self.current_type() != TokenType.lbrace:
            self.error("Expected '{' for function body")
        self.advance()
        self.local_declaration_list()
        self.statement_list()
        if self.current_type() != TokenType.rbrace:
            self.error("Expected '}' to close function")
        self.advance()
        self.exit_scope()

    def parameter_list(self):
        params = []
        while self.current_type() in [TokenType.frag, TokenType.elo, TokenType.ign, TokenType.surebol, TokenType.tag]:
            datatype = self.map_token_to_datatype(self.current_type())
            self.advance()
            if self.current_type() != TokenType.identifier:
                self.error("Expected param name")
            param_id = self.current_value()
            self.advance()
            self.add_symbol('param', datatype, param_id)
            params.append({'datatype': datatype, 'id': param_id})
            if self.current_type() == TokenType.comma:
                self.advance()
        return params

    def local_declaration_list(self):
        while self.current_type() in [TokenType.frag, TokenType.elo, TokenType.ign, TokenType.surebol, TokenType.tag, TokenType.stun]:
            self.declaration()

    def declaration(self):
        is_const = self.current_type() == TokenType.stun
        if is_const:
            self.advance()
        datatype_token = self.current_type()
        datatype = self.map_token_to_datatype(datatype_token)
        if not datatype:
            self.error(f"Invalid datatype")
            return
        self.advance()
        dimension = 0
        if self.current_type() == TokenType.lbracket:
            self.advance()
            if self.peek().type == TokenType.comma:
                dimension = 2
                self.advance()
                self.advance()  # ,
            else:
                dimension = 1
            if self.current_type() != TokenType.rbracket:
                self.error("Expected ']' for array dim")
            self.advance()
        sym_type = 'const-array' if is_const and dimension > 0 else 'const' if is_const else 'array' if dimension > 0 else 'var'
        if self.current_type() != TokenType.identifier:
            self.error("Expected identifier")
            return
        identifier = self.current_value()
        self.advance()
        self.add_symbol(sym_type, datatype, identifier, dimension)
        if self.current_type() in [TokenType.assign, TokenType.plus_assign, TokenType.minus_assign, TokenType.mul_assign, TokenType.div_assign, TokenType.mod_assign]:
            op = self.current_type()
            self.advance()
            if is_const and op != TokenType.assign:
                self.error("Const vars can only use simple assignment for initialization")
            if op != TokenType.assign and not self.is_numeric_type(datatype):
                self.error("Compound assignments only for numeric types")
            expr_type = self.expression()
            if expr_type and not self.check_type_compatible(datatype, expr_type):
                self.error(f"Type mismatch in assignment to '{identifier}' ({datatype} vs {expr_type})")
        if self.current_type() == TokenType.comma:
            self.advance()
            self.declaration()  # Chained
        elif self.current_type() != TokenType.semicolon:
            self.error("Expected ';' or ',' after declaration")
        else:
            self.advance()

    def statement_list(self):
        while self.current_type() not in [TokenType.rbrace, None]:
            self.statement()

    def statement(self):
        t = self.current_type()
        if t in [TokenType.frag, TokenType.elo, TokenType.ign, TokenType.surebol, TokenType.tag, TokenType.stun]:
            self.declaration()
        elif t == TokenType.identifier:
            self.assignment_statement()
        elif t == TokenType.comsat:
            self.input_statement()
        elif t == TokenType.shout:
            self.output_statement()
        elif t in [TokenType.stack, TokenType.craft, TokenType.drop, TokenType.count, TokenType.split]:
            self.function_call_stmt()
        elif t == TokenType.afk:
            self.break_statement()
        elif t == TokenType.hop:
            self.continue_statement()
        elif t == TokenType.ggwp:
            self.return_statement()
        elif t == TokenType.clutch:
            self.if_statement()
        elif t == TokenType.pick:
            self.switch_statement()
        elif t == TokenType.grind:
            self.for_loop()
        elif t == TokenType.retry:
            self.while_loop()
        elif t == TokenType.try_:
            self.do_while_loop()
        else:
            self.error(f"Unexpected statement start: {t}")

    def assignment_statement(self):
        if self.current_type() != TokenType.identifier:
            self.error("Expected identifier for assignment")
        identifier = self.current_value()
        datatype = self.get_datatype(identifier)
        if not datatype:
            return
        if self.is_const(identifier):
            self.error(f"Cannot assign to const '{identifier}'")
        self.advance()
        if self.current_type() == TokenType.lbracket:
            dim = self.get_dimension(identifier)
            self.advance()
            index_type = self.expression()
            if index_type != 'int':
                self.error("Array index must be int")
            if self.current_type() == TokenType.comma:
                self.advance()
                index_type2 = self.expression()
                if index_type2 != 'int':
                    self.error("Array index must be int")
                if dim != 2:
                    self.error(f"Dimension mismatch for array '{identifier}' (expected {dim}D)")
            if self.current_type() != TokenType.rbracket:
                self.error("Expected ']' for array access")
            self.advance()
        if self.current_type() not in [TokenType.assign, TokenType.plus_assign, TokenType.minus_assign, TokenType.mul_assign, TokenType.div_assign, TokenType.mod_assign]:
            self.error("Expected assignment operator")
        op = self.current_type()
        self.advance()
        if op != TokenType.assign and not self.is_numeric_type(datatype):
            self.error("Compound assign only for numbers")
        expr_type = self.expression()
        if not self.check_type_compatible(datatype, expr_type):
            self.error(f"Type mismatch assigning to '{identifier}' ({datatype} vs {expr_type})")
        if self.current_type() != TokenType.semicolon:
            self.error("Expected ';' after assignment")
        self.advance()

    def input_statement(self):
        self.advance()  # comsat
        if self.current_type() != TokenType.lparen:
            self.error("Expected '(' for input")
        self.advance()
        while self.current_type() == TokenType.identifier:
            id = self.current_value()
            datatype = self.get_datatype(id)
            if not datatype:
                continue
            if self.is_const(id):
                self.error(f"Cannot input to const '{id}'")
            self.advance()
            if self.current_type() == TokenType.comma:
                self.advance()
        if self.current_type() != TokenType.rparen:
            self.error("Expected ')' after input list")
        self.advance()
        if self.current_type() != TokenType.semicolon:
            self.error("Expected ';' after input")
        self.advance()

    def output_statement(self):
        self.advance()  # shout
        if self.current_type() != TokenType.lparen:
            self.error("Expected '(' for output")
        self.advance()
        while self.current_type() not in [TokenType.rparen, None]:
            self.expression()  # Any type ok for output
            if self.current_type() == TokenType.comma:
                self.advance()
        if self.current_type() != TokenType.rparen:
            self.error("Expected ')' after output list")
        self.advance()
        if self.current_type() != TokenType.semicolon:
            self.error("Expected ';' after output")
        self.advance()

    def function_call_stmt(self):
        func_id = self.current_value()
        self.advance()
        if self.current_type() != TokenType.lparen:
            self.error("Expected '(' for function call")
        self.advance()
        actual_args = []
        while self.current_type() not in [TokenType.rparen, None]:
            arg_type = self.expression()
            actual_args.append(arg_type)
            if self.current_type() == TokenType.comma:
                self.advance()
        if self.current_type() != TokenType.rparen:
            self.error("Expected ')' after args")
        self.advance()
        self.check_function_call(func_id, actual_args)
        if self.current_type() != TokenType.semicolon:
            self.error("Expected ';' after call")
        self.advance()

    def break_statement(self):
        self.advance()  # afk
        if self.current_type() != TokenType.semicolon:
            self.error("Expected ';' after break")
        self.advance()

    def continue_statement(self):
        self.advance()  # hop
        if self.current_type() != TokenType.semicolon:
            self.error("Expected ';' after continue")
        self.advance()

    def return_statement(self):
        self.advance()  # ggwp
        if self.current_type() != TokenType.semicolon:
            self.expression()  # Check matches func ret type
        self.advance()

    def if_statement(self):
        self.advance()  # clutch
        if self.current_type() != TokenType.lparen:
            self.error("Expected '(' for if")
        self.advance()
        cond_type = self.expression()
        if cond_type != 'bool':
            self.error("If condition must be bool")
        if self.current_type() != TokenType.rparen:
            self.error("Expected ')' after if condition")
        self.advance()
        self.enter_scope('if')
        if self.current_type() == TokenType.lbrace:
            self.advance()
            self.statement_list()
            if self.current_type() != TokenType.rbrace:
                self.error("Expected '}' for if body")
            self.advance()
        else:
            self.statement()
        self.exit_scope()
        while self.current_type() == TokenType.choke_clutch:
            self.advance()
            if self.current_type() != TokenType.lparen:
                self.error("Expected '(' for else if")
            self.advance()
            cond_type = self.expression()
            if cond_type != 'bool':
                self.error("Else if condition must be bool")
            if self.current_type() != TokenType.rparen:
                self.error("Expected ')' after else if condition")
            self.advance()
            self.enter_scope('elseif')
            if self.current_type() == TokenType.lbrace:
                self.advance()
                self.statement_list()
                if self.current_type() != TokenType.rbrace:
                    self.error("Expected '}' for else if body")
                self.advance()
            else:
                self.statement()
            self.exit_scope()
        if self.current_type() == TokenType.choke:
            self.advance()
            self.enter_scope('else')
            if self.current_type() == TokenType.lbrace:
                self.advance()
                self.statement_list()
                if self.current_type() != TokenType.rbrace:
                    self.error("Expected '}' for else body")
                self.advance()
            else:
                self.statement()
            self.exit_scope()

    def switch_statement(self):
        self.advance()  # pick
        if self.current_type() != TokenType.lparen:
            self.error("Expected '(' for switch")
        self.advance()
        switch_type = self.expression()
        if switch_type not in ['int', 'char', 'string', 'bool']:
            self.error("Switch expression must be int, char, string, or bool")
        if self.current_type() != TokenType.rparen:
            self.error("Expected ')' after switch expr")
        self.advance()
        if self.current_type() != TokenType.lbrace:
            self.error("Expected '{' for switch body")
        self.advance()
        self.enter_scope('switch')
        while self.current_type() == TokenType.role:
            self.advance()
            case_type = self.literal()  # case value
            if not self.check_type_compatible(switch_type, case_type):
                self.error("Case type mismatch with switch expr")
            if self.current_type() != TokenType.colon:
                self.error("Expected ':' after case")
            self.advance()
            self.statement_list()
        if self.current_type() == TokenType.noob:
            self.advance()
            if self.current_type() != TokenType.colon:
                self.error("Expected ':' after default")
            self.advance()
            self.statement_list()
        if self.current_type() != TokenType.rbrace:
            self.error("Expected '}' to close switch")
        self.advance()
        self.exit_scope()

    def for_loop(self):
        self.advance()  # grind
        if self.current_type() != TokenType.lparen:
            self.error("Expected '(' for for")
        self.advance()
        self.enter_scope('for')
        self.for_init()
        cond_type = self.expression()
        if cond_type != 'bool':
            self.error("For condition must be bool")
        if self.current_type() != TokenType.semicolon:
            self.error("Expected ';' after for condition")
        self.advance()
        self.for_update()
        if self.current_type() != TokenType.rparen:
            self.error("Expected ')' after for update")
        self.advance()
        if self.current_type() == TokenType.lbrace:
            self.advance()
            self.statement_list()
            if self.current_type() != TokenType.rbrace:
                self.error("Expected '}' for for body")
            self.advance()
        else:
            self.statement()
        self.exit_scope()

    def for_init(self):
        if self.current_type() in [TokenType.frag, TokenType.elo, TokenType.ign, TokenType.surebol, TokenType.tag]:
            self.declaration()
        elif self.current_type() == TokenType.identifier:
            self.assignment_statement_no_semi()
        elif self.current_type() != TokenType.semicolon:
            self.error("Invalid for init")
        if self.current_type() == TokenType.semicolon:
            self.advance()

    def assignment_statement_no_semi(self):
        if self.current_type() != TokenType.identifier:
            self.error("Expected identifier for assignment")
        identifier = self.current_value()
        datatype = self.get_datatype(identifier)
        if not datatype:
            return
        if self.is_const(identifier):
            self.error(f"Cannot assign to const '{identifier}'")
        self.advance()
        if self.current_type() == TokenType.lbracket:
            dim = self.get_dimension(identifier)
            self.advance()
            index_type = self.expression()
            if index_type != 'int':
                self.error("Array index must be int")
            if self.current_type() == TokenType.comma:
                self.advance()
                index_type2 = self.expression()
                if index_type2 != 'int':
                    self.error("Array index must be int")
                if dim != 2:
                    self.error(f"Dimension mismatch for array '{identifier}' (expected {dim}D)")
            if self.current_type() != TokenType.rbracket:
                self.error("Expected ']' for array access")
            self.advance()
        if self.current_type() not in [TokenType.assign, TokenType.plus_assign, TokenType.minus_assign, TokenType.mul_assign, TokenType.div_assign, TokenType.mod_assign]:
            self.error("Expected assignment operator")
        op = self.current_type()
        self.advance()
        if op != TokenType.assign and not self.is_numeric_type(datatype):
            self.error("Compound assign only for numbers")
        expr_type = self.expression()
        if not self.check_type_compatible(datatype, expr_type):
            self.error(f"Type mismatch assigning to '{identifier}' ({datatype} vs {expr_type})")

    def for_update(self):
        while self.current_type() == TokenType.identifier:
            self.assignment_statement_no_semi()
            if self.current_type() == TokenType.comma:
                self.advance()

    def while_loop(self):
        self.advance()  # retry
        if self.current_type() != TokenType.lparen:
            self.error("Expected '(' for while")
        self.advance()
        cond_type = self.expression()
        if cond_type != 'bool':
            self.error("While condition must be bool")
        if self.current_type() != TokenType.rparen:
            self.error("Expected ')' after while condition")
        self.advance()
        self.enter_scope('while')
        if self.current_type() == TokenType.lbrace:
            self.advance()
            self.statement_list()
            if self.current_type() != TokenType.rbrace:
                self.error("Expected '}' for while body")
            self.advance()
        else:
            self.statement()
        self.exit_scope()

    def do_while_loop(self):
        self.advance()  # try
        self.enter_scope('do')
        if self.current_type() == TokenType.lbrace:
            self.advance()
            self.statement_list()
            if self.current_type() != TokenType.rbrace:
                self.error("Expected '}' for do body")
            self.advance()
        else:
            self.statement()
        self.exit_scope()
        if self.current_type() != TokenType.retry:
            self.error("Expected 'retry' after do body")
        self.advance()
        if self.current_type() != TokenType.lparen:
            self.error("Expected '(' for do-while condition")
        self.advance()
        cond_type = self.expression()
        if cond_type != 'bool':
            self.error("Do-while condition must be bool")
        if self.current_type() != TokenType.rparen:
            self.error("Expected ')' after do-while condition")
        self.advance()
        if self.current_type() != TokenType.semicolon:
            self.error("Expected ';' after do-while")
        self.advance()

    def expression(self):
        typ = self.logical_or_expression()
        return typ

    def logical_or_expression(self):
        typ = self.logical_and_expression()
        while self.current_type() == TokenType.or_:
            self.advance()
            right_typ = self.logical_and_expression()
            if typ != 'bool' or right_typ != 'bool':
                self.error("|| requires bool operands")
            typ = 'bool'
        return typ

    def logical_and_expression(self):
        typ = self.equality_expression()
        while self.current_type() == TokenType.and_:
            self.advance()
            right_typ = self.equality_expression()
            if typ != 'bool' or right_typ != 'bool':
                self.error("&& requires bool operands")
            typ = 'bool'
        return typ

    def equality_expression(self):
        typ = self.relational_expression()
        while self.current_type() in [TokenType.eq, TokenType.neq]:
            op = self.current_type()
            self.advance()
            right_typ = self.relational_expression()
            if not self.check_type_compatible(typ, right_typ):
                self.error(f"{op} operands type mismatch ({typ} vs {right_typ})")
            typ = 'bool'
        return typ

    def relational_expression(self):
        typ = self.additive_expression()
        while self.current_type() in [TokenType.lt, TokenType.gt, TokenType.lte, TokenType.gte]:
            op = self.current_type()
            self.advance()
            right_typ = self.additive_expression()
            if not self.is_numeric_type(typ) or not self.is_numeric_type(right_typ):
                self.error(f"{op} requires numeric operands")
            typ = 'bool'
        return typ

    def additive_expression(self):
        typ = self.multiplicative_expression()
        while self.current_type() in [TokenType.plus, TokenType.minus]:
            op = self.current_type()
            self.advance()
            right_typ = self.multiplicative_expression()
            if op == TokenType.plus and typ == 'string' and right_typ == 'string':
                typ = 'string'
            elif not self.is_numeric_type(typ) or not self.is_numeric_type(right_typ):
                self.error(f"{op} requires numeric or string (for +) operands")
            typ = 'float' if 'float' in [typ, right_typ] else typ
        return typ

    def multiplicative_expression(self):
        typ = self.unary_expression()
        while self.current_type() in [TokenType.mul, TokenType.div, TokenType.mod]:
            op = self.current_type()
            self.advance()
            right_typ = self.unary_expression()
            if not self.is_numeric_type(typ) or not self.is_numeric_type(right_typ):
                self.error(f"{op} requires numeric operands")
            typ = 'float' if op == TokenType.div else typ
        return typ

    def unary_expression(self):
        if self.current_type() in [TokenType.plus, TokenType.minus, TokenType.not_, TokenType.increment, TokenType.decrement]:
            op = self.current_type()
            self.advance()
            typ = self.postfix_expression()
            if op == TokenType.not_:
                if typ != 'bool':
                    self.error("! requires bool")
                return 'bool'
            elif op in [TokenType.increment, TokenType.decrement]:
                if not self.is_numeric_type(typ):
                    self.error(f"{op} requires numeric")
                return typ
            else:  # +/-
                if not self.is_numeric_type(typ):
                    self.error(f"{op} requires numeric")
                return typ
        return self.postfix_expression()

    def postfix_expression(self):
        typ = self.primary_expression()
        while True:
            if self.current_type() in [TokenType.increment, TokenType.decrement]:
                op = self.current_type()
                self.advance()
                if not self.is_numeric_type(typ):
                    self.error(f"Postfix {op} requires numeric")
            elif self.current_type() == TokenType.lbracket:
                self.advance()
                index_typ = self.expression()
                if index_typ != 'int':
                    self.error("Array index must be int")
                if self.current_type() == TokenType.comma:
                    self.advance()
                    index_typ2 = self.expression()
                    if index_typ2 != 'int':
                        self.error("Array index must be int")
                if self.current_type() != TokenType.rbracket:
                    self.error("Expected ']' for array")
                self.advance()
            elif self.current_type() == TokenType.lparen:
                actual_args = []
                self.advance()
                while self.current_type() not in [TokenType.rparen, None]:
                    arg_typ = self.expression()
                    actual_args.append(arg_typ)
                    if self.current_type() == TokenType.comma:
                        self.advance()
                if self.current_type() != TokenType.rparen:
                    self.error("Expected ')' after call args")
                self.advance()
                func_id = self.tokens[self.pos - (len(actual_args)*2 + 3)].value if self.pos > 0 else ''  # Approximate
                self.check_function_call(func_id, actual_args)
            else:
                break
        return typ

    def primary_expression(self):
        t = self.current_type()
        if t == TokenType.identifier:
            id = self.current_value()
            typ = self.get_datatype(id)
            if not typ:
                return 'unknown'
            self.advance()
            return typ
        elif t in [TokenType.integer, TokenType.float, TokenType.string, TokenType.char, TokenType.buff, TokenType.nerf]:
            typ = self.map_token_to_datatype(t)
            self.advance()
            return typ
        elif t == TokenType.lparen:
            self.advance()
            typ = self.expression()
            if self.current_type() != TokenType.rparen:
                self.error("Expected ')'")
            self.advance()
            return typ
        else:
            self.error("Invalid primary expr")
            return 'unknown'

    def literal(self):
        t = self.current_type()
        if t in [TokenType.integer, TokenType.float, TokenType.string, TokenType.char, TokenType.buff, TokenType.nerf]:
            typ = self.map_token_to_datatype(t)
            self.advance()
            return typ
        self.error("Invalid literal")
        return 'unknown'