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
# COMPLETE CONTEXT-FREE GRAMMAR (productions 1-197 from paper, refactored for LL(1))
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
        ["<non_const_decl>"],  # refactored: replaces 6 and 8
        ["<constant_declaration>"]  # 7
    ],
    "<non_const_decl>": [
        ["<data_type>", "identifier", "<decl_suffix>"]  # refactored for var/array
    ],
    "<decl_suffix>": [
        ["[", "<expression>", "]", "<array_init>", ";"],  # array
        ["<init_option>", "<init_tail>", ";"]  # var
    ],
    "<variable_declaration>": [  # not directly used, but for reference
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
        ["<non_const_decl>"],  # refactored
        ["<constant_declaration>"]  # 31
    ],
    "<return_type>": [
        ["frag"],  # 33
        ["elo"],  # 34
        ["ign"],  # 35
        ["surebol"],  # 36
        ["tag"],  # 37
        ["dodge"]  # 38
    ],
    "<parameters>": [
        ["<parameter_list>"],  # 39
        []  # 40
    ],
    "<parameter_list>": [
        ["<data_type>", "identifier", "<parameter_tail>"]  # 41
    ],
    "<parameter_tail>": [
        [",", "<data_type>", "identifier", "<parameter_tail>"],  # 42
        []  # 43
    ],
    "<statement_list>": [
        ["<statement>", "<statement_list>"],  # 44
        []  # 45
    ],
    "<statement>": [
        ["<declaration_statement>"],  # 46
        ["<executable_statement>"],  # 47
        ["<control_statement>"],  # 48
        ["<local_declaration>"]  # 49
    ],
    "<declaration_statement>": [
        ["<non_const_decl>"],  # refactored
        ["<constant_declaration>"]  # 51
    ],
    "<executable_statement>": [
        ["<assignment_statement>"],  # 53
        ["<input_statement>"],  # 54
        ["<output_statement>"],  # 55
        ["<function_call_stmt>"],  # 56
        ["<break_statement>"],  # 57
        ["<continue_statement>"]  # 58
    ],
    "<control_statement>": [
        ["<if_statement>"],  # 59
        ["<switch_statement>"],  # 60
        ["<for_loop>"],  # 61
        ["<while_loop>"],  # 62
        ["<do_while_loop>"]  # 63
    ],
    "<assignment_statement>": [
        ["<lvalue>", "<assignment_operator>", "<expression>", ";"]  # 64
    ],
    "<lvalue>": [
        ["identifier", "<array_access>"]  # 65
    ],
    "<array_access>": [
        ["[", "<expression>", "]", "<array_access>"],  # 66
        []  # 67
    ],
    "<input_statement>": [
        ["comsat", "<input_list>", ";"]  # 68
    ],
    "<input_list>": [
        ["<lvalue>", "<input_tail>"]  # 69
    ],
    "<input_tail>": [
        [",", "<lvalue>", "<input_tail>"],  # 70
        []  # 71
    ],
    "<output_statement>": [
        ["shout", "<output_list>", ";"]  # 72
    ],
    "<output_list>": [
        ["<output_item>", "<output_tail>"]  # 73
    ],
    "<output_tail>": [
        [",", "<output_item>", "<output_tail>"],  # 74
        []  # 75
    ],
    "<output_item>": [
        ["string"],  # 76, changed to "string"
        ["<expression>"]  # 77
    ],
    "<function_call_stmt>": [
        ["<function_name>", "(", "<argument_list>", ")", ";"]  # 78
    ],
    "<function_call_expr>": [
        ["<function_name>", "(", "<argument_list>", ")"]  # 79
    ],
    "<function_name>": [
        ["identifier"],  # 80
        ["stack"],  
        ["craft"],
        ["drop"],
        ["count"],
        ["split"]
    ],
    "<argument_list>": [
        ["<expression>", "<argument_tail>"],  # 81
        []  # 82
    ],
    "<argument_tail>": [
        [",", "<expression>", "<argument_tail>"],  # 83
        []  # 84
    ],
    "<break_statement>": [
        ["afk", ";"]  # 85
    ],
    "<continue_statement>": [
        ["hop", ";"]  # 86
    ],
    "<return_statement>": [
        ["ggwp", "<return_value>", ";"],  # 87
        []  # 88
    ],
    "<return_value>": [
        ["<expression>"],  # 89
        []  # 90
    ],
    "<if_statement>": [
        ["clutch", "(", "<condition>", ")", "{", "<statement_list>", "}", "<else_if_block>", "<else_block>"]  # 91
    ],
    "<else_if_block>": [
        ["<else_if>", "<else_if_block>"],  # 92
        []  # 93
    ],
    "<else_if>": [
        ["choke", "clutch", "(", "<condition>", ")", "{", "<statement_list>", "}"]  # 94
    ],
    "<else_block>": [
        ["choke", "{", "<statement_list>", "}"],  # 95
        []  # 96
    ],
    "<switch_statement>": [
        ["pick", "(", "<expression>", ")", "{", "<case_blocks>", "<default_block>", "}"]  # 97
    ],
    "<case_blocks>": [
        ["<case_block>", "<case_blocks>"],  # 98
        []  # 99
    ],
    "<case_block>": [
        ["role", "<case_value>", ":", "<case_body>", "afk", ";"]  # 100
    ],
    "<case_body>": [
        ["<statement_list>"]  # 101
    ],
    "<default_block>": [
        ["noob", ":", "<case_body>", "afk", ";"],  # 102
        []  # 103
    ],
    "<for_loop>": [
        ["grind", "(", "<for_init>", ";", "<condition>", ";", "<for_update>", ")", "{", "<statement_list>", "}"]  # 104
    ],
    "<for_init>": [
        ["<variable_declaration>"],  # 105, note: now uses <non_const_decl> without ; ?
        ["<assignment_statement_no_semi>"],  # 106
        []  # 107
    ],
    "<assignment_statement_no_semi>": [
        ["<lvalue>", "<assignment_operator>", "<expression>"]  # 108
    ],
    "<for_update>": [
        ["<assignment_expression>", "<update_tail>"],  # 109
        []  # 110
    ],
    "<update_tail>": [
        [",", "<assignment_expression>", "<update_tail>"],  # 111
        []  # 112
    ],
    "<while_loop>": [
        ["retry", "(", "<condition>", ")", "{", "<statement_list>", "}"]  # 113
    ],
    "<do_while_loop>": [
        ["try", "{", "<statement_list>", "}", "retry", "(", "<condition>", ")", ";"]  # 114
    ],
    "<expression>": [
        ["<logical_or_expression>"]  # 115
    ],
    "<logical_or_expression>": [
        ["<logical_and_expression>", "<logical_or_tail>"]  # 116
    ],
    "<logical_or_tail>": [
        ["||", "<logical_and_expression>", "<logical_or_tail>"],  # 117
        []  # 118
    ],
    "<logical_and_expression>": [
        ["<equality_expression>", "<logical_and_tail>"]  # 119
    ],
    "<logical_and_tail>": [
        ["&&", "<equality_expression>", "<logical_and_tail>"],  # 120
        []  # 121
    ],
    "<equality_expression>": [
        ["<relational_expression>", "<equality_tail>"]  # 122
    ],
    "<equality_tail>": [
        ["<equality_op>", "<relational_expression>", "<equality_tail>"],  # 123
        []  # 124
    ],
    "<equality_op>": [
        ["=="],  # 125
        ["!="]  # 126
    ],
    "<relational_expression>": [
        ["<additive_expression>", "<relational_tail>"]  # 127
    ],
    "<relational_tail>": [
        ["<relational_op>", "<additive_expression>", "<relational_tail>"],  # 128
        []  # 129
    ],
    "<relational_op>": [
        ["<"],  # 130
        [">"],  # 131
        ["<="],  # 132
        [">="]  # 133
    ],
    "<additive_expression>": [
        ["<multiplicative_expression>", "<additive_tail>"]  # 134
    ],
    "<additive_tail>": [
        ["<additive_op>", "<multiplicative_expression>", "<additive_tail>"],  # 135
        []  # 136
    ],
    "<additive_op>": [
        ["+"],  # 137
        ["-"]  # 138
    ],
    "<multiplicative_expression>": [
        ["<unary_expression>", "<multiplicative_tail>"]  # 139
    ],
    "<multiplicative_tail>": [
        ["<multiplicative_op>", "<unary_expression>", "<multiplicative_tail>"],  # 140
        []  # 141
    ],
    "<multiplicative_op>": [
        ["*"],  # 142
        ["/"],  # 143
        ["%"]  # 144
    ],
    "<unary_expression>": [
        ["<unary_op>", "<unary_expression>"],  # 145
        ["<postfix_expression>"]  # 146
    ],
    "<unary_op>": [
        ["+"],  # 147
        ["-"],  # 148
        ["!"],  # 149
        ["++"],  # 150
        ["--"]  # 151
    ],
    "<postfix_expression>": [
        ["<primary_expression>", "<postfix_tail>"]  # 152
    ],
    "<postfix_tail>": [
        ["<postfix_op>", "<postfix_tail>"],  # refactored to allow multiple post ops
        ["<array_access>"],  # 154
        ["<function_call_suffix>"],  # 155
        []  # 156
    ],
    "<postfix_op>": [
        ["++"],  # 157
        ["--"]  # 158
    ],
    "<function_call_suffix>": [
        ["(", "<argument_list>", ")"]  # 159
    ],
    "<primary_expression>": [
        ["<literal>"],  # 160
        ["identifier"],  # 161
        ["(", "<expression>", ")"],  # 162
        ["<function_call_expr>"]  # 163
    ],
    "<data_type>": [
        ["frag"],  # 165
        ["elo"],  # 166
        ["ign"],  # 167
        ["surebol"],  # 168
        ["tag"]  # 169
    ],
    "<assignment_operator>": [
        ["="],  # 170
        ["+="],  # 171
        ["-="],  # 172
        ["*="],  # 173
        ["/="],  # 174
        ["%="]  # 175
    ],
    "<assignment_expression>": [
        ["<lvalue>", "<assignment_operator>", "<expression>"]  # 176
    ],
    "<condition>": [
        ["<expression>"]  # 177
    ],
    "<literal>": [
        ["integer"],  # 178, changed
        ["float"],  # 179
        ["string"],  # 180
        ["char"],  # 181
        ["<boolean_literal>"]  # 182
    ],
    "<boolean_literal>": [
        ["buff"],  # 195
        ["nerf"]  # 196
    ],
    # Refactored constant_value to avoid left-recursion
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
    "<arithmetic_operator>": [  # not used directly
        ["+"],
        ["-"],
        ["*"],
        ["/"],
        ["%"]
    ],
    "<case_value>": [
        ["integer"],  # 187
        ["char"],  # 188
        ["string"],  # 189
        ["<boolean_literal>"]  # 190
    ]
}

# ────────────────────────────────────────────────
# COMPLETE PREDICT SET (extended and completed for all multi-prod non-terminals)
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
        "frag": ["<function_section>", 1]  # main
    },
    "<global_declaration>": {
        "frag": ["<global_declaration>", 0],
        "elo": ["<global_declaration>", 0],
        "ign": ["<global_declaration>", 0],
        "surebol": ["<global_declaration>", 0],
        "tag": ["<global_declaration>", 0],
        "stun": ["<global_declaration>", 1]
    },
    "<non_const_decl>": {
        "frag": ["<non_const_decl>", 0],
        "elo": ["<non_const_decl>", 0],
        "ign": ["<non_const_decl>", 0],
        "surebol": ["<non_const_decl>", 0],
        "tag": ["<non_const_decl>", 0]
    },
    "<decl_suffix>": {
        "[": ["<decl_suffix>", 0],
        "=": ["<decl_suffix>", 1],
        "(": ["<decl_suffix>", 1],
        "{": ["<decl_suffix>", 1],
        ",": ["<decl_suffix>", 1],
        ";": ["<decl_suffix>", 1]
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
        "tag": ["<return_type>", 4],
        "dodge": ["<return_type>", 5]
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
        "ggwp": ["<statement_list>", 0],
        "}": ["<statement_list>", 1],
        "role": ["<statement_list>", 1],  # for case
        "noob": ["<statement_list>", 1]
    },
    "<statement>": {
        "frag": ["<statement>", 3],  # local_decl
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
        "stack": ["<executable_statement>", 2],  # function_call
        "craft": ["<executable_statement>", 2],
        "drop": ["<executable_statement>", 2],
        "count": ["<executable_statement>", 2],
        "split": ["<executable_statement>", 2],
        "comsat": ["<executable_statement>", 1],
        "shout": ["<executable_statement>", 2],
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
        "choke": ["<else_if_block>", 0],
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
        "choke": ["<else_if>", 0]
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
        "role": ["<case_body>", 0],  # epsilon for next case
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
        "<": ["<relational_op>", 0],
        ">": ["<relational_op>", 1],
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
        "+": ["<unary_op>", 0],
        "-": ["<unary_op>", 1],
        "!": ["<unary_op>", 2],
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
    "<data_type>": {
        "frag": ["<data_type>", 0],
        "elo": ["<data_type>", 1],
        "ign": ["<data_type>", 2],
        "surebol": ["<data_type>", 3],
        "tag": ["<data_type>", 4]
    },
    "<assignment_operator>": {
        "=": ["<assignment_operator>", 0],
        "+=": ["<assignment_operator>", 1],
        "-=": ["<assignment_operator>", 2],
        "*=": ["<assignment_operator>", 3],
        "/=": ["<assignment_operator>", 4],
        "%=": ["<assignment_operator>", 5]
    },
    "<assignment_expression>": {
        "identifier": ["<assignment_expression>", 0]
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
        ",": ["<const_add_tail>", 2],
        "}": ["<const_add_tail>", 2],
        ";": ["<const_add_tail>", 2],
        ")": ["<const_add_tail>", 2]
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
        ",": ["<const_mul_tail>", 3],
        "}": ["<const_mul_tail>", 3],
        ";": ["<const_mul_tail>", 3],
        ")": ["<const_mul_tail>", 3]
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
    "<case_value>": {
        "integer": ["<case_value>", 0],
        "char": ["<case_value>", 1],
        "string": ["<case_value>", 2],
        "buff": ["<case_value>", 3],
        "nerf": ["<case_value>", 3]
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

    def syntax_analyzer(self):
        stack = ["<program>"]
        error = None
        while stack and not error:
            top = stack[-1]
            line = self.current_token.line
            column = self.current_token.column

            if is_non_terminal(top):
                if top in PREDICT_SET and self.current_type in PREDICT_SET[top]:
                    prod_info = PREDICT_SET[top][self.current_type]
                    nt = prod_info[0]
                    idx = prod_info[1]
                    stack.pop()
                    production = CFG[nt][idx]
                    for sym in reversed(production):
                        if sym:  # skip empty for epsilon
                            stack.append(sym)
                else:
                    expected = ', '.join(PREDICT_SET.get(top, {}).keys()) or 'epsilon possible'
                    error = InvalidSyntaxError(
                        line, column,
                        f"Unexpected '{self.current_type}'. Expected: {expected}"
                    )
            else:
                stack.pop()
                if top == self.current_type:
                    self.advance()
                else:
                    error = InvalidSyntaxError(
                        line, column,
                        f"Expected '{top}', found '{self.current_type}'"
                    )

        if error:
            return error
        if self.current_type != 'eof':
            return InvalidSyntaxError(
                self.current_token.line, self.current_token.column,
                "Extra input after program end"
            )
        return None

def is_non_terminal(s):
    return s.startswith("<") and s.endswith(">")

def analyze_syntax(tokens):
    analyzer = SyntaxAnalyzer(tokens)
    error = analyzer.syntax_analyzer()
    if error:
        return False, error.as_string()
    return True, "Syntax analysis successful ✓ No errors."