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
        ["=", "<expression>"],      # 12
        ["(", "<expression>", ")"], # 13
        ["{", "<expression>", "}"], # 14
        []                          # 15
    ],
    "<init_tail>": [
        [",", "<identifier_init>", "<init_tail>"],  # 16
        []                                          # 17
    ],
    "<constant_declaration>": [
        ["stun", "<data_type>", "identifier", "=", "<constant_value>", ";"]  # 18
    ],
    "<array_declaration>": [
        ["<data_type>", "identifier", "<dimension_list>", "<array_init>"]  # 19
    ],
    "<dimension_list>": [
        ["[", "<array_size>", "]", "<dimension_tail>"]  # 20
    ],
    "<dimension_tail>": [
        ["[", "<array_size>", "]", "<dimension_tail>"],  # 21
        []                                               # 22
    ],
    "<array_size>": [
        ["<positive_integer>"],  # 23
        ["identifier"],          # 24
        []                       # 25
    ],
    "<array_init>": [
        ["=", "{", "<value_list>", "}"],  # 26
        []                                # 27
    ],
    "<value_list>": [
        ["<array_element>", "<value_tail>"]  # 28
    ],
    "<value_tail>": [
        [",", "<array_element>", "<value_tail>"],  # 29
        []                                         # 30
    ],
    "<array_element>": [
        ["<constant_value>"],       # 31
        ["{", "<value_list>", "}"]  # 32
    ],
    "<function_definition>": [
        ["build", "<return_type>", "identifier", "(", "<parameters>", ")", "{", "<standard_function_body>", "}"]  # 33
    ],
    "<main_function>": [
        ["frag", "lobby", "(", ")", "{", "<lobby_function_body>", "}"]  # 34
    ],
    "<standard_function_body>": [
        ["<local_declaration_list>", "<statement_list>"] # 35
    ],
    "<lobby_function_body>": [
        ["<local_declaration_list>", "<statement_list>", "<lobby_return_statement>"]  # 36
    ],
    "<local_declaration_list>": [
        ["<local_declaration>", "<local_declaration_list>"],  # 37
        []                                                    # 38
    ],
    "<local_declaration>": [
        ["<variable_declaration>", ";"],  # 39
        ["<constant_declaration>"],       # 40
        ["<array_declaration>", ";"]      # 41
    ],
    "<return_type>": [
        ["frag"],    # 42
        ["elo"],     # 43
        ["ign"],     # 44
        ["surebol"], # 45
        ["dodge"],   # 46
        ["tag"]      # 47
    ],
    "<parameters>": [
        ["<parameter_list>"],  # 48
        []                     # 49
    ],
    "<parameter_list>": [
        ["<data_type>", "identifier", "<param_arr_opt>", "<parameter_tail>"]  # 50
    ],
    "<parameter_tail>": [
        [",", "<data_type>", "identifier", "<param_arr_opt>", "<parameter_tail>"],  # 51
        []                                                                          # 52
    ],
    "<param_arr_opt>": [
        ["<dimension_list>"],  # 53
        []                     # 54
    ],
    "<statement_list>": [
        ["<statement>", "<statement_list>"],  # 55
        []                                    # 56
    ],
    "<statement>": [
        ["<declaration_statement>"],  # 57
        ["<executable_statement>"],   # 58
        ["<control_statement>"],      # 59
        ["<local_declaration>"]       # 60
    ],
    "<declaration_statement>": [
        ["<variable_declaration>", ";"],  # 61
        ["<constant_declaration>"],       # 62
        ["<array_declaration>", ";"]      # 63
    ],
    "<executable_statement>": [
        ["<assignment_statement>"],     # 64
        ["<input_statement>"],          # 65
        ["<output_statement>"],         # 66
        ["<function_call_stmt>"],       # 67
        ["<break_statement>"],          # 68
        ["<continue_statement>"],       # 69
        ["ggwp", "<return_value>", ";"] # 70
    ],
    "<control_statement>": [
        ["<if_statement>"],    # 71
        ["<switch_statement>"],# 72
        ["<for_loop>"],        # 73
        ["<while_loop>"],      # 74
        ["<do_while_loop>"]    # 75
    ],
    "<assignment_statement>": [
        ["<lvalue>", "<assign_tail>", ";"]  # 76
    ],
    "<lvalue>": [
        ["identifier", "<array_access>"]  # 77
    ],
    "<array_access>": [
        ["[", "<expression>", "]", "<array_access>"],  # 78
        []                                             # 79
    ],
    "<input_statement>": [
        ["comsat", "<input_list>", ";"]  # 80
    ],
    "<input_list>": [
        ["<lvalue>", "<input_tail>"]  # 81
    ],
    "<input_tail>": [
        [",", "<lvalue>", "<input_tail>"],  # 82
        []                                  # 83
    ],
    "<output_statement>": [
        ["shout", "<output_list>", ";"]  # 84
    ],
    "<output_list>": [
        ["<output_item>", "<output_tail>"]  # 85
    ],
    "<output_tail>": [
        [",", "<output_item>", "<output_tail>"],  # 86
        []                                        # 87
    ],
    "<output_item>": [
        ["<string_literal>"],  # 88
        ["<expression>"]       # 89
    ],
    "<function_call_stmt>": [
        ["<function_name>", "(", "<argument_list>", ")", ";"]  # 90
    ],
    "<function_call_expr>": [
        ["<function_name>", "(", "<argument_list>", ")"]  # 91
    ],
    "<function_name>": [
        ["identifier"],  # 92
        ["stack"],       # 93
        ["craft"],       # 94
        ["drop"],        # 95
        ["count"],       # 96
        ["split"]        # 97
    ],
    "<argument_list>": [
        ["<expression>", "<argument_tail>"],  # 98
        []                                    # 99
    ],
    "<argument_tail>": [
        [",", "<expression>", "<argument_tail>"],  # 100
        []                                         # 101
    ],
    "<break_statement>": [
        ["afk", ";"]  # 102
    ],
    "<continue_statement>": [
        ["hop", ";"]  # 103
    ],
    "<standard_return_statement>": [
        ["ggwp", "<return_value>", ";"]  # 104
    ],
    "<lobby_return_statement>": [
        ["ggwp", "<return_value>", ";"],  # 105
        []                                # 106
    ],
    "<return_value>": [
        ["<expression>"],  # 107
        []                 # 108
    ],
    "<if_statement>": [
        ["clutch", "(", "<condition>", ")", "{", "<statement_list>", "}", "<else_if_block>", "<else_block>"]  # 109
    ],
    "<else_if_block>": [
        ["<else_if>", "<else_if_block>"],  # 110
        []                                 # 111
    ],
    "<else_if>": [
        ["choke_clutch", "(", "<condition>", ")", "{", "<statement_list>", "}"]  # 112
    ],
    "<else_block>": [
        ["choke", "{", "<statement_list>", "}"],  # 113
        []                                        # 114
    ],
    "<switch_statement>": [
        ["pick", "(", "<expression>", ")", "{", "<case_blocks>", "<default_block>", "}"]  # 115
    ],
    "<case_blocks>": [
        ["<case_block>", "<case_blocks>"],  # 116
        []                                  # 117
    ],
    "<case_block>": [
        ["role", "<case_value>", ":", "<case_body>"]  # 118
    ],
    "<case_body>": [
        ["<statement_list>"]  # 119
    ],
    "<default_block>": [
        ["noob", ":", "<case_body>"],  # 120
        []                             # 121
    ],
    "<for_loop>": [
        ["grind", "(", "<for_init>", ";", "<condition>", ";", "<for_update>", ")", "{", "<statement_list>", "}"]  # 122
    ],
    "<for_init>": [
        ["<variable_declaration>"],           # 123
        ["<assignment_statement_no_semi>"],   # 124
        []                                    # 125
    ],
    "<assignment_statement_no_semi>": [
        ["<lvalue>", "<assignment_operator>", "<expression>"]  # 126
    ],
    "<for_update>": [
        ["<assignment_expression>", "<update_tail>"],  # 127
        []                                             # 128
    ],
    "<update_tail>": [
        [",", "<assignment_expression>", "<update_tail>"],  # 129
        []                                                  # 130
    ],
    "<while_loop>": [
        ["retry", "(", "<condition>", ")", "{", "<statement_list>", "}"]  # 131
    ],
    "<do_while_loop>": [
        ["try", "{", "<statement_list>", "}", "retry", "(", "<condition>", ")", ";"]  # 132
    ],
    "<expression>": [
        ["<logical_or_expression>"]  # 133
    ],
    "<logical_or_expression>": [
        ["<logical_and_expression>", "<logical_or_tail>"]  # 134
    ],
    "<logical_or_tail>": [
        ["||", "<logical_and_expression>", "<logical_or_tail>"],  # 135
        []                                                        # 136
    ],
    "<logical_and_expression>": [
        ["<equality_expression>", "<logical_and_tail>"]  # 137
    ],
    "<logical_and_tail>": [
        ["&&", "<equality_expression>", "<logical_and_tail>"],  # 138
        []                                                      # 139
    ],
    "<equality_expression>": [
        ["<relational_expression>", "<equality_tail>"]  # 140
    ],
    "<equality_tail>": [
        ["<equality_op>", "<relational_expression>", "<equality_tail>"],  # 141
        []                                                                # 142
    ],
    "<equality_op>": [
        ["=="],  # 143
        ["!="]   # 144
    ],
    "<relational_expression>": [
        ["<additive_expression>", "<relational_tail>"]  # 145
    ],
    "<relational_tail>": [
        ["<relational_op>", "<additive_expression>", "<relational_tail>"],  # 146
        []                                                                  # 147
    ],
    "<relational_op>": [
        ["<"],   # 148
        [">"],   # 149
        ["<="],  # 150
        [">="]   # 151
    ],
    "<additive_expression>": [
        ["<multiplicative_expression>", "<additive_tail>"]  # 152
    ],
    "<additive_tail>": [
        ["<additive_op>", "<multiplicative_expression>", "<additive_tail>"],  # 153
        []                                                                    # 154
    ],
    "<additive_op>": [
        ["+"],  # 155
        ["-"]   # 156
    ],
    "<multiplicative_expression>": [
        ["<unary_expression>", "<multiplicative_tail>"]  # 157
    ],
    "<multiplicative_tail>": [
        ["<multiplicative_op>", "<unary_expression>", "<multiplicative_tail>"],  # 158
        []                                                                       # 159
    ],
    "<multiplicative_op>": [
        ["*"],  # 160
        ["/"],  # 161
        ["%"]   # 162
    ],
    "<unary_expression>": [
        ["<unary_op>", "<unary_expression>"],  # 163
        ["<postfix_expression>"]               # 164
    ],
    "<unary_op>": [
        ["+"],   # 165
        ["-"],   # 166
        ["!"],   # 167
        ["++"],  # 168
        ["--"]   # 169
    ],
    "<postfix_expression>": [
        ["<primary_expression>", "<postfix_tail>"]  # 170
    ],
    "<postfix_tail>": [
        ["<postfix_op>"],                                        # 171
        ["<array_access>"],                                      # 172
        ["<function_call_suffix>"],                              # 173
        [".", "<function_name>", "(", "<argument_list>", ")"],   # 174
        []                                                       # 175
    ],
    "<postfix_op>": [
        ["++"],  # 176
        ["--"]   # 177
    ],
    "<function_call_suffix>": [
        ["(", "<argument_list>", ")"]  # 178
    ],
    "<primary_expression>": [
        ["<literal>"],              # 179
        ["identifier"],             # 180
        ["(", "<expression>", ")"], # 181
        ["<function_call_expr>"]    # 182
    ],
    "<data_type>": [
        ["frag"],    # 183
        ["elo"],     # 184
        ["ign"],     # 185
        ["surebol"], # 186
        ["dodge"],   # 187
        ["tag"]      # 188
    ],
    "<assignment_operator>": [
        ["="],   # 189
        ["+="],  # 190
        ["-="],  # 191
        ["*="],  # 192
        ["/="],  # 193
        ["%="]   # 194
    ],
    "<assignment_expression>": [
        ["<lvalue>", "<assign_tail>"]  # 195
    ],
    "<assign_tail>": [
        ["<assignment_operator>", "<expression>"],               # 196
        ["++"],                                                  # 197
        ["--"],                                                  # 198
        [".", "<function_name>", "(", "<argument_list>", ")"]    # 199
    ],
    "<condition>": [
        ["<expression>"]  # 200
    ],
    "<literal>": [
        ["<integer_literal>"],  # 201
        ["<float_literal>"],    # 202
        ["<string_literal>"],   # 203
        ["<char_literal>"],     # 204
        ["<boolean_literal>"]   # 205
    ],
    "<boolean_literal>": [
        ["buff"],  # 206
        ["nerf"]   # 207
    ],
    "<constant_value>": [
        ["<const_add_expression>"]  # 208
    ],
    "<const_add_expression>": [
        ["<const_mul_expression>", "<const_add_tail>"]  # 209
    ],
    "<const_add_tail>": [
        ["+", "<const_mul_expression>", "<const_add_tail>"],  # 210
        ["-", "<const_mul_expression>", "<const_add_tail>"],  # 211
        []                                                    # 212
    ],
    "<const_mul_expression>": [
        ["<const_primary>", "<const_mul_tail>"]  # 213
    ],
    "<const_mul_tail>": [
        ["*", "<const_primary>", "<const_mul_tail>"],  # 214
        ["/", "<const_primary>", "<const_mul_tail>"],  # 215
        ["%", "<const_primary>", "<const_mul_tail>"],  # 216
        []                                             # 217
    ],
    "<const_primary>": [
        ["<literal>"],                  # 218
        ["(", "<constant_value>", ")"]  # 219
    ],
    "<case_value>": [
        ["<integer_literal>"],  # 220
        ["<char_literal>"],     # 221
        ["<string_literal>"],   # 222
        ["<boolean_literal>"]   # 223
    ],
    "<integer_literal>": [
        ["integer"]  # 224
    ],
    "<float_literal>": [
        ["float"]  # 225
    ],
    "<string_literal>": [
        ["string"]  # 226
    ],
    "<char_literal>": [
        ["char"]  # 227
    ],
    "<positive_integer>": [
        ["integer"]  # 228
    ]
}

# ────────────────────────────────────────────────
# PREDICT SET
# ────────────────────────────────────────────────
PREDICT_SET = {
    "<program>": {
        "build": ["<program>", 0], "dodge": ["<program>", 0], "elo": ["<program>", 0], "frag": ["<program>", 0], "ign": ["<program>", 0], "stun": ["<program>", 0], "surebol": ["<program>", 0], "tag": ["<program>", 0]
    },
    "<global_section>": {
        "dodge": ["<global_section>", 0], "elo": ["<global_section>", 0], "ign": ["<global_section>", 0], "stun": ["<global_section>", 0], "surebol": ["<global_section>", 0], "tag": ["<global_section>", 0],
        "build": ["<global_section>", 1], "frag": ["<global_section>", 1]
    },
    "<function_section>": {
        "build": ["<function_section>", 0],
        "frag": ["<function_section>", 1]
    },
    "<global_declaration>": {
        "dodge": ["<global_declaration>", 0], "elo": ["<global_declaration>", 0], "frag": ["<global_declaration>", 0], "ign": ["<global_declaration>", 0], "surebol": ["<global_declaration>", 0], "tag": ["<global_declaration>", 0],
        "stun": ["<global_declaration>", 1]
    },
    "<variable_declaration>": {
        "dodge": ["<variable_declaration>", 0], "elo": ["<variable_declaration>", 0], "frag": ["<variable_declaration>", 0], "ign": ["<variable_declaration>", 0], "surebol": ["<variable_declaration>", 0], "tag": ["<variable_declaration>", 0]
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
        ",": ["<init_option>", 3], ";": ["<init_option>", 3]
    },
    "<init_tail>": {
        ",": ["<init_tail>", 0],
        ";": ["<init_tail>", 1]
    },
    "<constant_declaration>": {
        "stun": ["<constant_declaration>", 0]
    },
    "<array_declaration>": {
        "dodge": ["<array_declaration>", 0], "elo": ["<array_declaration>", 0], "frag": ["<array_declaration>", 0], "ign": ["<array_declaration>", 0], "surebol": ["<array_declaration>", 0], "tag": ["<array_declaration>", 0]
    },
    "<dimension_list>": {
        "[": ["<dimension_list>", 0]
    },
    "<dimension_tail>": {
        "[": ["<dimension_tail>", 0],
        ")": ["<dimension_tail>", 1], ",": ["<dimension_tail>", 1], ";": ["<dimension_tail>", 1], "=": ["<dimension_tail>", 1]
    },
    "<array_size>": {
        "integer": ["<array_size>", 0],
        "identifier": ["<array_size>", 1],
        "]": ["<array_size>", 2]
    },
    "<array_init>": {
        "=": ["<array_init>", 0],
        ";": ["<array_init>", 1]
    },
    "<value_list>": {
        "(": ["<value_list>", 0], "buff": ["<value_list>", 0], "char": ["<value_list>", 0], "float": ["<value_list>", 0], "integer": ["<value_list>", 0], "nerf": ["<value_list>", 0], "string": ["<value_list>", 0], "{": ["<value_list>", 0]
    },
    "<value_tail>": {
        ",": ["<value_tail>", 0],
        "}": ["<value_tail>", 1]
    },
    "<array_element>": {
        "(": ["<array_element>", 0], "buff": ["<array_element>", 0], "char": ["<array_element>", 0], "float": ["<array_element>", 0], "integer": ["<array_element>", 0], "nerf": ["<array_element>", 0], "string": ["<array_element>", 0],
        "{": ["<array_element>", 1]
    },
    "<function_definition>": {
        "build": ["<function_definition>", 0]
    },
    "<main_function>": {
        "frag": ["<main_function>", 0]
    },
    "<standard_function_body>": {
        "afk": ["<standard_function_body>", 0], "clutch": ["<standard_function_body>", 0], "comsat": ["<standard_function_body>", 0], "count": ["<standard_function_body>", 0], "craft": ["<standard_function_body>", 0], "dodge": ["<standard_function_body>", 0], "drop": ["<standard_function_body>", 0], "elo": ["<standard_function_body>", 0], "frag": ["<standard_function_body>", 0], "ggwp": ["<standard_function_body>", 0], "grind": ["<standard_function_body>", 0], "hop": ["<standard_function_body>", 0], "identifier": ["<standard_function_body>", 0], "ign": ["<standard_function_body>", 0], "pick": ["<standard_function_body>", 0], "retry": ["<standard_function_body>", 0], "shout": ["<standard_function_body>", 0], "split": ["<standard_function_body>", 0], "stack": ["<standard_function_body>", 0], "stun": ["<standard_function_body>", 0], "surebol": ["<standard_function_body>", 0], "tag": ["<standard_function_body>", 0], "try": ["<standard_function_body>", 0]
    },
    "<lobby_function_body>": {
        "afk": ["<lobby_function_body>", 0], "clutch": ["<lobby_function_body>", 0], "comsat": ["<lobby_function_body>", 0], "count": ["<lobby_function_body>", 0], "craft": ["<lobby_function_body>", 0], "dodge": ["<lobby_function_body>", 0], "drop": ["<lobby_function_body>", 0], "elo": ["<lobby_function_body>", 0], "frag": ["<lobby_function_body>", 0], "ggwp": ["<lobby_function_body>", 0], "grind": ["<lobby_function_body>", 0], "hop": ["<lobby_function_body>", 0], "identifier": ["<lobby_function_body>", 0], "ign": ["<lobby_function_body>", 0], "pick": ["<lobby_function_body>", 0], "retry": ["<lobby_function_body>", 0], "shout": ["<lobby_function_body>", 0], "split": ["<lobby_function_body>", 0], "stack": ["<lobby_function_body>", 0], "stun": ["<lobby_function_body>", 0], "surebol": ["<lobby_function_body>", 0], "tag": ["<lobby_function_body>", 0], "try": ["<lobby_function_body>", 0],
        "}": ["<lobby_function_body>", 1]
    },
    "<local_declaration_list>": {
        "dodge": ["<local_declaration_list>", 0], "elo": ["<local_declaration_list>", 0], "frag": ["<local_declaration_list>", 0], "ign": ["<local_declaration_list>", 0], "stun": ["<local_declaration_list>", 0], "surebol": ["<local_declaration_list>", 0], "tag": ["<local_declaration_list>", 0],
        "afk": ["<local_declaration_list>", 1], "clutch": ["<local_declaration_list>", 1], "comsat": ["<local_declaration_list>", 1], "count": ["<local_declaration_list>", 1], "craft": ["<local_declaration_list>", 1], "drop": ["<local_declaration_list>", 1], "ggwp": ["<local_declaration_list>", 1], "grind": ["<local_declaration_list>", 1], "hop": ["<local_declaration_list>", 1], "identifier": ["<local_declaration_list>", 1], "pick": ["<local_declaration_list>", 1], "retry": ["<local_declaration_list>", 1], "shout": ["<local_declaration_list>", 1], "split": ["<local_declaration_list>", 1], "stack": ["<local_declaration_list>", 1], "try": ["<local_declaration_list>", 1], "}": ["<local_declaration_list>", 1]
    },
    "<local_declaration>": {
        "dodge": ["<local_declaration>", 0], "elo": ["<local_declaration>", 0], "frag": ["<local_declaration>", 0], "ign": ["<local_declaration>", 0], "surebol": ["<local_declaration>", 0], "tag": ["<local_declaration>", 0],
        "stun": ["<local_declaration>", 1]
    },
    "<return_type>": {
        "frag": ["<return_type>", 0],
        "elo": ["<return_type>", 1],
        "ign": ["<return_type>", 2],
        "surebol": ["<return_type>", 3],
        "dodge": ["<return_type>", 4],
        "tag": ["<return_type>", 5]
    },
    "<parameters>": {
        "dodge": ["<parameters>", 0], "elo": ["<parameters>", 0], "frag": ["<parameters>", 0], "ign": ["<parameters>", 0], "surebol": ["<parameters>", 0], "tag": ["<parameters>", 0],
        ")": ["<parameters>", 1]
    },
    "<parameter_list>": {
        "dodge": ["<parameter_list>", 0], "elo": ["<parameter_list>", 0], "frag": ["<parameter_list>", 0], "ign": ["<parameter_list>", 0], "surebol": ["<parameter_list>", 0], "tag": ["<parameter_list>", 0]
    },
    "<parameter_tail>": {
        ",": ["<parameter_tail>", 0],
        ")": ["<parameter_tail>", 1]
    },
    "<param_arr_opt>": {
        "[": ["<param_arr_opt>", 0],
        ")": ["<param_arr_opt>", 1], ",": ["<param_arr_opt>", 1]
    },
    "<statement_list>": {
        "afk": ["<statement_list>", 0], "clutch": ["<statement_list>", 0], "comsat": ["<statement_list>", 0], "count": ["<statement_list>", 0], "craft": ["<statement_list>", 0], "dodge": ["<statement_list>", 0], "drop": ["<statement_list>", 0], "elo": ["<statement_list>", 0], "frag": ["<statement_list>", 0], "ggwp": ["<statement_list>", 0], "grind": ["<statement_list>", 0], "hop": ["<statement_list>", 0], "identifier": ["<statement_list>", 0], "ign": ["<statement_list>", 0], "pick": ["<statement_list>", 0], "retry": ["<statement_list>", 0], "shout": ["<statement_list>", 0], "split": ["<statement_list>", 0], "stack": ["<statement_list>", 0], "stun": ["<statement_list>", 0], "surebol": ["<statement_list>", 0], "tag": ["<statement_list>", 0], "try": ["<statement_list>", 0],
        "noob": ["<statement_list>", 1], "role": ["<statement_list>", 1], "}": ["<statement_list>", 1]
    },
    "<statement>": {
        "dodge": ["<statement>", 0], "elo": ["<statement>", 0], "frag": ["<statement>", 0], "ign": ["<statement>", 0], "stun": ["<statement>", 0], "surebol": ["<statement>", 0], "tag": ["<statement>", 0],
        "afk": ["<statement>", 1], "comsat": ["<statement>", 1], "count": ["<statement>", 1], "craft": ["<statement>", 1], "drop": ["<statement>", 1], "ggwp": ["<statement>", 1], "hop": ["<statement>", 1], "identifier": ["<statement>", 1], "shout": ["<statement>", 1], "split": ["<statement>", 1], "stack": ["<statement>", 1],
        "clutch": ["<statement>", 2], "grind": ["<statement>", 2], "pick": ["<statement>", 2], "retry": ["<statement>", 2], "try": ["<statement>", 2]
    },
    "<declaration_statement>": {
        "dodge": ["<declaration_statement>", 0], "elo": ["<declaration_statement>", 0], "frag": ["<declaration_statement>", 0], "ign": ["<declaration_statement>", 0], "surebol": ["<declaration_statement>", 0], "tag": ["<declaration_statement>", 0],
        "stun": ["<declaration_statement>", 1]
    },
    "<executable_statement>": {
        "identifier": ["<executable_statement>", 0],
        "comsat": ["<executable_statement>", 1],
        "shout": ["<executable_statement>", 2],
        "count": ["<executable_statement>", 3], "craft": ["<executable_statement>", 3], "drop": ["<executable_statement>", 3], "split": ["<executable_statement>", 3], "stack": ["<executable_statement>", 3],
        "afk": ["<executable_statement>", 4],
        "hop": ["<executable_statement>", 5],
        "ggwp": ["<executable_statement>", 6]
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
        "!=": ["<array_access>", 1], "%": ["<array_access>", 1], "%=": ["<array_access>", 1], "&&": ["<array_access>", 1], ")": ["<array_access>", 1], "*": ["<array_access>", 1], "*=": ["<array_access>", 1], "+": ["<array_access>", 1], "++": ["<array_access>", 1], "+=": ["<array_access>", 1], ",": ["<array_access>", 1], "-": ["<array_access>", 1], "--": ["<array_access>", 1], "-=": ["<array_access>", 1], ".": ["<array_access>", 1], "/": ["<array_access>", 1], "/=": ["<array_access>", 1], ";": ["<array_access>", 1], "<": ["<array_access>", 1], "<=": ["<array_access>", 1], "=": ["<array_access>", 1], "==": ["<array_access>", 1], ">": ["<array_access>", 1], ">=": ["<array_access>", 1], "]": ["<array_access>", 1], "||": ["<array_access>", 1], "}": ["<array_access>", 1]
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
        "!": ["<output_list>", 0], "(": ["<output_list>", 0], "+": ["<output_list>", 0], "++": ["<output_list>", 0], "-": ["<output_list>", 0], "--": ["<output_list>", 0], "buff": ["<output_list>", 0], "char": ["<output_list>", 0], "count": ["<output_list>", 0], "craft": ["<output_list>", 0], "drop": ["<output_list>", 0], "float": ["<output_list>", 0], "identifier": ["<output_list>", 0], "integer": ["<output_list>", 0], "nerf": ["<output_list>", 0], "split": ["<output_list>", 0], "stack": ["<output_list>", 0], "string": ["<output_list>", 0]
    },
    "<output_tail>": {
        ",": ["<output_tail>", 0],
        ";": ["<output_tail>", 1]
    },
    "<output_item>": {
        "string": ["<output_item>", 0],
        "!": ["<output_item>", 1], "(": ["<output_item>", 1], "+": ["<output_item>", 1], "++": ["<output_item>", 1], "-": ["<output_item>", 1], "--": ["<output_item>", 1], "buff": ["<output_item>", 1], "char": ["<output_item>", 1], "count": ["<output_item>", 1], "craft": ["<output_item>", 1], "drop": ["<output_item>", 1], "float": ["<output_item>", 1], "identifier": ["<output_item>", 1], "integer": ["<output_item>", 1], "nerf": ["<output_item>", 1], "split": ["<output_item>", 1], "stack": ["<output_item>", 1]
    },
    "<function_call_stmt>": {
        "count": ["<function_call_stmt>", 0], "craft": ["<function_call_stmt>", 0], "drop": ["<function_call_stmt>", 0], "identifier": ["<function_call_stmt>", 0], "split": ["<function_call_stmt>", 0], "stack": ["<function_call_stmt>", 0]
    },
    "<function_call_expr>": {
        "count": ["<function_call_expr>", 0], "craft": ["<function_call_expr>", 0], "drop": ["<function_call_expr>", 0], "identifier": ["<function_call_expr>", 0], "split": ["<function_call_expr>", 0], "stack": ["<function_call_expr>", 0]
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
        "!": ["<argument_list>", 0], "(": ["<argument_list>", 0], "+": ["<argument_list>", 0], "++": ["<argument_list>", 0], "-": ["<argument_list>", 0], "--": ["<argument_list>", 0], "buff": ["<argument_list>", 0], "char": ["<argument_list>", 0], "count": ["<argument_list>", 0], "craft": ["<argument_list>", 0], "drop": ["<argument_list>", 0], "float": ["<argument_list>", 0], "identifier": ["<argument_list>", 0], "integer": ["<argument_list>", 0], "nerf": ["<argument_list>", 0], "split": ["<argument_list>", 0], "stack": ["<argument_list>", 0], "string": ["<argument_list>", 0],
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
    "<standard_return_statement>": {
        "ggwp": ["<standard_return_statement>", 0]
    },
    "<lobby_return_statement>": {
        "ggwp": ["<lobby_return_statement>", 0],
        "}": ["<lobby_return_statement>", 1]
    },
    "<return_value>": {
        "!": ["<return_value>", 0], "(": ["<return_value>", 0], "+": ["<return_value>", 0], "++": ["<return_value>", 0], "-": ["<return_value>", 0], "--": ["<return_value>", 0], "buff": ["<return_value>", 0], "char": ["<return_value>", 0], "count": ["<return_value>", 0], "craft": ["<return_value>", 0], "drop": ["<return_value>", 0], "float": ["<return_value>", 0], "identifier": ["<return_value>", 0], "integer": ["<return_value>", 0], "nerf": ["<return_value>", 0], "split": ["<return_value>", 0], "stack": ["<return_value>", 0], "string": ["<return_value>", 0],
        ";": ["<return_value>", 1]
    },
    "<if_statement>": {
        "clutch": ["<if_statement>", 0]
    },
    "<else_if_block>": {
        "choke_clutch": ["<else_if_block>", 0],
        "afk": ["<else_if_block>", 1], "choke": ["<else_if_block>", 1], "clutch": ["<else_if_block>", 1], "comsat": ["<else_if_block>", 1], "count": ["<else_if_block>", 1], "craft": ["<else_if_block>", 1], "dodge": ["<else_if_block>", 1], "drop": ["<else_if_block>", 1], "elo": ["<else_if_block>", 1], "frag": ["<else_if_block>", 1], "ggwp": ["<else_if_block>", 1], "grind": ["<else_if_block>", 1], "hop": ["<else_if_block>", 1], "identifier": ["<else_if_block>", 1], "ign": ["<else_if_block>", 1], "noob": ["<else_if_block>", 1], "pick": ["<else_if_block>", 1], "retry": ["<else_if_block>", 1], "role": ["<else_if_block>", 1], "shout": ["<else_if_block>", 1], "split": ["<else_if_block>", 1], "stack": ["<else_if_block>", 1], "stun": ["<else_if_block>", 1], "surebol": ["<else_if_block>", 1], "tag": ["<else_if_block>", 1], "try": ["<else_if_block>", 1], "}": ["<else_if_block>", 1]
    },
    "<else_if>": {
        "choke_clutch": ["<else_if>", 0]
    },
    "<else_block>": {
        "choke": ["<else_block>", 0],
        "afk": ["<else_block>", 1], "clutch": ["<else_block>", 1], "comsat": ["<else_block>", 1], "count": ["<else_block>", 1], "craft": ["<else_block>", 1], "dodge": ["<else_block>", 1], "drop": ["<else_block>", 1], "elo": ["<else_block>", 1], "frag": ["<else_block>", 1], "ggwp": ["<else_block>", 1], "grind": ["<else_block>", 1], "hop": ["<else_block>", 1], "identifier": ["<else_block>", 1], "ign": ["<else_block>", 1], "noob": ["<else_block>", 1], "pick": ["<else_block>", 1], "retry": ["<else_block>", 1], "role": ["<else_block>", 1], "shout": ["<else_block>", 1], "split": ["<else_block>", 1], "stack": ["<else_block>", 1], "stun": ["<else_block>", 1], "surebol": ["<else_block>", 1], "tag": ["<else_block>", 1], "try": ["<else_block>", 1], "}": ["<else_block>", 1]
    },
    "<switch_statement>": {
        "pick": ["<switch_statement>", 0]
    },
    "<case_blocks>": {
        "role": ["<case_blocks>", 0],
        "noob": ["<case_blocks>", 1], "}": ["<case_blocks>", 1]
    },
    "<case_block>": {
        "role": ["<case_block>", 0]
    },
    "<case_body>": {
        "afk": ["<case_body>", 0], "clutch": ["<case_body>", 0], "comsat": ["<case_body>", 0], "count": ["<case_body>", 0], "craft": ["<case_body>", 0], "dodge": ["<case_body>", 0], "drop": ["<case_body>", 0], "elo": ["<case_body>", 0], "frag": ["<case_body>", 0], "ggwp": ["<case_body>", 0], "grind": ["<case_body>", 0], "hop": ["<case_body>", 0], "identifier": ["<case_body>", 0], "ign": ["<case_body>", 0], "noob": ["<case_body>", 0], "pick": ["<case_body>", 0], "retry": ["<case_body>", 0], "role": ["<case_body>", 0], "shout": ["<case_body>", 0], "split": ["<case_body>", 0], "stack": ["<case_body>", 0], "stun": ["<case_body>", 0], "surebol": ["<case_body>", 0], "tag": ["<case_body>", 0], "try": ["<case_body>", 0], "}": ["<case_body>", 0]
    },
    "<default_block>": {
        "noob": ["<default_block>", 0],
        "}": ["<default_block>", 1]
    },
    "<for_loop>": {
        "grind": ["<for_loop>", 0]
    },
    "<for_init>": {
        "dodge": ["<for_init>", 0], "elo": ["<for_init>", 0], "frag": ["<for_init>", 0], "ign": ["<for_init>", 0], "surebol": ["<for_init>", 0], "tag": ["<for_init>", 0],
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
        "!": ["<expression>", 0], "(": ["<expression>", 0], "+": ["<expression>", 0], "++": ["<expression>", 0], "-": ["<expression>", 0], "--": ["<expression>", 0], "buff": ["<expression>", 0], "char": ["<expression>", 0], "count": ["<expression>", 0], "craft": ["<expression>", 0], "drop": ["<expression>", 0], "float": ["<expression>", 0], "identifier": ["<expression>", 0], "integer": ["<expression>", 0], "nerf": ["<expression>", 0], "split": ["<expression>", 0], "stack": ["<expression>", 0], "string": ["<expression>", 0]
    },
    "<logical_or_expression>": {
        "!": ["<logical_or_expression>", 0], "(": ["<logical_or_expression>", 0], "+": ["<logical_or_expression>", 0], "++": ["<logical_or_expression>", 0], "-": ["<logical_or_expression>", 0], "--": ["<logical_or_expression>", 0], "buff": ["<logical_or_expression>", 0], "char": ["<logical_or_expression>", 0], "count": ["<logical_or_expression>", 0], "craft": ["<logical_or_expression>", 0], "drop": ["<logical_or_expression>", 0], "float": ["<logical_or_expression>", 0], "identifier": ["<logical_or_expression>", 0], "integer": ["<logical_or_expression>", 0], "nerf": ["<logical_or_expression>", 0], "split": ["<logical_or_expression>", 0], "stack": ["<logical_or_expression>", 0], "string": ["<logical_or_expression>", 0]
    },
    "<logical_or_tail>": {
        "||": ["<logical_or_tail>", 0],
        ")": ["<logical_or_tail>", 1], ",": ["<logical_or_tail>", 1], ";": ["<logical_or_tail>", 1], "]": ["<logical_or_tail>", 1], "}": ["<logical_or_tail>", 1]
    },
    "<logical_and_expression>": {
        "!": ["<logical_and_expression>", 0], "(": ["<logical_and_expression>", 0], "+": ["<logical_and_expression>", 0], "++": ["<logical_and_expression>", 0], "-": ["<logical_and_expression>", 0], "--": ["<logical_and_expression>", 0], "buff": ["<logical_and_expression>", 0], "char": ["<logical_and_expression>", 0], "count": ["<logical_and_expression>", 0], "craft": ["<logical_and_expression>", 0], "drop": ["<logical_and_expression>", 0], "float": ["<logical_and_expression>", 0], "identifier": ["<logical_and_expression>", 0], "integer": ["<logical_and_expression>", 0], "nerf": ["<logical_and_expression>", 0], "split": ["<logical_and_expression>", 0], "stack": ["<logical_and_expression>", 0], "string": ["<logical_and_expression>", 0]
    },
    "<logical_and_tail>": {
        "&&": ["<logical_and_tail>", 0],
        ")": ["<logical_and_tail>", 1], ",": ["<logical_and_tail>", 1], ";": ["<logical_and_tail>", 1], "]": ["<logical_and_tail>", 1], "||": ["<logical_and_tail>", 1], "}": ["<logical_and_tail>", 1]
    },
    "<equality_expression>": {
        "!": ["<equality_expression>", 0], "(": ["<equality_expression>", 0], "+": ["<equality_expression>", 0], "++": ["<equality_expression>", 0], "-": ["<equality_expression>", 0], "--": ["<equality_expression>", 0], "buff": ["<equality_expression>", 0], "char": ["<equality_expression>", 0], "count": ["<equality_expression>", 0], "craft": ["<equality_expression>", 0], "drop": ["<equality_expression>", 0], "float": ["<equality_expression>", 0], "identifier": ["<equality_expression>", 0], "integer": ["<equality_expression>", 0], "nerf": ["<equality_expression>", 0], "split": ["<equality_expression>", 0], "stack": ["<equality_expression>", 0], "string": ["<equality_expression>", 0]
    },
    "<equality_tail>": {
        "!=": ["<equality_tail>", 0], "==": ["<equality_tail>", 0],
        "&&": ["<equality_tail>", 1], ")": ["<equality_tail>", 1], ",": ["<equality_tail>", 1], ";": ["<equality_tail>", 1], "]": ["<equality_tail>", 1], "||": ["<equality_tail>", 1], "}": ["<equality_tail>", 1]
    },
    "<equality_op>": {
        "==": ["<equality_op>", 0],
        "!=": ["<equality_op>", 1]
    },
    "<relational_expression>": {
        "!": ["<relational_expression>", 0], "(": ["<relational_expression>", 0], "+": ["<relational_expression>", 0], "++": ["<relational_expression>", 0], "-": ["<relational_expression>", 0], "--": ["<relational_expression>", 0], "buff": ["<relational_expression>", 0], "char": ["<relational_expression>", 0], "count": ["<relational_expression>", 0], "craft": ["<relational_expression>", 0], "drop": ["<relational_expression>", 0], "float": ["<relational_expression>", 0], "identifier": ["<relational_expression>", 0], "integer": ["<relational_expression>", 0], "nerf": ["<relational_expression>", 0], "split": ["<relational_expression>", 0], "stack": ["<relational_expression>", 0], "string": ["<relational_expression>", 0]
    },
    "<relational_tail>": {
        "<": ["<relational_tail>", 0], "<=": ["<relational_tail>", 0], ">": ["<relational_tail>", 0], ">=": ["<relational_tail>", 0],
        "!=": ["<relational_tail>", 1], "&&": ["<relational_tail>", 1], ")": ["<relational_tail>", 1], ",": ["<relational_tail>", 1], ";": ["<relational_tail>", 1], "==": ["<relational_tail>", 1], "]": ["<relational_tail>", 1], "||": ["<relational_tail>", 1], "}": ["<relational_tail>", 1]
    },
    "<relational_op>": {
        "<": ["<relational_op>", 0],
        ">": ["<relational_op>", 1],
        "<=": ["<relational_op>", 2],
        ">=": ["<relational_op>", 3]
    },
    "<additive_expression>": {
        "!": ["<additive_expression>", 0], "(": ["<additive_expression>", 0], "+": ["<additive_expression>", 0], "++": ["<additive_expression>", 0], "-": ["<additive_expression>", 0], "--": ["<additive_expression>", 0], "buff": ["<additive_expression>", 0], "char": ["<additive_expression>", 0], "count": ["<additive_expression>", 0], "craft": ["<additive_expression>", 0], "drop": ["<additive_expression>", 0], "float": ["<additive_expression>", 0], "identifier": ["<additive_expression>", 0], "integer": ["<additive_expression>", 0], "nerf": ["<additive_expression>", 0], "split": ["<additive_expression>", 0], "stack": ["<additive_expression>", 0], "string": ["<additive_expression>", 0]
    },
    "<additive_tail>": {
        "+": ["<additive_tail>", 0], "-": ["<additive_tail>", 0],
        "!=": ["<additive_tail>", 1], "&&": ["<additive_tail>", 1], ")": ["<additive_tail>", 1], ",": ["<additive_tail>", 1], ";": ["<additive_tail>", 1], "<": ["<additive_tail>", 1], "<=": ["<additive_tail>", 1], "==": ["<additive_tail>", 1], ">": ["<additive_tail>", 1], ">=": ["<additive_tail>", 1], "]": ["<additive_tail>", 1], "||": ["<additive_tail>", 1], "}": ["<additive_tail>", 1]
    },
    "<additive_op>": {
        "+": ["<additive_op>", 0],
        "-": ["<additive_op>", 1]
    },
    "<multiplicative_expression>": {
        "!": ["<multiplicative_expression>", 0], "(": ["<multiplicative_expression>", 0], "+": ["<multiplicative_expression>", 0], "++": ["<multiplicative_expression>", 0], "-": ["<multiplicative_expression>", 0], "--": ["<multiplicative_expression>", 0], "buff": ["<multiplicative_expression>", 0], "char": ["<multiplicative_expression>", 0], "count": ["<multiplicative_expression>", 0], "craft": ["<multiplicative_expression>", 0], "drop": ["<multiplicative_expression>", 0], "float": ["<multiplicative_expression>", 0], "identifier": ["<multiplicative_expression>", 0], "integer": ["<multiplicative_expression>", 0], "nerf": ["<multiplicative_expression>", 0], "split": ["<multiplicative_expression>", 0], "stack": ["<multiplicative_expression>", 0], "string": ["<multiplicative_expression>", 0]
    },
    "<multiplicative_tail>": {
        "%": ["<multiplicative_tail>", 0], "*": ["<multiplicative_tail>", 0], "/": ["<multiplicative_tail>", 0],
        "!=": ["<multiplicative_tail>", 1], "&&": ["<multiplicative_tail>", 1], ")": ["<multiplicative_tail>", 1], "+": ["<multiplicative_tail>", 1], ",": ["<multiplicative_tail>", 1], "-": ["<multiplicative_tail>", 1], ";": ["<multiplicative_tail>", 1], "<": ["<multiplicative_tail>", 1], "<=": ["<multiplicative_tail>", 1], "==": ["<multiplicative_tail>", 1], ">": ["<multiplicative_tail>", 1], ">=": ["<multiplicative_tail>", 1], "]": ["<multiplicative_tail>", 1], "||": ["<multiplicative_tail>", 1], "}": ["<multiplicative_tail>", 1]
    },
    "<multiplicative_op>": {
        "*": ["<multiplicative_op>", 0],
        "/": ["<multiplicative_op>", 1],
        "%": ["<multiplicative_op>", 2]
    },
    "<unary_expression>": {
        "!": ["<unary_expression>", 0], "+": ["<unary_expression>", 0], "++": ["<unary_expression>", 0], "-": ["<unary_expression>", 0], "--": ["<unary_expression>", 0],
        "(": ["<unary_expression>", 1], "buff": ["<unary_expression>", 1], "char": ["<unary_expression>", 1], "count": ["<unary_expression>", 1], "craft": ["<unary_expression>", 1], "drop": ["<unary_expression>", 1], "float": ["<unary_expression>", 1], "identifier": ["<unary_expression>", 1], "integer": ["<unary_expression>", 1], "nerf": ["<unary_expression>", 1], "split": ["<unary_expression>", 1], "stack": ["<unary_expression>", 1], "string": ["<unary_expression>", 1]
    },
    "<unary_op>": {
        "+": ["<unary_op>", 0],
        "-": ["<unary_op>", 1],
        "!": ["<unary_op>", 2],
        "++": ["<unary_op>", 3],
        "--": ["<unary_op>", 4]
    },
    "<postfix_expression>": {
        "(": ["<postfix_expression>", 0], "buff": ["<postfix_expression>", 0], "char": ["<postfix_expression>", 0], "count": ["<postfix_expression>", 0], "craft": ["<postfix_expression>", 0], "drop": ["<postfix_expression>", 0], "float": ["<postfix_expression>", 0], "identifier": ["<postfix_expression>", 0], "integer": ["<postfix_expression>", 0], "nerf": ["<postfix_expression>", 0], "split": ["<postfix_expression>", 0], "stack": ["<postfix_expression>", 0], "string": ["<postfix_expression>", 0]
    },
    "<postfix_tail>": {
        "++": ["<postfix_tail>", 0], "--": ["<postfix_tail>", 0],
        "[": ["<postfix_tail>", 1],
        "(": ["<postfix_tail>", 2],
        ".": ["<postfix_tail>", 3],
        "!=": ["<postfix_tail>", 4], "%": ["<postfix_tail>", 4], "&&": ["<postfix_tail>", 4], ")": ["<postfix_tail>", 4], "*": ["<postfix_tail>", 4], "+": ["<postfix_tail>", 4], ",": ["<postfix_tail>", 4], "-": ["<postfix_tail>", 4], "/": ["<postfix_tail>", 4], ";": ["<postfix_tail>", 4], "<": ["<postfix_tail>", 4], "<=": ["<postfix_tail>", 4], "==": ["<postfix_tail>", 4], ">": ["<postfix_tail>", 4], ">=": ["<postfix_tail>", 4], "]": ["<postfix_tail>", 4], "||": ["<postfix_tail>", 4], "}": ["<postfix_tail>", 4]
    },
    "<postfix_op>": {
        "++": ["<postfix_op>", 0],
        "--": ["<postfix_op>", 1]
    },
    "<function_call_suffix>": {
        "(": ["<function_call_suffix>", 0]
    },
    "<primary_expression>": {
        "buff": ["<primary_expression>", 0], "char": ["<primary_expression>", 0], "float": ["<primary_expression>", 0], "integer": ["<primary_expression>", 0], "nerf": ["<primary_expression>", 0], "string": ["<primary_expression>", 0],
        "identifier": ["<primary_expression>", 1],
        "(": ["<primary_expression>", 2],
        "count": ["<primary_expression>", 3], "craft": ["<primary_expression>", 3], "drop": ["<primary_expression>", 3], "split": ["<primary_expression>", 3], "stack": ["<primary_expression>", 3]
    },
    "<data_type>": {
        "frag": ["<data_type>", 0],
        "elo": ["<data_type>", 1],
        "ign": ["<data_type>", 2],
        "surebol": ["<data_type>", 3],
        "dodge": ["<data_type>", 4],
        "tag": ["<data_type>", 5]
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
    "<assign_tail>": {
        "=": ["<assign_tail>", 0], "%=": ["<assign_tail>", 0], "*=": ["<assign_tail>", 0], "+=": ["<assign_tail>", 0], "-=": ["<assign_tail>", 0], "/=": ["<assign_tail>", 0],
        "++": ["<assign_tail>", 1],
        "--": ["<assign_tail>", 2],
        ".": ["<assign_tail>", 3]
    },
    "<condition>": {
        "!": ["<condition>", 0], "(": ["<condition>", 0], "+": ["<condition>", 0], "++": ["<condition>", 0], "-": ["<condition>", 0], "--": ["<condition>", 0], "buff": ["<condition>", 0], "char": ["<condition>", 0], "count": ["<condition>", 0], "craft": ["<condition>", 0], "drop": ["<condition>", 0], "float": ["<condition>", 0], "identifier": ["<condition>", 0], "integer": ["<condition>", 0], "nerf": ["<condition>", 0], "split": ["<condition>", 0], "stack": ["<condition>", 0], "string": ["<condition>", 0]
    },
    "<literal>": {
        "integer": ["<literal>", 0],
        "float": ["<literal>", 1],
        "string": ["<literal>", 2],
        "char": ["<literal>", 3],
        "buff": ["<literal>", 4], "nerf": ["<literal>", 4]
    },
    "<boolean_literal>": {
        "buff": ["<boolean_literal>", 0],
        "nerf": ["<boolean_literal>", 1]
    },
    "<constant_value>": {
        "(": ["<constant_value>", 0], "buff": ["<constant_value>", 0], "char": ["<constant_value>", 0], "float": ["<constant_value>", 0], "integer": ["<constant_value>", 0], "nerf": ["<constant_value>", 0], "string": ["<constant_value>", 0]
    },
    "<const_add_expression>": {
        "(": ["<const_add_expression>", 0], "buff": ["<const_add_expression>", 0], "char": ["<const_add_expression>", 0], "float": ["<const_add_expression>", 0], "integer": ["<const_add_expression>", 0], "nerf": ["<const_add_expression>", 0], "string": ["<const_add_expression>", 0]
    },
    "<const_add_tail>": {
        "+": ["<const_add_tail>", 0],
        "-": ["<const_add_tail>", 1],
        ")": ["<const_add_tail>", 2], ",": ["<const_add_tail>", 2], ";": ["<const_add_tail>", 2], "}": ["<const_add_tail>", 2]
    },
    "<const_mul_expression>": {
        "(": ["<const_mul_expression>", 0], "buff": ["<const_mul_expression>", 0], "char": ["<const_mul_expression>", 0], "float": ["<const_mul_expression>", 0], "integer": ["<const_mul_expression>", 0], "nerf": ["<const_mul_expression>", 0], "string": ["<const_mul_expression>", 0]
    },
    "<const_mul_tail>": {
        "*": ["<const_mul_tail>", 0],
        "/": ["<const_mul_tail>", 1],
        "%": ["<const_mul_tail>", 2],
        ")": ["<const_mul_tail>", 3], "+": ["<const_mul_tail>", 3], ",": ["<const_mul_tail>", 3], "-": ["<const_mul_tail>", 3], ";": ["<const_mul_tail>", 3], "}": ["<const_mul_tail>", 3]
    },
    "<const_primary>": {
        "buff": ["<const_primary>", 0], "char": ["<const_primary>", 0], "float": ["<const_primary>", 0], "integer": ["<const_primary>", 0], "nerf": ["<const_primary>", 0], "string": ["<const_primary>", 0],
        "(": ["<const_primary>", 1]
    },
    "<case_value>": {
        "integer": ["<case_value>", 0],
        "char": ["<case_value>", 1],
        "string": ["<case_value>", 2],
        "buff": ["<case_value>", 3], "nerf": ["<case_value>", 3]
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
        # 1. Filter out whitespace, newlines, and comments first to find real code
        self.tokens = [t for t in tokens if t.type not in [
            TokenType.whitespace, 
            TokenType.newline, 
            TokenType.comment, 
            TokenType.eof
        ]]
        
        # 2. Anchor the EOF to the exact end of the last real token
        if self.tokens:
            last_real_token = self.tokens[-1]
            self.eof_line = last_real_token.line
            # Add the length of the last token to point right after it
            self.eof_col = last_real_token.column + len(str(last_real_token.value))
        else:
            self.eof_line = 1
            self.eof_col = 1
            
        self.token_idx = -1
        self.advance()

    def advance(self):
        self.token_idx += 1
        if self.token_idx < len(self.tokens):
            self.current_token = self.tokens[self.token_idx]
            # Use map_token_type to translate Lexer Type -> Grammar Symbol
            self.current_type = self.map_token_type(self.current_token)
        else:
            # 3. Use smart EOF coordinates
            self.current_token = Token(TokenType.eof, None, line=self.eof_line, column=self.eof_col)
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
        if t == TokenType.separator:
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
                # Array Dimension Validation
                if top == "<positive_integer>" and str(self.current_token.value) == "0":
                    error = InvalidSyntaxError(line, column, "Array dimensions must be greater than 0.")
                    break
                
                # Ambiguity Check: Main Function vs Global Section
                if top == "<global_section>" and self.current_type == "frag":
                    if self.peek_n(1) != "identifier":
                        stack.pop()
                        continue

                # Ambiguity Check: Array vs Variable Declaration
                ambiguous_parents = ["<global_declaration>", "<local_declaration>", "<declaration_statement>"]
                data_types = ["frag", "elo", "ign", "surebol", "tag"]

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

                # ------------------------------------------------------------------
                # ---> NEW CODE STARTS HERE <---
                # ------------------------------------------------------------------
                # Ambiguity Check 1: Assignment vs Function Call Statement
                if top == "<executable_statement>" and self.current_type == "identifier":
                    symbol_after_id = self.peek_n(1)
                    stack.pop()
                    if symbol_after_id == "(":
                        stack.append("<function_call_stmt>")
                    else:
                        stack.append("<assignment_statement>")
                    continue
                    
                # Ambiguity Check 2: Variable vs Function Call in Math Expressions
                if top == "<primary_expression>" and self.current_type == "identifier":
                    symbol_after_id = self.peek_n(1)
                    stack.pop()
                    if symbol_after_id == "(":
                        stack.append("<function_call_expr>")
                    else:
                        stack.append("identifier")
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
                        f"Unexpected '{self.current_type}' while parsing. {top} Expected: {expected}"
                    )

            else:
                # Terminal Matching
                stack.pop()
                if top == self.current_type:
                    self.advance()
                else:
                    error = InvalidSyntaxError(
                        line, column, 
                        f"Unexpected '{self.current_type}' while parsing.  Expected: {top}"
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