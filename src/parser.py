from .lexer import LexicalError, Position
from .token import Token
from .token_types import TokenType

class InvalidSyntaxError(Exception):
    def __init__(self, line, column, details=''):
        self.line = line
        self.column = column
        self.details = details

    def as_string(self):
        return f"Syntax Error at Ln {self.line}, Col {self.column}: {self.details}"

# ────────────────────────────────────────────────
# CONTEXT-FREE GRAMMAR
# ────────────────────────────────────────────────
CFG = {
    "<program>": [
        ["<global_section>", "<function_section>", "<main_function>"]  # 1
    ],
    "<global_section>": [
        ["<global_declaration>", "<global_section>"],  # 2
        []  # 3
    ],
    "<function_section>": [
        ["<function_definition>", "<function_section>"],  # 4
        []  # 5
    ],
    "<global_declaration>": [
        ["<variable_declaration>", ";"],  # 6 
        ["<constant_declaration>"],       # 7 
        ["<array_declaration>", ";"]      # 8 
    ],
    "<variable_declaration>": [
        ["<data_type>", "<identifier_init_list>"]  # 9
    ],
    "<identifier_init_list>": [
        ["<identifier_init>", "<init_tail>"]  # 10
    ],
    "<identifier_init>": [
        ["identifier", "<init_option>"]  # 11
    ],
    "<init_option>": [
        ["=", "<expression>"],  # 12
        ["(", "<expression>", ")"],  # 13
        ["{", "<expression>", "}"],  # 14
        []  # 15
    ],
    "<init_tail>": [
        [",", "<identifier_init>", "<init_tail>"],  # 16
        []  # 17
    ],
    "<constant_declaration>": [
        ["stun", "<data_type>", "identifier", "=", "<constant_value>", ";"]  # 18
    ],
    "<array_declaration>": [
        ["<data_type>", "identifier", "[", "<positive_integer>", "]", "<array_init>"]  # 19
    ],
    "<array_init>": [
        ["=", "{", "<value_list>", "}"],  # 20
        []  # 21
    ],
    "<value_list>": [
        ["<constant_value>", "<value_tail>"]  # 22
    ],
    "<value_tail>": [
        [",", "<constant_value>", "<value_tail>"],  # 23
        []  # 24
    ],
    "<function_definition>": [
        ["build", "<return_type>", "identifier", "(", "<parameters>", ")", "{", "<function_body>", "}"]  # 25
    ],
    "<main_function>": [
        ["frag", "lobby", "(", ")", "{", "<function_body>", "}"]  # 26
    ],
    "<function_body>": [
        ["<local_declaration_list>", "<statement_list>", "<return_statement>"]  # 27
    ],
    "<local_declaration_list>": [
        ["<local_declaration>", "<local_declaration_list>"],  # 28
        []  # 29
    ],
    "<local_declaration>": [
        ["<variable_declaration>", ";"],  # 30 
        ["<constant_declaration>"],       # 31 
        ["<array_declaration>", ";"]      # 32 
    ],
    "<return_type>": [
        ["frag"],     # 33
        ["elo"],      # 34
        ["ign"],      # 35
        ["surebol"],  # 36
        ["dodge"]     # 37
    ],
    "<parameters>": [
        ["<parameter_list>"],  # 38
        []  # 39
    ],
    "<parameter_list>": [
        ["<data_type>", "identifier", "<parameter_tail>"]  # 40
    ],
    "<parameter_tail>": [
        [",", "<data_type>", "identifier", "<parameter_tail>"],  # 41
        []  # 42
    ],
    "<statement_list>": [
        ["<statement>", "<statement_list>"],  # 43
        []  # 44
    ],
    "<statement>": [
        ["<declaration_statement>"],  # 45
        ["<executable_statement>"],   # 46
        ["<control_statement>"],      # 47
        ["<local_declaration>"]       # 48
    ],
    "<declaration_statement>": [
        ["<variable_declaration>", ";"],  # 49 
        ["<constant_declaration>"],       # 50 
        ["<array_declaration>", ";"]      # 51 
    ],
    "<executable_statement>": [
        ["<assignment_statement>"],  # 52
        ["<input_statement>"],       # 53
        ["<output_statement>"],      # 54
        ["<function_call_stmt>"],    # 55
        ["<break_statement>"],       # 56
        ["<continue_statement>"]     # 57
    ],
    "<control_statement>": [
        ["<if_statement>"],      # 58
        ["<switch_statement>"],  # 59
        ["<for_loop>"],          # 60
        ["<while_loop>"],        # 61
        ["<do_while_loop>"]      # 62
    ],
    "<assignment_statement>": [
        ["<lvalue>", "<assignment_operator>", "<expression>", ";"]  # 63
    ],
    "<lvalue>": [
        ["identifier", "<array_access>"]  # 64
    ],
    "<array_access>": [
        ["[", "<expression>", "]", "<array_access>"],  # 65
        []  # 66
    ],
    "<input_statement>": [
        ["comsat", "<input_list>", ";"]  # 67
    ],
    "<input_list>": [
        ["<lvalue>", "<input_tail>"]  # 68
    ],
    "<input_tail>": [
        [",", "<lvalue>", "<input_tail>"],  # 69
        []  # 70
    ],
    "<output_statement>": [
        ["shout", "<output_list>", ";"]  # 71
    ],
    "<output_list>": [
        ["<output_item>", "<output_tail>"]  # 72
    ],
    "<output_tail>": [
        [",", "<output_item>", "<output_tail>"],  # 73
        []  # 74
    ],
    "<output_item>": [
        ["<string_literal>"],  # 75
        ["<expression>"]       # 76
    ],
    "<function_call_stmt>": [
        ["<function_name>", "(", "<argument_list>", ")", ";"]  # 77
    ],
    "<function_call_expr>": [
        ["<function_name>", "(", "<argument_list>", ")"]  # 78
    ],
    "<function_name>": [
        ["identifier"],  # 79
        ["stack"], ["craft"], ["drop"], ["count"], ["split"]
    ],
    "<argument_list>": [
        ["<expression>", "<argument_tail>"],  # 80
        []  # 81
    ],
    "<argument_tail>": [
        [",", "<expression>", "<argument_tail>"],  # 82
        []  # 83
    ],
    "<break_statement>": [
        ["afk", ";"]  # 84
    ],
    "<continue_statement>": [
        ["hop", ";"]  # 85
    ],
    "<return_statement>": [
        ["ggwp", "<return_value>", ";"],  # 86
        []  # 87
    ],
    "<return_value>": [
        ["<expression>"],  # 88
        []  # 89
    ],
    "<if_statement>": [
        ["clutch", "(", "<condition>", ")", "{", "<statement_list>", "}", "<else_if_block>", "<else_block>"]  # 90
    ],
    "<else_if_block>": [
        ["<else_if>", "<else_if_block>"],  # 91
        []  # 92
    ],
    "<else_if>": [
        ["choke_clutch", "(", "<condition>", ")", "{", "<statement_list>", "}"]  # 93
    ],
    "<else_block>": [
        ["choke", "{", "<statement_list>", "}"],  # 94
        []  # 95
    ],
    "<switch_statement>": [
        ["pick", "(", "<expression>", ")", "{", "<case_blocks>", "<default_block>", "}"]  # 96
    ],
    "<case_blocks>": [
        ["<case_block>", "<case_blocks>"],  # 97
        []  # 98
    ],
    "<case_block>": [
        ["role", "<case_value>", ":", "<case_body>"]  # 99
    ],
    "<case_body>": [
        ["<statement_list>"]  # 100
    ],
    "<default_block>": [
        ["noob", ":", "<case_body>"],  # 101
        []  # 102
    ],
    "<for_loop>": [
        ["grind", "(", "<for_init>", ";", "<condition>", ";", "<for_update>", ")", "{", "<statement_list>", "}"]  # 103
    ],
    "<for_init>": [
        ["<variable_declaration>"],        # 104
        ["<assignment_statement_no_semi>"], # 105
        []                                 # 106
    ],
    "<assignment_statement_no_semi>": [
        ["<lvalue>", "<assignment_operator>", "<expression>"]  # 107
    ],
    "<for_update>": [
        ["<assignment_expression>", "<update_tail>"],  # 108
        []  # 109
    ],
    "<update_tail>": [
        [",", "<assignment_expression>", "<update_tail>"],  # 110
        []  # 111
    ],
    "<while_loop>": [
        ["retry", "(", "<condition>", ")", "{", "<statement_list>", "}"]  # 112
    ],
    "<do_while_loop>": [
        ["try", "{", "<statement_list>", "}", "retry", "(", "<condition>", ")", ";"]  # 113
    ],
    "<expression>": [
        ["<logical_or_expression>"]  # 114
    ],
    "<logical_or_expression>": [
        ["<logical_and_expression>", "<logical_or_tail>"]  # 115
    ],
    "<logical_or_tail>": [
        ["||", "<logical_and_expression>", "<logical_or_tail>"],  # 116
        []  # 117
    ],
    "<logical_and_expression>": [
        ["<equality_expression>", "<logical_and_tail>"]  # 118
    ],
    "<logical_and_tail>": [
        ["&&", "<equality_expression>", "<logical_and_tail>"],  # 119
        []  # 120
    ],
    "<equality_expression>": [
        ["<relational_expression>", "<equality_tail>"]  # 121
    ],
    "<equality_tail>": [
        ["<equality_op>", "<relational_expression>", "<equality_tail>"],  # 122
        []  # 123
    ],
    "<equality_op>": [
        ["=="],  # 124
        ["!="]   # 125
    ],
    "<relational_expression>": [
        ["<additive_expression>", "<relational_tail>"]  # 126
    ],
    "<relational_tail>": [
        ["<relational_op>", "<additive_expression>", "<relational_tail>"],  # 127
        []  # 128
    ],
    "<relational_op>": [
        ["<"], [">"], ["<="], [">="]  # 129-132
    ],
    "<additive_expression>": [
        ["<multiplicative_expression>", "<additive_tail>"]  # 133
    ],
    "<additive_tail>": [
        ["<additive_op>", "<multiplicative_expression>", "<additive_tail>"],  # 134
        []  # 135
    ],
    "<additive_op>": [
        ["+"],  # 136
        ["-"]   # 137
    ],
    "<multiplicative_expression>": [
        ["<unary_expression>", "<multiplicative_tail>"]  # 138
    ],
    "<multiplicative_tail>": [
        ["<multiplicative_op>", "<unary_expression>", "<multiplicative_tail>"],  # 139
        []  # 140
    ],
    "<multiplicative_op>": [
        ["*"],  # 141
        ["/"],  # 142
        ["%"]   # 143
    ],
    "<unary_expression>": [
        ["<unary_op>", "<unary_expression>"],  # 144
        ["<postfix_expression>"]  # 145
    ],
    "<unary_op>": [
        ["+"], ["-"], ["!"], ["++"], ["--"]  # 146-150
    ],
    "<postfix_expression>": [
        ["<primary_expression>", "<postfix_tail>"]  # 151
    ],
    "<postfix_tail>": [
        ["<postfix_op>"],  # 152
        ["<array_access>"], # 153
        ["<function_call_suffix>"], # 154
        []  # 155
    ],
    "<postfix_op>": [
        ["++"],  # 156
        ["--"]   # 157
    ],
    "<function_call_suffix>": [
        ["(", "<argument_list>", ")"]  # 158
    ],
    "<primary_expression>": [
        ["<literal>"],  # 159
        ["identifier"],  # 160
        ["(", "<expression>", ")"],  # 161
        ["<function_call_expr>"]  # 162
    ],
    "<data_type>": [
        ["frag"],  # 163
        ["elo"],   # 164
        ["ign"],   # 165
        ["surebol"], # 166
        ["tag"]   # 167
    ],
    "<assignment_operator>": [
        ["="], ["+="], ["-="], ["*="], ["/="], ["%="] # 168-173
    ],
    "<assignment_expression>": [
        ["<lvalue>", "<assignment_operator>", "<expression>"]  # 174
    ],
    "<condition>": [
        ["<expression>"]  # 175
    ],
    "<literal>": [
        ["<integer_literal>"], # 176
        ["<float_literal>"],   # 177
        ["<string_literal>"],  # 178
        ["<char_literal>"],    # 179
        ["<boolean_literal>"]  # 180
    ],
    "<boolean_literal>": [
        ["buff"],  # 193
        ["nerf"]   # 194
    ],
    "<constant_value>": [
        ["<const_add_expression>"]
    ],
    "<const_add_expression>": [
        ["<const_mul_expression>", "<const_add_tail>"]
    ],
    "<const_add_tail>": [
        ["+", "<const_mul_expression>", "<const_add_tail>"],
        ["-", "<const_mul_expression>", "<const_add_tail>"],
        []
    ],
    "<const_mul_expression>": [
        ["<const_primary>", "<const_mul_tail>"]
    ],
    "<const_mul_tail>": [
        ["*", "<const_primary>", "<const_mul_tail>"],
        ["/", "<const_primary>", "<const_mul_tail>"],
        ["%", "<const_primary>", "<const_mul_tail>"],
        []
    ],
    "<const_primary>": [
        ["<literal>"],
        ["(", "<constant_value>", ")"]
    ],
    "<case_value>": [
        ["<integer_literal>"], # 185
        ["<char_literal>"],    # 186
        ["<string_literal>"],  # 187
        ["<boolean_literal>"]  # 188
    ],
    "<integer_literal>": [["integer"]], # 189
    "<float_literal>": [["float"]],     # 190
    "<string_literal>": [["string"]],   # 191
    "<char_literal>": [["char"]], # 192
    "<positive_integer>": [["integer"]] # 195
}

# ────────────────────────────────────────────────
# PREDICT SET
# ────────────────────────────────────────────────
PREDICT_SET = {
    "<program>": {
        "frag": ["<program>", 0],
        "elo": ["<program>", 0],
        "ign": ["<program>", 0],
        "surebol": ["<program>", 0],
        "tag": ["<program>", 0],
        "stun": ["<program>", 0],
        "build": ["<program>", 0]
    },
    "<global_section>": {
        "frag": ["<global_section>", 0],
        "elo": ["<global_section>", 0],
        "ign": ["<global_section>", 0],
        "surebol": ["<global_section>", 0],
        "tag": ["<global_section>", 0],
        "stun": ["<global_section>", 0],
        "build": ["<global_section>", 1]
    },
    "<function_section>": {
        "build": ["<function_section>", 0],
        "frag": ["<function_section>", 1]
    },
    "<global_declaration>": {
        "frag": ["<global_declaration>", 0],
        "elo": ["<global_declaration>", 0],
        "ign": ["<global_declaration>", 0],
        "surebol": ["<global_declaration>", 0],
        "tag": ["<global_declaration>", 0],
        "stun": ["<global_declaration>", 1]
    },
    "<variable_declaration>": {
        "frag": ["<variable_declaration>", 0],
        "elo": ["<variable_declaration>", 0],
        "ign": ["<variable_declaration>", 0],
        "surebol": ["<variable_declaration>", 0],
        "tag": ["<variable_declaration>", 0]
    },
    "<identifier_init_list>": {
        "identifier": ["<identifier_init_list>", 0]
    },
    "<identifier_init>": {
        "identifier": ["<identifier_init>", 0]
    },
    "<init_option>": {
        "=": ["<init_option>", 0],
        "(": ["<init_option>", 1],
        "{": ["<init_option>", 2],
        ",": ["<init_option>", 3],
        ";": ["<init_option>", 3]
    },
    "<init_tail>": {
        ",": ["<init_tail>", 0],
        ";": ["<init_tail>", 1]
    },
    "<constant_declaration>": {
        "stun": ["<constant_declaration>", 0]
    },
    "<array_declaration>": {
        "frag": ["<array_declaration>", 0],
        "elo": ["<array_declaration>", 0],
        "ign": ["<array_declaration>", 0],
        "surebol": ["<array_declaration>", 0],
        "tag": ["<array_declaration>", 0]
    },
    "<array_init>": {
        "=": ["<array_init>", 0],
        ";": ["<array_init>", 1]
    },
    "<value_list>": {
        "integer": ["<value_list>", 0],
        "float": ["<value_list>", 0],
        "string": ["<value_list>", 0],
        "char": ["<value_list>", 0],
        "buff": ["<value_list>", 0],
        "nerf": ["<value_list>", 0],
        "(": ["<value_list>", 0]
    },
    "<value_tail>": {
        ",": ["<value_tail>", 0],
        "}": ["<value_tail>", 1]
    },
    "<function_definition>": {
        "build": ["<function_definition>", 0]
    },
    "<main_function>": {
        "frag": ["<main_function>", 0]
    },
    "<function_body>": {
        "frag": ["<function_body>", 0],
        "elo": ["<function_body>", 0],
        "ign": ["<function_body>", 0],
        "surebol": ["<function_body>", 0],
        "tag": ["<function_body>", 0],
        "stun": ["<function_body>", 0],
        "identifier": ["<function_body>", 0],
        "comsat": ["<function_body>", 0],
        "shout": ["<function_body>", 0],
        "afk": ["<function_body>", 0],
        "hop": ["<function_body>", 0],
        "clutch": ["<function_body>", 0],
        "pick": ["<function_body>", 0],
        "grind": ["<function_body>", 0],
        "retry": ["<function_body>", 0],
        "try": ["<function_body>", 0],
        "ggwp": ["<function_body>", 0],
        "}": ["<function_body>", 0]
    },
    "<local_declaration_list>": {
        "frag": ["<local_declaration_list>", 0],
        "elo": ["<local_declaration_list>", 0],
        "ign": ["<local_declaration_list>", 0],
        "surebol": ["<local_declaration_list>", 0],
        "tag": ["<local_declaration_list>", 0],
        "stun": ["<local_declaration_list>", 0],
        "identifier": ["<local_declaration_list>", 1],
        "comsat": ["<local_declaration_list>", 1],
        "shout": ["<local_declaration_list>", 1],
        "afk": ["<local_declaration_list>", 1],
        "hop": ["<local_declaration_list>", 1],
        "clutch": ["<local_declaration_list>", 1],
        "pick": ["<local_declaration_list>", 1],
        "grind": ["<local_declaration_list>", 1],
        "retry": ["<local_declaration_list>", 1],
        "try": ["<local_declaration_list>", 1],
        "ggwp": ["<local_declaration_list>", 1],
        "}": ["<local_declaration_list>", 1]
    },
    "<local_declaration>": {
        "frag": ["<local_declaration>", 0],
        "elo": ["<local_declaration>", 0],
        "ign": ["<local_declaration>", 0],
        "surebol": ["<local_declaration>", 0],
        "tag": ["<local_declaration>", 0],
        "stun": ["<local_declaration>", 1]
    },
    "<return_type>": {
        "frag": ["<return_type>", 0],
        "elo": ["<return_type>", 1],
        "ign": ["<return_type>", 2],
        "surebol": ["<return_type>", 3],
        "dodge": ["<return_type>", 4]
    },
    "<data_type>": {
        "frag":    ["<data_type>", 0],
        "elo":     ["<data_type>", 1],
        "ign":     ["<data_type>", 2],
        "surebol": ["<data_type>", 3],
        "tag":     ["<data_type>", 4]
    },
    "<parameters>": {
        "frag": ["<parameters>", 0],
        "elo": ["<parameters>", 0],
        "ign": ["<parameters>", 0],
        "surebol": ["<parameters>", 0],
        "tag": ["<parameters>", 0],
        ")": ["<parameters>", 1]
    },
    "<parameter_list>": {
        "frag": ["<parameter_list>", 0],
        "elo": ["<parameter_list>", 0],
        "ign": ["<parameter_list>", 0],
        "surebol": ["<parameter_list>", 0],
        "tag": ["<parameter_list>", 0]
    },
    "<parameter_tail>": {
        ",": ["<parameter_tail>", 0],
        ")": ["<parameter_tail>", 1]
    },
    "<statement_list>": {
        "frag": ["<statement_list>", 0],
        "elo": ["<statement_list>", 0],
        "ign": ["<statement_list>", 0],
        "surebol": ["<statement_list>", 0],
        "tag": ["<statement_list>", 0],
        "stun": ["<statement_list>", 0],
        "identifier": ["<statement_list>", 0],
        "comsat": ["<statement_list>", 0],
        "shout": ["<statement_list>", 0],
        "afk": ["<statement_list>", 0],
        "hop": ["<statement_list>", 0],
        "clutch": ["<statement_list>", 0],
        "pick": ["<statement_list>", 0],
        "grind": ["<statement_list>", 0],
        "retry": ["<statement_list>", 0],
        "try": ["<statement_list>", 0],
        "ggwp": ["<statement_list>", 1],
        "}": ["<statement_list>", 1],
        "role": ["<statement_list>", 1],
        "noob": ["<statement_list>", 1]
    },
    "<statement>": {
        "frag": ["<statement>", 3],
        "elo": ["<statement>", 3],
        "ign": ["<statement>", 3],
        "surebol": ["<statement>", 3],
        "tag": ["<statement>", 3],
        "stun": ["<statement>", 3],
        "identifier": ["<statement>", 1],
        "comsat": ["<statement>", 1],
        "shout": ["<statement>", 1],
        "afk": ["<statement>", 1],
        "hop": ["<statement>", 1],
        "stack": ["<statement>", 1],
        "craft": ["<statement>", 1],
        "drop": ["<statement>", 1],
        "count": ["<statement>", 1],
        "split": ["<statement>", 1],
        "clutch": ["<statement>", 2],
        "pick": ["<statement>", 2],
        "grind": ["<statement>", 2],
        "retry": ["<statement>", 2],
        "try": ["<statement>", 2]
    },
    "<declaration_statement>": {
        "frag": ["<declaration_statement>", 0],
        "elo": ["<declaration_statement>", 0],
        "ign": ["<declaration_statement>", 0],
        "surebol": ["<declaration_statement>", 0],
        "tag": ["<declaration_statement>", 0],
        "stun": ["<declaration_statement>", 1]
    },
    "<executable_statement>": {
        "identifier": ["<executable_statement>", 0],
        "comsat": ["<executable_statement>", 1],
        "shout": ["<executable_statement>", 2],
        "stack": ["<executable_statement>", 3],
        "craft": ["<executable_statement>", 3],
        "drop": ["<executable_statement>", 3],
        "count": ["<executable_statement>", 3],
        "split": ["<executable_statement>", 3],
        "afk": ["<executable_statement>", 4],
        "hop": ["<executable_statement>", 5]
    },
    "<control_statement>": {
        "clutch": ["<control_statement>", 0],
        "pick": ["<control_statement>", 1],
        "grind": ["<control_statement>", 2],
        "retry": ["<control_statement>", 3],
        "try": ["<control_statement>", 4]
    },
    "<assignment_statement>": {
        "identifier": ["<assignment_statement>", 0]
    },
    "<lvalue>": {
        "identifier": ["<lvalue>", 0]
    },
    "<array_access>": {
        "[": ["<array_access>", 0],
        "=": ["<array_access>", 1],
        "+=": ["<array_access>", 1],
        "-=": ["<array_access>", 1],
        "*=": ["<array_access>", 1],
        "/=": ["<array_access>", 1],
        "%=": ["<array_access>", 1],
        ";": ["<array_access>", 1],
        ")": ["<array_access>", 1],
        ",": ["<array_access>", 1],
        "]": ["<array_access>", 1]
    },
    "<input_statement>": {
        "comsat": ["<input_statement>", 0]
    },
    "<input_list>": {
        "identifier": ["<input_list>", 0]
    },
    "<input_tail>": {
        ",": ["<input_tail>", 0],
        ";": ["<input_tail>", 1]
    },
    "<output_statement>": {
        "shout": ["<output_statement>", 0]
    },
    "<output_list>": {
        "string": ["<output_list>", 0],
        "+": ["<output_list>", 0],
        "-": ["<output_list>", 0],
        "!": ["<output_list>", 0],
        "++": ["<output_list>", 0],
        "--": ["<output_list>", 0],
        "integer": ["<output_list>", 0],
        "float": ["<output_list>", 0],
        "char": ["<output_list>", 0],
        "buff": ["<output_list>", 0],
        "nerf": ["<output_list>", 0],
        "identifier": ["<output_list>", 0],
        "(": ["<output_list>", 0]
    },
    "<output_tail>": {
        ",": ["<output_tail>", 0],
        ";": ["<output_tail>", 1]
    },
    "<output_item>": {
        "string": ["<output_item>", 0],
        "+": ["<output_item>", 1],
        "-": ["<output_item>", 1],
        "!": ["<output_item>", 1],
        "++": ["<output_item>", 1],
        "--": ["<output_item>", 1],
        "integer": ["<output_item>", 1],
        "float": ["<output_item>", 1],
        "char": ["<output_item>", 1],
        "buff": ["<output_item>", 1],
        "nerf": ["<output_item>", 1],
        "identifier": ["<output_item>", 1],
        "(": ["<output_item>", 1]
    },
    "<function_call_stmt>": {
        "identifier": ["<function_call_stmt>", 0],
        "stack": ["<function_call_stmt>", 0],
        "craft": ["<function_call_stmt>", 0],
        "drop": ["<function_call_stmt>", 0],
        "count": ["<function_call_stmt>", 0],
        "split": ["<function_call_stmt>", 0]
    },
    "<function_call_expr>": {
        "identifier": ["<function_call_expr>", 0],
        "stack": ["<function_call_expr>", 0],
        "craft": ["<function_call_expr>", 0],
        "drop": ["<function_call_expr>", 0],
        "count": ["<function_call_expr>", 0],
        "split": ["<function_call_expr>", 0]
    },
    "<function_name>": {
        "identifier": ["<function_name>", 0],
        "stack": ["<function_name>", 1],
        "craft": ["<function_name>", 2],
        "drop": ["<function_name>", 3],
        "count": ["<function_name>", 4],
        "split": ["<function_name>", 5]
    },
    "<argument_list>": {
        "+": ["<argument_list>", 0],
        "-": ["<argument_list>", 0],
        "!": ["<argument_list>", 0],
        "++": ["<argument_list>", 0],
        "--": ["<argument_list>", 0],
        "integer": ["<argument_list>", 0],
        "float": ["<argument_list>", 0],
        "string": ["<argument_list>", 0],
        "char": ["<argument_list>", 0],
        "buff": ["<argument_list>", 0],
        "nerf": ["<argument_list>", 0],
        "identifier": ["<argument_list>", 0],
        "(": ["<argument_list>", 0],
        ")": ["<argument_list>", 1]
    },
    "<argument_tail>": {
        ",": ["<argument_tail>", 0],
        ")": ["<argument_tail>", 1]
    },
    "<break_statement>": {
        "afk": ["<break_statement>", 0]
    },
    "<continue_statement>": {
        "hop": ["<continue_statement>", 0]
    },
    "<return_statement>": {
        "ggwp": ["<return_statement>", 0],
        "}": ["<return_statement>", 1]
    },
    "<return_value>": {
        "+": ["<return_value>", 0],
        "-": ["<return_value>", 0],
        "!": ["<return_value>", 0],
        "++": ["<return_value>", 0],
        "--": ["<return_value>", 0],
        "integer": ["<return_value>", 0],
        "float": ["<return_value>", 0],
        "string": ["<return_value>", 0],
        "char": ["<return_value>", 0],
        "buff": ["<return_value>", 0],
        "nerf": ["<return_value>", 0],
        "identifier": ["<return_value>", 0],
        "(": ["<return_value>", 0],
        ";": ["<return_value>", 1]
    },
    "<if_statement>": {
        "clutch": ["<if_statement>", 0]
    },
    "<else_if_block>": {
        "choke_clutch": ["<else_if_block>", 0],
        "choke": ["<else_if_block>", 1],
        "frag": ["<else_if_block>", 1],
        "elo": ["<else_if_block>", 1],
        "ign": ["<else_if_block>", 1],
        "surebol": ["<else_if_block>", 1],
        "tag": ["<else_if_block>", 1],
        "stun": ["<else_if_block>", 1],
        "identifier": ["<else_if_block>", 1],
        "comsat": ["<else_if_block>", 1],
        "shout": ["<else_if_block>", 1],
        "afk": ["<else_if_block>", 1],
        "hop": ["<else_if_block>", 1],
        "clutch": ["<else_if_block>", 1],
        "pick": ["<else_if_block>", 1],
        "grind": ["<else_if_block>", 1],
        "retry": ["<else_if_block>", 1],
        "try": ["<else_if_block>", 1],
        "ggwp": ["<else_if_block>", 1],
        "}": ["<else_if_block>", 1]
    },
    "<else_if>": {
        "choke_clutch": ["<else_if>", 0]
    },
    "<else_block>": {
        "choke": ["<else_block>", 0],
        "frag": ["<else_block>", 1],
        "elo": ["<else_block>", 1],
        "ign": ["<else_block>", 1],
        "surebol": ["<else_block>", 1],
        "tag": ["<else_block>", 1],
        "stun": ["<else_block>", 1],
        "identifier": ["<else_block>", 1],
        "comsat": ["<else_block>", 1],
        "shout": ["<else_block>", 1],
        "afk": ["<else_block>", 1],
        "hop": ["<else_block>", 1],
        "clutch": ["<else_block>", 1],
        "pick": ["<else_block>", 1],
        "grind": ["<else_block>", 1],
        "retry": ["<else_block>", 1],
        "try": ["<else_block>", 1],
        "ggwp": ["<else_block>", 1],
        "}": ["<else_block>", 1]
    },
    "<switch_statement>": {
        "pick": ["<switch_statement>", 0]
    },
    "<case_blocks>": {
        "role": ["<case_blocks>", 0],
        "noob": ["<case_blocks>", 1],
        "}": ["<case_blocks>", 1]
    },
    "<case_block>": {
        "role": ["<case_block>", 0]
    },
    "<case_body>": {
        "frag": ["<case_body>", 0],
        "elo": ["<case_body>", 0],
        "ign": ["<case_body>", 0],
        "surebol": ["<case_body>", 0],
        "tag": ["<case_body>", 0],
        "stun": ["<case_body>", 0],
        "identifier": ["<case_body>", 0],
        "comsat": ["<case_body>", 0],
        "shout": ["<case_body>", 0],
        "afk": ["<case_body>", 0],
        "hop": ["<case_body>", 0],
        "clutch": ["<case_body>", 0],
        "pick": ["<case_body>", 0],
        "grind": ["<case_body>", 0],
        "retry": ["<case_body>", 0],
        "try": ["<case_body>", 0],
        "role": ["<case_body>", 0],
        "noob": ["<case_body>", 0],
        "}": ["<case_body>", 0]
    },
    "<default_block>": {
        "noob": ["<default_block>", 0],
        "}": ["<default_block>", 1]
    },
    "<for_loop>": {
        "grind": ["<for_loop>", 0]
    },
    "<for_init>": {
        "frag": ["<for_init>", 0],
        "elo": ["<for_init>", 0],
        "ign": ["<for_init>", 0],
        "surebol": ["<for_init>", 0],
        "tag": ["<for_init>", 0],
        "identifier": ["<for_init>", 1],
        ";": ["<for_init>", 2]
    },
    "<assignment_statement_no_semi>": {
        "identifier": ["<assignment_statement_no_semi>", 0]
    },
    "<for_update>": {
        "identifier": ["<for_update>", 0],
        ")": ["<for_update>", 1]
    },
    "<update_tail>": {
        ",": ["<update_tail>", 0],
        ")": ["<update_tail>", 1]
    },
    "<while_loop>": {
        "retry": ["<while_loop>", 0]
    },
    "<do_while_loop>": {
        "try": ["<do_while_loop>", 0]
    },
    "<expression>": {
        "+": ["<expression>", 0],
        "-": ["<expression>", 0],
        "!": ["<expression>", 0],
        "++": ["<expression>", 0],
        "--": ["<expression>", 0],
        "integer": ["<expression>", 0],
        "float": ["<expression>", 0],
        "string": ["<expression>", 0],
        "char": ["<expression>", 0],
        "buff": ["<expression>", 0],
        "nerf": ["<expression>", 0],
        "identifier": ["<expression>", 0],
        "(": ["<expression>", 0]
    },
    "<logical_or_expression>": {
        "+": ["<logical_or_expression>", 0],
        "-": ["<logical_or_expression>", 0],
        "!": ["<logical_or_expression>", 0],
        "++": ["<logical_or_expression>", 0],
        "--": ["<logical_or_expression>", 0],
        "integer": ["<logical_or_expression>", 0],
        "float": ["<logical_or_expression>", 0],
        "string": ["<logical_or_expression>", 0],
        "char": ["<logical_or_expression>", 0],
        "buff": ["<logical_or_expression>", 0],
        "nerf": ["<logical_or_expression>", 0],
        "identifier": ["<logical_or_expression>", 0],
        "(": ["<logical_or_expression>", 0]
    },
    "<logical_or_tail>": {
        "||": ["<logical_or_tail>", 0],
        ")": ["<logical_or_tail>", 1],
        ";": ["<logical_or_tail>", 1],
        ",": ["<logical_or_tail>", 1],
        "]": ["<logical_or_tail>", 1]
    },
    "<logical_and_expression>": {
        "+": ["<logical_and_expression>", 0],
        "-": ["<logical_and_expression>", 0],
        "!": ["<logical_and_expression>", 0],
        "++": ["<logical_and_expression>", 0],
        "--": ["<logical_and_expression>", 0],
        "integer": ["<logical_and_expression>", 0],
        "float": ["<logical_and_expression>", 0],
        "string": ["<logical_and_expression>", 0],
        "char": ["<logical_and_expression>", 0],
        "buff": ["<logical_and_expression>", 0],
        "nerf": ["<logical_and_expression>", 0],
        "identifier": ["<logical_and_expression>", 0],
        "(": ["<logical_and_expression>", 0]
    },
    "<logical_and_tail>": {
        "&&": ["<logical_and_tail>", 0],
        "||": ["<logical_and_tail>", 1],
        ")": ["<logical_and_tail>", 1],
        ";": ["<logical_and_tail>", 1],
        ",": ["<logical_and_tail>", 1],
        "]": ["<logical_and_tail>", 1]
    },
    "<equality_expression>": {
        "+": ["<equality_expression>", 0],
        "-": ["<equality_expression>", 0],
        "!": ["<equality_expression>", 0],
        "++": ["<equality_expression>", 0],
        "--": ["<equality_expression>", 0],
        "integer": ["<equality_expression>", 0],
        "float": ["<equality_expression>", 0],
        "string": ["<equality_expression>", 0],
        "char": ["<equality_expression>", 0],
        "buff": ["<equality_expression>", 0],
        "nerf": ["<equality_expression>", 0],
        "identifier": ["<equality_expression>", 0],
        "(": ["<equality_expression>", 0]
    },
    "<equality_tail>": {
        "==": ["<equality_tail>", 0],
        "!=": ["<equality_tail>", 0],
        "&&": ["<equality_tail>", 1],
        "||": ["<equality_tail>", 1],
        ")": ["<equality_tail>", 1],
        ";": ["<equality_tail>", 1],
        ",": ["<equality_tail>", 1],
        "]": ["<equality_tail>", 1]
    },
    "<equality_op>": {
        "==": ["<equality_op>", 0],
        "!=": ["<equality_op>", 1]
    },
    "<relational_expression>": {
        "+": ["<relational_expression>", 0],
        "-": ["<relational_expression>", 0],
        "!": ["<relational_expression>", 0],
        "++": ["<relational_expression>", 0],
        "--": ["<relational_expression>", 0],
        "integer": ["<relational_expression>", 0],
        "float": ["<relational_expression>", 0],
        "string": ["<relational_expression>", 0],
        "char": ["<relational_expression>", 0],
        "buff": ["<relational_expression>", 0],
        "nerf": ["<relational_expression>", 0],
        "identifier": ["<relational_expression>", 0],
        "(": ["<relational_expression>", 0]
    },
    "<relational_tail>": {
        "<": ["<relational_tail>", 0],
        ">": ["<relational_tail>", 0],
        "<=": ["<relational_tail>", 0],
        ">=": ["<relational_tail>", 0],
        "==": ["<relational_tail>", 1],
        "!=": ["<relational_tail>", 1],
        "&&": ["<relational_tail>", 1],
        "||": ["<relational_tail>", 1],
        ")": ["<relational_tail>", 1],
        ";": ["<relational_tail>", 1],
        ",": ["<relational_tail>", 1],
        "]": ["<relational_tail>", 1]
    },
    "<relational_op>": {
        "<":  ["<relational_op>", 0],
        ">":  ["<relational_op>", 1],
        "<=": ["<relational_op>", 2],
        ">=": ["<relational_op>", 3]
    },
    "<additive_expression>": {
        "+": ["<additive_expression>", 0],
        "-": ["<additive_expression>", 0],
        "!": ["<additive_expression>", 0],
        "++": ["<additive_expression>", 0],
        "--": ["<additive_expression>", 0],
        "integer": ["<additive_expression>", 0],
        "float": ["<additive_expression>", 0],
        "string": ["<additive_expression>", 0],
        "char": ["<additive_expression>", 0],
        "buff": ["<additive_expression>", 0],
        "nerf": ["<additive_expression>", 0],
        "identifier": ["<additive_expression>", 0],
        "(": ["<additive_expression>", 0]
    },
    "<additive_tail>": {
        "+": ["<additive_tail>", 0],
        "-": ["<additive_tail>", 0],
        "<": ["<additive_tail>", 1],
        ">": ["<additive_tail>", 1],
        "<=": ["<additive_tail>", 1],
        ">=": ["<additive_tail>", 1],
        "==": ["<additive_tail>", 1],
        "!=": ["<additive_tail>", 1],
        "&&": ["<additive_tail>", 1],
        "||": ["<additive_tail>", 1],
        ")": ["<additive_tail>", 1],
        ";": ["<additive_tail>", 1],
        ",": ["<additive_tail>", 1],
        "]": ["<additive_tail>", 1]
    },
    "<additive_op>": {
        "+": ["<additive_op>", 0],
        "-": ["<additive_op>", 1]
    },
    "<multiplicative_expression>": {
        "+": ["<multiplicative_expression>", 0],
        "-": ["<multiplicative_expression>", 0],
        "!": ["<multiplicative_expression>", 0],
        "++": ["<multiplicative_expression>", 0],
        "--": ["<multiplicative_expression>", 0],
        "integer": ["<multiplicative_expression>", 0],
        "float": ["<multiplicative_expression>", 0],
        "string": ["<multiplicative_expression>", 0],
        "char": ["<multiplicative_expression>", 0],
        "buff": ["<multiplicative_expression>", 0],
        "nerf": ["<multiplicative_expression>", 0],
        "identifier": ["<multiplicative_expression>", 0],
        "(": ["<multiplicative_expression>", 0]
    },
    "<multiplicative_tail>": {
        "*": ["<multiplicative_tail>", 0],
        "/": ["<multiplicative_tail>", 0],
        "%": ["<multiplicative_tail>", 0],
        "+": ["<multiplicative_tail>", 1],
        "-": ["<multiplicative_tail>", 1],
        "<": ["<multiplicative_tail>", 1],
        ">": ["<multiplicative_tail>", 1],
        "<=": ["<multiplicative_tail>", 1],
        ">=": ["<multiplicative_tail>", 1],
        "==": ["<multiplicative_tail>", 1],
        "!=": ["<multiplicative_tail>", 1],
        "&&": ["<multiplicative_tail>", 1],
        "||": ["<multiplicative_tail>", 1],
        ")": ["<multiplicative_tail>", 1],
        ";": ["<multiplicative_tail>", 1],
        ",": ["<multiplicative_tail>", 1],
        "]": ["<multiplicative_tail>", 1]
    },
    "<multiplicative_op>": {
        "*": ["<multiplicative_op>", 0],
        "/": ["<multiplicative_op>", 1],
        "%": ["<multiplicative_op>", 2]
    },
    "<unary_expression>": {
        "+": ["<unary_expression>", 0],
        "-": ["<unary_expression>", 0],
        "!": ["<unary_expression>", 0],
        "++": ["<unary_expression>", 0],
        "--": ["<unary_expression>", 0],
        "integer": ["<unary_expression>", 1],
        "float": ["<unary_expression>", 1],
        "string": ["<unary_expression>", 1],
        "char": ["<unary_expression>", 1],
        "buff": ["<unary_expression>", 1],
        "nerf": ["<unary_expression>", 1],
        "identifier": ["<unary_expression>", 1],
        "(": ["<unary_expression>", 1]
    },
    "<unary_op>": {
        "+":  ["<unary_op>", 0],
        "-":  ["<unary_op>", 1],
        "!":  ["<unary_op>", 2],
        "++": ["<unary_op>", 3],
        "--": ["<unary_op>", 4]
    },
    "<postfix_expression>": {
        "integer": ["<postfix_expression>", 0],
        "float": ["<postfix_expression>", 0],
        "string": ["<postfix_expression>", 0],
        "char": ["<postfix_expression>", 0],
        "buff": ["<postfix_expression>", 0],
        "nerf": ["<postfix_expression>", 0],
        "identifier": ["<postfix_expression>", 0],
        "(": ["<postfix_expression>", 0]
    },
    "<postfix_tail>": {
        "++": ["<postfix_tail>", 0],
        "--": ["<postfix_tail>", 0],
        "[": ["<postfix_tail>", 1],
        "(": ["<postfix_tail>", 2],
        "+": ["<postfix_tail>", 3],
        "-": ["<postfix_tail>", 3],
        "*": ["<postfix_tail>", 3],
        "/": ["<postfix_tail>", 3],
        "%": ["<postfix_tail>", 3],
        "<": ["<postfix_tail>", 3],
        ">": ["<postfix_tail>", 3],
        "<=": ["<postfix_tail>", 3],
        ">=": ["<postfix_tail>", 3],
        "==": ["<postfix_tail>", 3],
        "!=": ["<postfix_tail>", 3],
        "&&": ["<postfix_tail>", 3],
        "||": ["<postfix_tail>", 3],
        ")": ["<postfix_tail>", 3],
        ";": ["<postfix_tail>", 3],
        ",": ["<postfix_tail>", 3],
        "]": ["<postfix_tail>", 3]
    },
    "<postfix_op>": {
        "++": ["<postfix_op>", 0],
        "--": ["<postfix_op>", 1]
    },
    "<function_call_suffix>": {
        "(": ["<function_call_suffix>", 0]
    },
    "<primary_expression>": {
        "integer": ["<primary_expression>", 0],
        "float": ["<primary_expression>", 0],
        "string": ["<primary_expression>", 0],
        "char": ["<primary_expression>", 0],
        "buff": ["<primary_expression>", 0],
        "nerf": ["<primary_expression>", 0],
        "identifier": ["<primary_expression>", 1],
        "(": ["<primary_expression>", 2],
        "stack": ["<primary_expression>", 3],
        "craft": ["<primary_expression>", 3],
        "drop": ["<primary_expression>", 3],
        "count": ["<primary_expression>", 3],
        "split": ["<primary_expression>", 3]
    },
    "<case_value>": {
        "integer": ["<case_value>", 0],
        "char": ["<case_value>", 1],
        "string": ["<case_value>", 2],
        "buff": ["<case_value>", 3],
        "nerf": ["<case_value>", 3]
    },
    "<boolean_literal>": {
        "buff": ["<boolean_literal>", 0],
        "nerf": ["<boolean_literal>", 1]
    },
    "<constant_value>": {
        "integer": ["<constant_value>", 0],
        "float": ["<constant_value>", 0],
        "string": ["<constant_value>", 0],
        "char": ["<constant_value>", 0],
        "buff": ["<constant_value>", 0],
        "nerf": ["<constant_value>", 0],
        "(": ["<constant_value>", 0]
    },
    "<const_add_expression>": {
        "integer": ["<const_add_expression>", 0],
        "float": ["<const_add_expression>", 0],
        "string": ["<const_add_expression>", 0],
        "char": ["<const_add_expression>", 0],
        "buff": ["<const_add_expression>", 0],
        "nerf": ["<const_add_expression>", 0],
        "(": ["<const_add_expression>", 0]
    },
    "<const_add_tail>": {
        "+": ["<const_add_tail>", 0],
        "-": ["<const_add_tail>", 1],
        ")": ["<const_add_tail>", 2],
        ";": ["<const_add_tail>", 2],
        ",": ["<const_add_tail>", 2],
        "}": ["<const_add_tail>", 2]
    },
    "<const_mul_expression>": {
        "integer": ["<const_mul_expression>", 0],
        "float": ["<const_mul_expression>", 0],
        "string": ["<const_mul_expression>", 0],
        "char": ["<const_mul_expression>", 0],
        "buff": ["<const_mul_expression>", 0],
        "nerf": ["<const_mul_expression>", 0],
        "(": ["<const_mul_expression>", 0]
    },
    "<const_mul_tail>": {
        "*": ["<const_mul_tail>", 0],
        "/": ["<const_mul_tail>", 1],
        "%": ["<const_mul_tail>", 2],
        "+": ["<const_mul_tail>", 3],
        "-": ["<const_mul_tail>", 3],
        ")": ["<const_mul_tail>", 3],
        ";": ["<const_mul_tail>", 3],
        ",": ["<const_mul_tail>", 3],
        "}": ["<const_mul_tail>", 3]
    },
    "<const_primary>": {
        "integer": ["<const_primary>", 0],
        "float": ["<const_primary>", 0],
        "string": ["<const_primary>", 0],
        "char": ["<const_primary>", 0],
        "buff": ["<const_primary>", 0],
        "nerf": ["<const_primary>", 0],
        "(": ["<const_primary>", 1]
    },
    "<condition>": {
        "+": ["<condition>", 0],
        "-": ["<condition>", 0],
        "!": ["<condition>", 0],
        "++": ["<condition>", 0],
        "--": ["<condition>", 0],
        "integer": ["<condition>", 0],
        "float": ["<condition>", 0],
        "string": ["<condition>", 0],
        "char": ["<condition>", 0],
        "buff": ["<condition>", 0],
        "nerf": ["<condition>", 0],
        "identifier": ["<condition>", 0],
        "(": ["<condition>", 0]
    },
    "<literal>": {
        "integer": ["<literal>", 0],
        "float": ["<literal>", 1],
        "string": ["<literal>", 2],
        "char": ["<literal>", 3],
        "buff": ["<literal>", 4],
        "nerf": ["<literal>", 4]
    },
    "<assignment_expression>": {
        "identifier": ["<assignment_expression>", 0]
    },
    "<assignment_operator>": {
        "=":  ["<assignment_operator>", 0],
        "+=": ["<assignment_operator>", 1],
        "-=": ["<assignment_operator>", 2],
        "*=": ["<assignment_operator>", 3],
        "/=": ["<assignment_operator>", 4],
        "%=": ["<assignment_operator>", 5]
    },
    "<integer_literal>": {
        "integer": ["<integer_literal>", 0]
    },
    "<float_literal>": {
        "float": ["<float_literal>", 0]
    },
    "<string_literal>": {
        "string": ["<string_literal>", 0]
    },
    "<char_literal>": {
        "char": ["<char_literal>", 0]
    },
    "<positive_integer>": {
        "integer": ["<positive_integer>", 0]
    }
}

# ────────────────────────────────────────────────
# SYNTAX ANALYZER
# ────────────────────────────────────────────────
class SyntaxAnalyzer:
    def __init__(self, tokens):
        # Filter tokens (exclude comments/whitespace)
        self.tokens = [t for t in tokens if t.type not in [
            TokenType.whitespace, 
            TokenType.newline, 
            TokenType.comment, 
            TokenType.eof
        ]]
        self.token_idx = -1
        self.advance()

    def advance(self):
        self.token_idx += 1
        if self.token_idx < len(self.tokens):
            self.current_token = self.tokens[self.token_idx]
            # Use map_token_type to translate Lexer Type -> Grammar Symbol
            self.current_type = self.map_token_type(self.current_token)
        else:
            self.current_token = Token(TokenType.eof, None, line=-1, column=-1)
            self.current_type = 'eof'

    def peek(self):
        """Returns the type of the NEXT token without consuming it."""
        if self.token_idx + 1 < len(self.tokens):
            next_token = self.tokens[self.token_idx + 1]
            return self.map_token_type(next_token)
        return 'eof'

    def map_token_type(self, token):
        # Map all TokenType values to their grammar symbols or string representations
        t = token.type
        # Data Types
        if t == TokenType.frag:
            return "frag"
        if t == TokenType.elo:
            return "elo"
        if t == TokenType.ign:
            return "ign"
        if t == TokenType.surebol:
            return "surebol"
        if t == TokenType.tag:
            return "tag"

        # Control Flow
        if t == TokenType.clutch:
            return "clutch"
        if t == TokenType.choke:
            return "choke"
        if t == TokenType.choke_clutch:
            return "choke_clutch"
        if t == TokenType.pick:
            return "pick"
        if t == TokenType.role:
            return "role"
        if t == TokenType.noob:
            return "noob"
        if t == TokenType.grind:
            return "grind"
        if t == TokenType.retry:
            return "retry"
        if t == TokenType.try_:
            return "try"
        if t == TokenType.afk:
            return "afk"
        if t == TokenType.hop:
            return "hop"

        # I/O
        if t == TokenType.comsat:
            return "comsat"
        if t == TokenType.shout:
            return "shout"

        # Functions
        if t == TokenType.build:
            return "build"
        if t == TokenType.lobby:
            return "lobby"
        if t == TokenType.dodge:
            return "dodge"
        if t == TokenType.ggwp:
            return "ggwp"

        # Modifiers
        if t == TokenType.stun:
            return "stun"

        # Boolean Literals
        if t == TokenType.buff:
            return "buff"
        if t == TokenType.nerf:
            return "nerf"

        # Array Operations
        if t == TokenType.stack:
            return "stack"
        if t == TokenType.craft:
            return "craft"
        if t == TokenType.drop:
            return "drop"
        if t == TokenType.count:
            return "count"
        if t == TokenType.split:
            return "split"

        # Arithmetic Operators
        if t == TokenType.plus:
            return "+"
        if t == TokenType.minus:
            return "-"
        if t == TokenType.mul:
            return "*"
        if t == TokenType.div:
            return "/"
        if t == TokenType.mod:
            return "%"

        # Relational Operators
        if t == TokenType.eq:
            return "=="
        if t == TokenType.neq:
            return "!="
        if t == TokenType.lt:
            return "<"
        if t == TokenType.gt:
            return ">"
        if t == TokenType.lte:
            return "<="
        if t == TokenType.gte:
            return ">="

        # Assignment Operators
        if t == TokenType.assign:
            return "="
        if t == TokenType.plus_assign:
            return "+="
        if t == TokenType.minus_assign:
            return "-="
        if t == TokenType.mul_assign:
            return "*="
        if t == TokenType.div_assign:
            return "/="
        if t == TokenType.mod_assign:
            return "%="

        # Logical Operators
        if t == TokenType.and_:
            return "&&"
        if t == TokenType.or_:
            return "||"
        if t == TokenType.not_:
            return "!"

        # Unary Operators
        if t == TokenType.increment:
            return "++"
        if t == TokenType.decrement:
            return "--"

        # Delimiters
        if t == TokenType.lparen:
            return "("
        if t == TokenType.rparen:
            return ")"
        if t == TokenType.lbrace:
            return "{"
        if t == TokenType.rbrace:
            return "}"
        if t == TokenType.lbracket:
            return "["
        if t == TokenType.rbracket:
            return "]"
        if t == TokenType.comma:
            return ","
        if t == TokenType.semicolon:
            return ";"
        if t == TokenType.colon:
            return ":"
        if t == TokenType.dot:
            return "."

        # New unified delimiter types
        if t == TokenType.terminator:
            return ";"
        if t == TokenType.separator:
            return token.value
        if t == TokenType.bracket:
            return "bracket"

        # Literals
        if t == TokenType.integer:
            return "integer"
        if t == TokenType.float:
            return "float"
        if t == TokenType.string:
            return "string"
        if t == TokenType.char:
            return "char"

        # Identifiers
        if t == TokenType.identifier:
            return "identifier"

        # Special
        if t == TokenType.eof:
            return "eof"
        if t == TokenType.error:
            return "error"
        if t == TokenType.comment:
            return "comment"
        if t == TokenType.whitespace:
            return "whitespace"
        if t == TokenType.newline:
            return "newline"

        # Fallback: string representation
        return str(t)

    def peek_n(self, n):
            target_idx = self.token_idx + n
            if target_idx < len(self.tokens):
                return self.map_token_type(self.tokens[target_idx])
            return 'eof'

    def syntax_analyzer(self):
        stack = ["<program>"]
        error = None
        
        while stack and not error:
            top = stack[-1]
            line = self.current_token.line if self.current_token else -1
            column = self.current_token.column if self.current_token else -1

            if is_non_terminal(top):
                # Ambiguity Check: Main Function vs Global Section
                if top == "<global_section>" and self.current_type == "frag":
                    if self.peek_n(1) == "lobby":
                        stack.pop()
                        continue

                # Ambiguity Check: Array vs Variable Declaration
                ambiguous_parents = ["<global_declaration>", "<local_declaration>", "<declaration_statement>"]
                data_types = ["frag", "elo", "ign", "surebol", "tag", "stun"]

                if top in ambiguous_parents and self.current_type in data_types:
                    symbol_after_id = self.peek_n(2)
                    stack.pop()

                    if symbol_after_id == "[":
                        stack.append(";")
                        stack.append("<array_declaration>")
                    else:
                        stack.append(";")
                        stack.append("<variable_declaration>")
                    continue

                # Standard Table Lookup
                if top in PREDICT_SET and self.current_type in PREDICT_SET[top]:
                    prod_info = PREDICT_SET[top][self.current_type]
                    nt, idx = prod_info
                    
                    stack.pop()
                    production = CFG[nt][idx]
                    
                    for sym in reversed(production):
                        if sym:
                            stack.append(sym)
                else:
                    expected = ', '.join(PREDICT_SET.get(top, {}).keys()) or 'epsilon'
                    error = InvalidSyntaxError(
                        line, column, 
                        f"Unexpected '{self.current_type}' while parsing {top}. Expected: {expected}"
                    )

            else:
                # Terminal Matching
                stack.pop()
                if top == self.current_type:
                    self.advance()
                else:
                    error = InvalidSyntaxError(
                        line, column, 
                        f"Expected '{top}', but found '{self.current_type}'"
                    )

        if not error and self.current_type != 'eof':
             return InvalidSyntaxError(
                self.current_token.line, self.current_token.column,
                "Extra input found after program end"
            )

        return error

def is_non_terminal(s):
    return s.startswith("<") and s.endswith(">")

def analyze_syntax(tokens):
    analyzer = SyntaxAnalyzer(tokens)
    error = analyzer.syntax_analyzer()
    if error:
        return False, error.as_string()
    return True, "Syntax analysis successful ✓ No errors."