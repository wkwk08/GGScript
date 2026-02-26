from decimal import Decimal
from typing import List, Dict, Optional, Tuple, Any

from .token_types import TokenType
from .token import Token

# ────────────────────────────────────────────────────────────────────────────────
# ERROR REPORTING UTILITIES
# ────────────────────────────────────────────────────────────────────────────────

class ErrorNode:
    def __init__(self, line, startCol, tokenName=None):
        self.line = line
        self.startCol = startCol
        self.tokenName = tokenName

class SemanticError(Exception):
    pass

# ────────────────────────────────────────────────────────────────────────────────
# ABSTRACT SYNTAX TREE (AST) NODES (GGScript Structure)
# ────────────────────────────────────────────────────────────────────────────────

class node_program:
    def __init__(self, globals_n, funcs_n, main_n):
        self.globals_n = globals_n
        self.funcs_n = funcs_n
        self.main_n = main_n

class node_vardec:
    def __init__(self, dtype_t, id_t, const_b, init_value_n):
        self.dtype_t = dtype_t
        self.id_t = id_t
        self.const_b = const_b
        self.init_value_n = init_value_n

class node_arr_dec:
    def __init__(self, dtype_t, id_t, const_b, size1_n, size2_n, init_values_n):
        self.dtype_t = dtype_t
        self.id_t = id_t
        self.const_b = const_b
        self.size1_n = size1_n
        self.size2_n = size2_n
        self.init_values_n = init_values_n

class node_func_dec:
    def __init__(self, dtype_t, id_t, params_n, body_n):
        self.dtype_t = dtype_t
        self.id_t = id_t
        self.params_n = params_n
        self.body_n = body_n

class node_funcpar_var:
    def __init__(self, dtype_t, id_t):
        self.dtype_t = dtype_t
        self.id_t = id_t

class node_main_func:
    def __init__(self, body_n):
        self.body_n = body_n

class node_code_block:
    def __init__(self, statements_n):
        self.statements_n = statements_n

class node_if_stmt:
    def __init__(self, condition_n, body_n, else_chain_n, else_stmt_n):
        self.condition_n = condition_n
        self.body_n = body_n
        self.else_chain_n = else_chain_n
        self.else_stmt_n = else_stmt_n

class node_else_if_stmt:
    def __init__(self, condition_n, body_n):
        self.condition_n = condition_n
        self.body_n = body_n

class node_else_stmt:
    def __init__(self, body_n):
        self.body_n = body_n

class node_switch_stmt:
    def __init__(self, value_n, cases_n, default_n):
        self.value_n = value_n
        self.cases_n = cases_n
        self.default_n = default_n

class node_case_stmt:
    def __init__(self, case_value_n, body_n):
        self.case_value_n = case_value_n
        self.body_n = body_n

class node_default_stmt:
    def __init__(self, body_n):
        self.body_n = body_n

class node_loop_stmt:
    def __init__(self, loop_type, init_n, condition_n, update_n, body_n):
        self.loop_type = loop_type
        self.init_n = init_n
        self.condition_n = condition_n
        self.update_n = update_n
        self.body_n = body_n

class node_assign_stmt:
    def __init__(self, id_t, op_t, value_n):
        self.id_t = id_t
        self.op_t = op_t
        self.value_n = value_n

class node_arr_assign_stmt:
    def __init__(self, arr_idx_n, op_t, value_n):
        self.arr_idx_n = arr_idx_n
        self.op_t = op_t
        self.value_n = value_n

class node_input:
    def __init__(self, targets_n):
        self.targets_n = targets_n

class node_output:
    def __init__(self, print_params_n):
        self.print_params_n = print_params_n

class node_func_call:
    def __init__(self, id_t, args_n):
        self.id_t = id_t
        self.args_n = args_n

class node_method_call:
    def __init__(self, id_t, method_t, args_n):
        self.id_t = id_t
        self.method_t = method_t
        self.args_n = args_n

class node_return_block:
    def __init__(self, ret_value_n):
        self.ret_value_n = ret_value_n

class node_break_stmt:
    def __init__(self, id_t):
        self.id_t = id_t

class node_continue_stmt:
    def __init__(self, id_t):
        self.id_t = id_t

class node_bi_op:
    def __init__(self, left_n, op_t, right_n):
        self.left_n = left_n
        self.op_t = op_t
        self.right_n = right_n

class node_pre_un_op:
    def __init__(self, op_t, right_n):
        self.op_t = op_t
        self.right_n = right_n

class node_post_un_op:
    def __init__(self, left_n, op_t):
        self.left_n = left_n
        self.op_t = op_t

class node_iden:
    def __init__(self, id_t):
        self.id_t = id_t

class node_arr_idx:
    def __init__(self, id_t, idx1_n, idx2_n=None):
        self.id_t = id_t
        self.idx1_n = idx1_n
        self.idx2_n = idx2_n

class node_num:
    def __init__(self, val_t, dtype):
        self.val_t = val_t
        self.dtype = dtype

class node_str:
    def __init__(self, val_t):
        self.val_t = val_t

class node_bool:
    def __init__(self, val_t):
        self.val_t = val_t

class node_char:
    def __init__(self, val_t):
        self.val_t = val_t

# ────────────────────────────────────────────────────────────────────────────────
# SYMBOL TABLE
# ────────────────────────────────────────────────────────────────────────────────

class SymbolTable:
    def __init__(self, parent=None):
        self.syms = {} 
        self.parent = parent 

    def get(self, sym_name, checkParent=True):
        sym = self.syms.get(sym_name, None)
        if not sym and self.parent and checkParent:
            return self.parent.get(sym_name) 
        return sym

    def _create_symbol_entry(self, value, dtype, const):  
        return {
            "value": value,
            "dtype": dtype, 
            "const": const, 
        }

    def set(self, sym_name, value, dtype=None, const=False):
        sym_content = self._create_symbol_entry(value, dtype, const)
        self.syms[sym_name] = sym_content 
        return {sym_name: sym_content} 

    def set_array(self, sym_name, value, dtype, arr_info, const=False):
        sym_content = self._create_symbol_entry(value, dtype, const)
        sym_content["arr_info"] = arr_info  
        self.syms[sym_name] = sym_content 
        return {sym_name: sym_content}

    def set_function(self, sym_name, return_type, param_types):
        sym_content = {
            "value": None,
            "dtype": return_type,
            "params": param_types 
        }
        self.syms[sym_name] = sym_content
        return {sym_name: sym_content}
    
    def print_symbol_tree(self, indent=0):
        print("\t" * indent + f"Scope Level {indent}: {self.syms}")
        if self.parent:
            self.parent.print_symbol_tree(indent + 1) 

# ────────────────────────────────────────────────────────────────────────────────
# SEMANTIC ANALYZER
# ────────────────────────────────────────────────────────────────────────────────

class SemanticAnalyzer:
    numtypes = ['frag', 'elo']

    default_vals = { 
        'ign': '',
        'surebol' : False,
        'frag' : 0,
        'elo' : Decimal('0.0'),
        'tag' : ' ',
        'dodge': None
    }
   
    # GGScript specific valid ranges
    MIN_FRAG = -999999999999999
    MAX_FRAG =  999999999999999
    MIN_ELO = -999999990.0
    MAX_ELO =  999999990.0

    def __init__(self):
        self.curr_scope = SymbolTable() 
        self.errors = []    
        self.loop_depth = 0    
        self.switch_depth = 0  
        self.function_return_stack = [] 

    def interpret(self, node):
            try:
                self.visit_node(node) 
                # Success message removed from the error list
                print("Semantic checking completed successfully. No Semantic Errors found.")
                print('---------GLOBAL TABLE---------\n\t\t')
                self.print_symbols(self.curr_scope.syms, indent=2)
            except SemanticError as e:
                pass
            return self.errors

    def enter_scope(self, nodeName): 
        print(f'\n(semantic)(dbg) ENTERING scope {nodeName}')
        self.curr_scope = SymbolTable(self.curr_scope) 
    
    def exit_scope(self, nodeName):
        print(f'\n(semantic)(dbg) EXITING scope {nodeName}, table: ')
        self.print_symbols(self.curr_scope.syms, indent=2)
        self.curr_scope = self.curr_scope.parent

    def visit_node(self, node, funcExpectedVal=True):
        if node is None:
            return None
        nodeName = type(node).__name__
        visit_func = getattr(self, f'visit_{nodeName}', None)

        if visit_func is None:
            print(f"\n(semantic)(dbg) Not implemented yet: {nodeName}")
            return None
        else:
            print(f'\n(semantic)(dbg) VISITING {nodeName}!!')
            ret_val = None
            if nodeName in ['node_func_call', 'node_method_call']:
                ret_val = visit_func(node, expected_val=funcExpectedVal) 
            else:
                ret_val = visit_func(node)
                
            if nodeName in ['node_iden', 'node_num', 'node_bi_op', 'node_un_op', 'node_post_un_op', 'node_pre_un_op', 'node_arr_idx', 'node_func_call', 'node_method_call']:
                if ret_val and ret_val[0][1] == 'elo' and ret_val[0][0] in ['var', 'lit']:  
                    ret_val = (ret_val[0], Decimal(ret_val[1] if ret_val[1] is not None else 0), ret_val[2]) 
            return ret_val
        
    def print_symbols(self, d, indent=2):
        if isinstance(d, dict):
            if not d:
                print("\t" * indent + "{ }")
                return
            for key, value in d.items():
                print("\t" * indent + f"{key} :", end=" ")
                if isinstance(value, dict):
                    print("{") 
                    self.print_symbols(value, indent + 1)
                    print("\t" * indent + "}") 
                elif isinstance(value, list):
                    if not value: print("[ ]")
                    else:
                        print("[")
                        for item in value:
                            if isinstance(item, dict):
                                self.print_symbols(item, indent + 1)
                            else: print("\t" * (indent + 1) + str(item))
                        print("\t" * indent + "]")
                else: print(value)
        elif isinstance(d, list): 
            if not d: print("\t" * indent + "[ ]") 
            else:
                print("\t" * indent + "[") 
                for item in d:
                    if isinstance(item, dict): 
                        self.print_symbols(item, indent + 1)
                    else: print("\t" * (indent + 1) + str(item))
                print("\t" * indent + "]")
        else: print(d) 

    def logError(self, msg, err_n=None): 
        if isinstance(err_n, ErrorNode):
            full_message = f"Semantic Error Ln {err_n.line}, Col {err_n.startCol}: {msg}"
        else:
            full_message = f"Semantic Error: {msg}"
            
        self.errors.append(full_message)
        print(full_message)
        raise SemanticError(full_message)

    # ------------------------------------ NODE VISITATION FUNCS ----------------------------------

    def visit_node_program(self, node):
            self.has_main = False
            
            for statement in node.globals_n: 
                self.visit_node(statement)

            for func in node.funcs_n:
                self.visit_node(func)

            if node.main_n:
                self.has_main = True
                self.current_function_name = "lobby" 
                self.function_return_stack.append("frag")
                self.count_return = 0
                    
                self.visit_node(node.main_n)
                
                self.function_return_stack.pop()
                self.current_function_name = None
            
            if not self.has_main:
                self.logError(f"Program must contain a main 'lobby' function.", ErrorNode(1, 1))

    def visit_node_main_func(self, node):
        self.enter_scope("lobby") 
        self.visit_node(node.body_n) 
        self.exit_scope("lobby")

    def visit_node_code_block(self, node):
        for statement in node.statements_n:
            self.visit_node(statement, funcExpectedVal=False)

    def visit_node_vardec(self, node):
        err_n = ErrorNode(node.id_t["tokenLine"], node.id_t["tokenCol"], node.id_t["tokenName"])

        if self.curr_scope.get(node.id_t["tokenName"], False):
            self.logError(f"Symbol '{node.id_t['tokenName']}' has already been declared.", err_n)
            
        const = node.const_b
        dtype = ('var', node.dtype_t["tokenName"])
        id_name = node.id_t["tokenName"]
        
        val_type = None
        value = None
        
        if node.init_value_n: 
            val_type, value, _ = self.visit_node(node.init_value_n)

        default_val = self.default_vals[dtype[1]]

        if not val_type and value is None:
            if const:
                self.logError("Constant ('stun') variables must be initialized.", err_n)
            val_type = ('lit', dtype[1])   
            value = default_val

        self.check_type_and_range("variable", dtype, val_type, value, id_n=node.id_t, err_n=err_n)
        self.curr_scope.set(id_name, value, dtype=dtype, const=const)

    def visit_node_arr_dec(self, node):
        err_n = ErrorNode(node.id_t["tokenLine"], node.id_t["tokenCol"], node.id_t["tokenName"])
        id_name = node.id_t["tokenName"]
        const = node.const_b
        
        if self.curr_scope.get(id_name, checkParent=False):
            self.logError(f"Symbol '{id_name}' has already been declared.", err_n)

        dtype = ('arr', node.dtype_t["tokenName"])
        base_val = self.default_vals[dtype[1]]

        dim = 1
        size_1_type, size_1, _ = self.visit_node(node.size1_n)
        
        if size_1_type[1] != 'frag':
            self.logError(f"Array size must be a 'frag', got '{size_1_type[1]}'.", err_n)

        size_2 = None
        if node.size2_n:
            dim = 2
            size_2_type, size_2, _ = self.visit_node(node.size2_n)
            if size_2_type[1] != 'frag':
                self.logError(f"Array 2nd dimension must be a 'frag', got '{size_2_type[1]}'.", err_n)

        if const and not node.init_values_n:
            self.logError("Constant arrays must be initialized.", err_n)

        arr_vals = []
        if not node.init_values_n:
            if dim == 1:
                arr_vals = [base_val for _ in range(size_1)]
            else:
                arr_vals = [[base_val for _ in range(size_2)] for _ in range(size_1)]
        else:
            if dim == 1:
                for idx, v_node in enumerate(node.init_values_n):
                    v_type, v_val, v_err = self.visit_node(v_node)
                    self.check_type_and_range("array element", dtype, v_type, v_val, node.id_t, index_1D=idx, err_n=v_err)
                    arr_vals.append(v_val)
            else:
                # Assuming nested lists for 2D initialization
                for idx1, inner_arr in enumerate(node.init_values_n):
                    row = []
                    for idx2, v_node in enumerate(inner_arr):
                        v_type, v_val, v_err = self.visit_node(v_node)
                        self.check_type_and_range("array element", dtype, v_type, v_val, node.id_t, index_1D=idx1, index_2D=idx2, err_n=v_err)
                        row.append(v_val)
                    arr_vals.append(row)

        self.curr_scope.set_array(id_name, arr_vals, dtype=dtype, arr_info={'dimension': dim, 'size1': size_1, 'size2': size_2}, const=const)

    def visit_node_func_dec(self, node):
        func_name = node.id_t["tokenName"]
        err_n = ErrorNode(node.id_t["tokenLine"], node.id_t["tokenCol"])
        return_type = ('func', node.dtype_t["tokenName"])

        if self.curr_scope.get(func_name, checkParent=False):
            self.logError(f"Symbol '{func_name}' has already been declared.", err_n)

        param_types = []
        if node.params_n: 
            for param in node.params_n:
                param_types.append({
                    "dtype": ("var", param.dtype_t["tokenName"]) 
                })  
        
        self.current_function_name = func_name
        self.curr_scope.set_function(func_name, return_type, param_types)

        self.enter_scope(f"Function: {func_name}")
        
        if node.params_n:
            for param in node.params_n:
                param_name = param.id_t["tokenName"]
                if self.curr_scope.get(param_name, checkParent=False):
                    self.logError(f"Parameter '{param_name}' already declared in function '{func_name}'.", err_n)
                
                var_dtype = ('var', param.dtype_t["tokenName"])
                self.curr_scope.set(param_name, value=self.default_vals[var_dtype[1]], dtype=var_dtype, const=False)

        self.function_return_stack.append(return_type[1])
        
        if not node.body_n:
            self.logError(f"Function '{func_name}' must have a body.", err_n)

        self.count_return = 0
        has_return = self.check_return_in_body(node.body_n)
        if return_type[1] != 'dodge' and not has_return:
            self.logError(f"Function '{func_name}' must have a return statement on all code paths.", err_n)
                
        self.visit_node(node.body_n)

        self.function_return_stack.pop()
        self.current_function_name = None
        self.exit_scope(f"Function: {func_name}")

    def visit_node_assign_stmt(self, node): 
        iden_name = node.id_t["tokenName"]
        iden_symbol = self.curr_scope.get(iden_name)
        id_err = ErrorNode(node.id_t["tokenLine"], node.id_t["tokenCol"], node.id_t["tokenName"])
        
        if not iden_symbol: 
            self.logError(f"Symbol '{iden_name}' hasn't been declared yet.", id_err)

        if iden_symbol["dtype"][0] == "arr":
            self.logError(f"Symbol '{iden_name}' is an array and cannot be reassigned.", id_err)
            
        if iden_symbol.get("const"):
            self.logError(f"Symbol '{iden_name}' is a constant ('stun') and cannot be reassigned.", id_err)
            
        val_type, val, val_err = self.visit_node(node.value_n)
        
        # Handle compound assignments (+=, -=, *=, /=, %=)
        op = node.op_t["tokenName"]
        if op in ['+=', '-=', '*=', '/=', '%=']:
            if iden_symbol["dtype"][1] not in self.numtypes or val_type[1] not in self.numtypes:
                if not (op == '+=' and iden_symbol["dtype"][1] == 'ign' and val_type[1] in ['ign', 'tag']):
                    self.logError(f"Compound assignment '{op}' invalid between '{iden_symbol['dtype'][1]}' and '{val_type[1]}'.", id_err)

        self.check_type_and_range("variable", iden_symbol["dtype"], val_type, val, id_n=node.id_t, err_n=val_err)

    def visit_node_arr_assign_stmt(self, node):
        arr_name = node.arr_idx_n.id_t["tokenName"]
        arr_symbol = self.curr_scope.get(arr_name) 
        arr_err = ErrorNode(node.arr_idx_n.id_t["tokenLine"], node.arr_idx_n.id_t["tokenCol"], node.arr_idx_n.id_t["tokenName"])

        if not arr_symbol:
            self.logError(f"Array '{arr_name}' hasn't been declared yet.", arr_err)

        if arr_symbol["const"]:
            self.logError(f"Array '{arr_name}' is a constant and cannot be modified.", arr_err)

        arr_dtype = arr_symbol["dtype"][1]
        if arr_symbol["dtype"][0] != 'arr':
            if arr_dtype == 'ign':
                self.logError(f"Strings ('ign') are not mutable by index.", arr_err)
            else:
                self.logError(f"Symbol '{arr_name}' is not an array.", arr_err)

        arr_dim = arr_symbol["arr_info"]["dimension"]

        idx1_type, idx1_val, idx_err = self.visit_node(node.arr_idx_n.idx1_n)
        if idx1_type[1] != 'frag':
            self.logError(f"Array index must be a 'frag' (integer), found '{idx1_type[1]}'.", idx_err)

        idx2_val = None
        if node.arr_idx_n.idx2_n:
            if arr_dim == 1:
                self.logError(f"Array '{arr_name}' is 1D but accessed with 2 indices.", arr_err)
            idx2_type, idx2_val, idx2_err = self.visit_node(node.arr_idx_n.idx2_n)
            if idx2_type[1] != 'frag':
                self.logError(f"Array index must be a 'frag', found '{idx2_type[1]}'.", idx2_err)
        elif arr_dim == 2:
            self.logError(f"Array '{arr_name}' is 2D but accessed with 1 index.", arr_err)

        value_type, value, val_err_n = self.visit_node(node.value_n)

        # Handle compound assignments (+=, -=, *=, /=, %=)
        op = node.op_t["tokenName"]
        if op in ['+=', '-=', '*=', '/=', '%=']:
            if arr_symbol["dtype"][1] not in self.numtypes or value_type[1] not in self.numtypes:
                if not (op == '+=' and arr_symbol["dtype"][1] == 'ign' and value_type[1] in ['ign', 'tag']):
                    self.logError(f"Compound assignment '{op}' invalid between '{arr_symbol['dtype'][1]}' and '{value_type[1]}'.", arr_err)

        self.check_type_and_range("array element", arr_symbol["dtype"], value_type, value, id_n=node.arr_idx_n.id_t, index_1D=idx1_val, index_2D=idx2_val, err_n=val_err_n)

    def visit_node_func_call(self, node, expected_val):
        func_name = node.id_t["tokenName"]
        func_symbol = self.curr_scope.get(func_name)
        err_n = ErrorNode(node.id_t["tokenLine"], node.id_t["tokenCol"], node.id_t["tokenName"])
        
        if not func_symbol:
            self.logError(f"Function '{func_name}' hasn't been declared yet.", err_n)
        if func_symbol["dtype"][0] != 'func':
            self.logError(f"Symbol '{func_name}' is not a function.", err_n)
        
        self.check_function_params(func_symbol, node.args_n, node.id_t, "function")
        
        val = None
        if func_symbol["dtype"][1] == 'dodge':
            if expected_val:
                self.logError(f"Void ('dodge') function '{func_name}' cannot be used as a value.", err_n)
        else:
            val = self.default_vals[func_symbol["dtype"][1]]

        return (('lit', f'{func_symbol["dtype"][1]}'), val, err_n) 

    def check_function_params(self, func_symbol, args, node_id, call_string):
        err_n = ErrorNode(node_id["tokenLine"], node_id["tokenCol"], node_id["tokenName"])
        if func_symbol["params"]:
            if len(func_symbol["params"]) != len(args):
                self.logError(f"{call_string.capitalize()} '{node_id['tokenName']}' expects {len(func_symbol['params'])} parameters, got {len(args)}.", err_n)
            
            for i, (arg_node, param_type) in enumerate(zip(args, func_symbol["params"])):
                arg_val_type, arg_val, arg_err_n = self.visit_node(arg_node)
                if param_type["dtype"][1] != arg_val_type[1]: 
                    if not (param_type["dtype"][1] == 'elo' and arg_val_type[1] == 'frag'):
                        self.logError(f"Type mismatch for param {i+1} of '{node_id['tokenName']}': expected '{param_type['dtype'][1]}', got '{arg_val_type[1]}'.", arg_err_n)
        else:
            if args:
                self.logError(f"{call_string.capitalize()} '{node_id['tokenName']}' expects 0 parameters, got {len(args)}.", err_n)

    def visit_node_method_call(self, node, expected_val):
        target_type, target_val, target_err = self.visit_node(node.target_n)
        method_name = node.method_t["tokenName"]
        err_n = ErrorNode(node.method_t["tokenLine"], node.method_t["tokenCol"], node.method_t["tokenName"])

        if method_name in ["stack", "craft", "drop", "count"]:
            if target_type[0] != "arr":
                self.logError(f"Method '{method_name}' is only valid for arrays.", target_err)
            if method_name == "count":
                return (('lit', 'frag'), 0, err_n)
            return (('lit', 'dodge'), None, err_n)

        elif method_name == "split":
            if target_type[1] != "ign":
                self.logError(f"Method 'split' is only valid for string ('ign') types.", target_err)
            return (('arr', 'ign'), [], err_n)

        self.logError(f"Unknown method '{method_name}'.", err_n)

    def visit_node_iden(self, node):
        iden_symbol = self.curr_scope.get(node.id_t["tokenName"])
        err_n = ErrorNode(node.id_t["tokenLine"], node.id_t["tokenCol"], node.id_t["tokenName"])
        if not iden_symbol:
            self.logError(f"Symbol '{node.id_t['tokenName']}' hasn't been declared yet.", err_n)
        else:
            if iden_symbol["dtype"][0] == 'func':
                self.logError(f"Symbol '{node.id_t['tokenName']}' is a function and needs to be called '()'.", err_n)
            return (iden_symbol.get("dtype"), iden_symbol.get("value"), err_n)

    def visit_node_num(self, node):
        err_n = ErrorNode(node.val_t["tokenLine"], node.val_t["tokenCol"], node.val_t["tokenName"])
        val = 0
        if node.dtype == "frag":
            val = int(node.val_t["tokenName"])
            if val > self.MAX_FRAG or val < self.MIN_FRAG:
                self.logError(f"Value {val} is out of 'frag' bounds.", err_n)
        elif node.dtype == "elo":
            val = Decimal(node.val_t["tokenName"])
            if val > self.MAX_ELO or val < self.MIN_ELO:
                self.logError(f"Value {val} is out of 'elo' bounds.", err_n)
        return (('lit', node.dtype), val, err_n) 

    def visit_node_str(self, node):
        err_n = ErrorNode(node.val_t["tokenLine"], node.val_t["tokenCol"], node.val_t["tokenName"])
        return (('lit', 'ign'), node.val_t["tokenName"][1:-1], err_n)
    
    def visit_node_bool(self, node):
        err_n = ErrorNode(node.val_t["tokenLine"], node.val_t["tokenCol"], node.val_t["tokenName"])
        return (('lit', 'surebol'), node.val_t["tokenName"] == "buff", err_n)

    def visit_node_char(self, node):
        err_n = ErrorNode(node.val_t["tokenLine"], node.val_t["tokenCol"], node.val_t["tokenName"])
        return (('lit', 'tag'), node.val_t["tokenName"][1:-1], err_n)

    def visit_node_arr_idx(self, node): 
        arr_sym = self.curr_scope.get(node.id_t["tokenName"])
        arr_err = ErrorNode(node.id_t["tokenLine"], node.id_t["tokenCol"], node.id_t["tokenName"])
        
        if not arr_sym:
            self.logError(f"Symbol '{node.id_t['tokenName']}' has not been declared.", arr_err)
        
        dtype = arr_sym["dtype"][1]
        idx_type, idx_val, idx_err = self.visit_node(node.idx1_n)

        if arr_sym["dtype"][0] != 'arr':
            if not node.idx2_n and dtype == 'ign':
                if idx_type[1] != 'frag':
                    self.logError(f"Expected 'frag' (integer) for string indexing, got '{idx_type[1]}'.", idx_err)
                return (('lit', 'tag'), "", arr_err)
            else:
                self.logError(f"Symbol '{node.id_t['tokenName']}' is not an array.", arr_err)

        if idx_type[1] != 'frag':
            self.logError(f"Expected 'frag' for array index, got '{idx_type[1]}'.", idx_err)

        if node.idx2_n:
            if arr_sym["arr_info"]["dimension"] == 1:
                if dtype == 'ign':
                    self.logError("String indexing not allowed for array elements.", arr_err)
                self.logError(f"Array '{node.id_t['tokenName']}' is 1D but accessed with 2 indices.", arr_err)
            
            idx2_type, idx2_val, idx2_err = self.visit_node(node.idx2_n)
            if idx2_type[1] != 'frag':
                self.logError(f"Expected 'frag' for array index, got '{idx2_type[1]}'.", idx2_err)
        else:
            if arr_sym["arr_info"]["dimension"] == 2:
                return (('arr', dtype), self.default_vals[dtype], arr_err)
        
        return (('var', dtype), self.default_vals[dtype], arr_err)

    def visit_node_bi_op(self, node):
        left_type, left_val, left_err = self.visit_node(node.left_n)
        right_type, right_val, right_err = self.visit_node(node.right_n)
        
        if left_type[0] == 'arr' or right_type[0] == 'arr':
            self.logError("Direct operations on entire arrays are not allowed. Access elements.", left_err)

        left_val = Decimal(left_val) if left_type[1] == 'elo' else int(left_val) if left_type[1] == 'frag' and left_val is not None else left_val
        right_val = Decimal(right_val) if right_type[1] == 'elo' else int(right_val) if right_type[1] == 'frag' and right_val is not None else right_val

        dtype = ('lit', 'frag')
        if left_type[1] == 'elo' or right_type[1] == 'elo':
            dtype = ('lit', 'elo')

        op = node.op_t["tokenName"]

        if op == '+': 
            if left_type[1] == 'ign':
                if right_type[1] not in ['ign', 'tag']:
                    self.logError(f"Cannot concatenate 'ign' with '{right_type[1]}'.", right_err)
                return (('lit', 'ign'), str(left_val or "") + str(right_val or ""), left_err)
            elif left_type[1] in self.numtypes and right_type[1] in self.numtypes:
                return (dtype, (left_val or 0) + (right_val or 0), left_err)
            else:
                self.logError(f"Type mismatch for '+', got {left_type[1]} and {right_type[1]}.", left_err)

        elif op in ['-', '*', '/', '%']:
            if left_type[1] not in self.numtypes or right_type[1] not in self.numtypes:
                self.logError(f"Type mismatch for '{op}', requires numeric operands.", left_err)
            
            if op == '/':
                if right_val == 0: self.logError("Division by 0.", right_err)
                return (dtype, left_val / right_val, left_err)
            elif op == '%':
                if right_val == 0: self.logError("Modulo by 0.", right_err)
                if left_type[1] == 'elo' or right_type[1] == 'elo':
                    self.logError("Modulo only supports 'frag' (integer).", left_err)
                return (dtype, left_val % right_val, left_err)
            elif op == '-': return (dtype, left_val - right_val, left_err)
            elif op == '*': return (dtype, left_val * right_val, left_err)

        elif op in ['==', '!=', '<', '<=', '>', '>=']:
            if op in ['==', '!=']:
                if left_type[1] != right_type[1]:
                    if not (left_type[1] in self.numtypes and right_type[1] in self.numtypes):
                        self.logError(f"Cannot compare {left_type[1]} with {right_type[1]}.", left_err)
            else:
                if left_type[1] not in self.numtypes or right_type[1] not in self.numtypes:
                    self.logError(f"Relational '{op}' requires numeric types.", left_err)
            return (('lit', 'surebol'), None, left_err)

        elif op in ['&&', '||']:
            if left_type[1] != 'surebol' or right_type[1] != 'surebol':
                self.logError(f"Logical '{op}' requires 'surebol' operands.", left_err)
            return (('lit', 'surebol'), None, left_err)

    def visit_node_pre_un_op(self, node):
        right_type, right_val, right_err = self.visit_node(node.right_n)
        op = node.op_t["tokenName"]
        left_err = ErrorNode(node.op_t["tokenLine"], node.op_t["tokenCol"])

        if right_type[0] == 'arr':
            self.logError("Arrays cannot be used as operands.", right_err)

        if op == '!':
            if right_type[1] != 'surebol':
                self.logError(f"Expected 'surebol' for '!', got {right_type[1]}.", right_err)
            return (('lit', 'surebol'), not right_val, left_err)
        
        elif op in ['-', '+']:
            if right_type[1] not in self.numtypes:
                self.logError(f"Expected numeric type for '{op}', got {right_type[1]}.", right_err)
            return (right_type, -right_val if op == '-' else right_val, left_err)

        elif op in ['++', '--']:
            if not hasattr(node.right_n, 'id_t'):
                self.logError(f"Increment/decrement target must be a variable.", left_err)
            right_sym = self.curr_scope.get(node.right_n.id_t["tokenName"])
            if right_sym and right_sym.get("const"):
                self.logError("Constant symbols cannot be modified.", right_err)
            if right_type[1] not in self.numtypes:
                self.logError(f"Expected numeric variable for '{op}', got {right_type[1]}.", right_err)
            return (right_type, right_val, left_err)

    def visit_node_post_un_op(self, node):
        left_type, left_val, left_err = self.visit_node(node.left_n)
        op = node.op_t["tokenName"]

        if left_type[0] == 'arr':
            self.logError("Arrays cannot be used as operands.", left_err)

        if not hasattr(node.left_n, 'id_t'):
            self.logError(f"Increment/decrement target must be a variable.", left_err)

        left_sym = self.curr_scope.get(node.left_n.id_t["tokenName"])
        if left_sym and left_sym.get("const"):
            self.logError("Constant symbols cannot be modified.", left_err)
            
        if left_type[1] not in self.numtypes:
            self.logError(f"Expected numeric variable for '{op}', got {left_type[1]}.", left_err)
            
        return (left_type, left_val, left_err)

    def visit_node_if_stmt(self, node):
        self.enter_scope("clutch")
        cond = self.visit_node(node.condition_n)
        if cond[0][1] != 'surebol':
            self.logError(f"Condition must be 'surebol', got '{cond[0][1]}'.", cond[2])
        
        self.visit_node(node.body_n)
        self.exit_scope("clutch")

        if node.else_chain_n:
            for elif_stmt in node.else_chain_n:
                self.visit_node(elif_stmt)

        if node.else_stmt_n:
            self.visit_node(node.else_stmt_n)

    def visit_node_else_if_stmt(self, node):
        self.enter_scope("choke_clutch")
        cond = self.visit_node(node.condition_n)
        if cond[0][1] != 'surebol':
            self.logError(f"Condition must be 'surebol', got '{cond[0][1]}'.", cond[2])
        self.visit_node(node.body_n)
        self.exit_scope("choke_clutch")

    def visit_node_else_stmt(self, node):
        self.enter_scope("choke")
        self.visit_node(node.body_n)
        self.exit_scope("choke")

    def visit_node_switch_stmt(self, node):
        self.enter_scope("pick")
        self.switch_depth += 1
        
        switch_type, switch_val, err_n = self.visit_node(node.value_n)
        if switch_type[1] not in ["ign", "frag", "tag"]:
            self.logError("Switch value must be 'ign', 'frag', or 'tag'.", err_n)
        
        case_value_list = []
        for case_stmt in node.cases_n:
            self.enter_scope("role")
            case_type, case_val, c_err_n = self.visit_node(case_stmt.case_value_n)
            
            if case_val in case_value_list:
                self.logError(f"Duplicate switch case '{case_val}'.", c_err_n)
            
            if case_type[1] != switch_type[1]:
                self.logError(f"Case type '{case_type[1]}' does not match switch type '{switch_type[1]}'.", c_err_n)

            case_value_list.append(case_val)
            self.visit_node(case_stmt.body_n, funcExpectedVal=False)
            self.exit_scope("role")

        if node.default_n:
            self.enter_scope("noob")
            self.visit_node(node.default_n.body_n, funcExpectedVal=False)
            self.exit_scope("noob")

        self.switch_depth -= 1
        self.exit_scope("pick")

    def visit_node_loop_stmt(self, node):
        loop_name = node.loop_type 
        self.loop_depth += 1
        self.enter_scope(loop_name)
        
        if node.init_n: 
            if isinstance(node.init_n, list):
                for init_stmt in node.init_n:
                    self.visit_node(init_stmt)
            else:
                self.visit_node(node.init_n)
        
        if node.condition_n:
            cond = self.visit_node(node.condition_n)
            if cond[0][1] != 'surebol':
                self.logError(f"Loop condition must be 'surebol'.", cond[2])

        if node.update_n: self.visit_node(node.update_n, funcExpectedVal=False)
        self.visit_node(node.body_n)

        self.loop_depth -= 1
        self.exit_scope(loop_name)

    def visit_node_break_stmt(self, node):
        err_n = ErrorNode(node.id_t["tokenLine"], node.id_t["tokenCol"], node.id_t["tokenName"])
        if self.loop_depth == 0 and self.switch_depth == 0:
            self.logError("'afk' (break) must be inside a loop or switch.", err_n)

    def visit_node_continue_stmt(self, node):
        err_n = ErrorNode(node.id_t["tokenLine"], node.id_t["tokenCol"], node.id_t["tokenName"])
        if self.loop_depth == 0:
            self.logError("'hop' (continue) must be inside a loop.", err_n)

    def visit_node_return_block(self, node):
            if not self.function_return_stack:
                self.logError("'ggwp' (return) statement outside of a function.", ErrorNode(0,0))
                return

            expected_type = self.function_return_stack[-1]
            
            if node.ret_value_n:
                ret_type, _, val_err = self.visit_node(node.ret_value_n)
                if ret_type[0] == 'arr':
                    self.logError(f"Function '{self.current_function_name}' cannot return an array.", val_err)
                    
                actual_type = ret_type[1]
                if expected_type == 'dodge':
                    self.logError(f"Void ('dodge') function '{self.current_function_name}' cannot return a value.", val_err)
                elif expected_type != actual_type:
                    if not (expected_type == 'elo' and actual_type == 'frag'):
                        self.logError(f"Expected return type '{expected_type}', got '{actual_type}'.", val_err)
            else:
                # No return value provided (e.g., just 'ggwp;')
                if expected_type != "dodge":
                    # ALLOW IMPLICIT RETURN FOR LOBBY
                    if self.current_function_name == "lobby" and expected_type == "frag":
                        pass # 'ggwp;' inside 'lobby' acts implicitly as 'return 0'
                    else:
                        self.logError(f"Function '{self.current_function_name}' expects return type '{expected_type}', but got none.", ErrorNode(0,0))

            self.count_return += 1

    def visit_node_input(self, node):
        for target in node.targets_n:
            self.visit_node(target)
            if not isinstance(target, (node_iden, node_arr_idx)):
                self.logError("Input ('comsat') target must be a variable or array element.")
            if isinstance(target, node_iden):
                sym = self.curr_scope.get(target.id_t["tokenName"])
                if sym: sym["initialized"] = True

    def visit_node_output(self, node):
        for item in node.print_params_n:
            item_type, _, item_err = self.visit_node(item)
            if item_type[0] == 'arr':
                self.logError(f"Cannot directly output ('shout') entire arrays. Access elements instead.", item_err)

    def check_type_and_range(self, dec_type, dtype, val_type, value, id_n=None, index_1D=None, index_2D=None, err_n=None):
        if val_type[0] == 'arr' and dec_type != 'array':
            self.logError(f"Cannot assign entire array to {dec_type}.", err_n)

        # Allow implicit frag -> elo
        if dtype[1] == 'elo' and val_type[1] == 'frag':
            pass
        elif dtype[1] != val_type[1]:
            self.logError(f"Type Mismatch: expected '{dtype[1]}' for {dec_type} but found '{val_type[1]}'.", err_n)

        if dtype[1] == "frag":
            if value is not None and type(value) in [int, float, Decimal] and (value > self.MAX_FRAG or value < self.MIN_FRAG):
                self.logError(f"Value '{value}' is out of 'frag' bounds.", err_n)
        elif dtype[1] == "elo":
            if value is not None and type(value) in [int, float, Decimal] and (value > self.MAX_ELO or value < self.MIN_ELO):
                self.logError(f"Value '{value}' is out of 'elo' bounds.", err_n)

    def check_return_in_body(self, node):
        if node is None: return False
        node_type = type(node).__name__

        if node_type == "node_code_block":
            return any(self.check_return_in_body(stmt) for stmt in node.statements_n)
        if node_type == "node_if_stmt":
            has_if = self.check_return_in_body(node.body_n)
            has_else = False
            
            if node.else_chain_n:
                has_else_ifs = all(self.check_return_in_body(ei) for ei in node.else_chain_n)
            else:
                has_else_ifs = True
            
            if node.else_stmt_n:
                has_else = self.check_return_in_body(node.else_stmt_n)
                
            return has_if and has_else_ifs and has_else
        if node_type == "node_else_if_stmt":
            return self.check_return_in_body(node.body_n)
        if node_type == "node_else_stmt":
            return self.check_return_in_body(node.body_n)
        if node_type == "node_switch_stmt":
            case_returns = all(self.check_return_in_body(case) for case in node.cases_n)
            has_default = node.default_n is not None
            has_return_in_default = self.check_return_in_body(node.default_n) if has_default else False
            return case_returns and has_return_in_default
        if node_type == "node_case_stmt":
            return self.check_return_in_body(node.body_n)
        if node_type == "node_default_stmt":
            return self.check_return_in_body(node.body_n)
        if node_type == "node_return_block":
            self.count_return += 1  
            return True
        return False


# ────────────────────────────────────────────────────────────────────────────────
# PHASE 1: AST BUILDER (Converts Tokens to node_ classes)
# ────────────────────────────────────────────────────────────────────────────────

class ASTBuilder:
    def __init__(self, tokens: List[Token], errors: List[SemanticError]):
        self.tokens = [t for t in tokens if t.type not in (TokenType.whitespace, TokenType.newline, TokenType.comment)]
        self.pos = 0
        self.errors = errors
        self.current_token = self.tokens[self.pos] if self.tokens else Token(TokenType.eof, None, 0, 0)

    def token_to_dict(self, token: Token) -> Dict[str, Any]:
        return {"tokenName": str(token.value), "tokenLine": token.line, "tokenCol": token.column}

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = Token(TokenType.eof, None, self.current_token.line, self.current_token.column)

    def match(self, expected_type: str) -> bool:
        if self.current_token.type == expected_type:
            self.advance()
            return True
        return False

    def expect(self, expected_type: str):
        if self.current_token.type == expected_type:
            token = self.current_token
            self.advance()
            return token
        self.errors.append(SemanticError(f"Ln {self.current_token.line}, Col {self.current_token.column}: Expected '{expected_type}', found '{self.current_token.type}'"))
        raise SemanticError()

    def parse_program(self) -> node_program:
        globals_ = []
        funcs_ = []
        main_ = None

        while self.current_token.type in (TokenType.frag, TokenType.elo, TokenType.ign, TokenType.surebol, TokenType.tag, TokenType.stun, TokenType.build):
            if self.current_token.type == TokenType.build:
                funcs_.append(self.parse_function_dec())
            else:
                if self.current_token.type == TokenType.frag and self.pos + 1 < len(self.tokens) and self.tokens[self.pos+1].type == TokenType.lobby:
                    main_ = self.parse_main_func()
                    break
                else:
                    globals_.extend(self.parse_declarations())
        
        if self.current_token.type != TokenType.eof:
            self.errors.append(SemanticError(f"Ln {self.current_token.line}, Col {self.current_token.column}: Extra input found after program"))
            
        return node_program(globals_, funcs_, main_)

    def parse_declarations(self):
        const_b = False
        if self.match(TokenType.stun):
            const_b = True
        
        dtype_token = self.current_token
        self.advance() 
        
        declarations = []
        
        while True:
            id_token = self.expect(TokenType.identifier)

            if self.current_token.type == TokenType.lbracket:
                self.advance()
                size1 = self.parse_expression()
                self.expect(TokenType.rbracket)
                size2 = None
                if self.match(TokenType.lbracket):
                    size2 = self.parse_expression()
                    self.expect(TokenType.rbracket)

                init_vals = []
                if self.match(TokenType.assign):
                    self.expect(TokenType.lbrace)
                    if self.current_token.type != TokenType.rbrace:
                        if self.current_token.type == TokenType.lbrace:
                            while self.match(TokenType.lbrace):
                                row = []
                                if self.current_token.type != TokenType.rbrace:
                                    row.append(self.parse_expression())
                                    while self.match(TokenType.separator):
                                        row.append(self.parse_expression())
                                self.expect(TokenType.rbrace)
                                init_vals.append(row)
                                self.match(TokenType.separator) 
                        else:
                            init_vals.append(self.parse_expression())
                            while self.match(TokenType.separator):
                                init_vals.append(self.parse_expression())
                    self.expect(TokenType.rbrace)
                
                declarations.append(node_arr_dec(self.token_to_dict(dtype_token), self.token_to_dict(id_token), const_b, size1, size2, init_vals))
            else:
                init_val = None
                if self.match(TokenType.assign):
                    init_val = self.parse_expression()
                declarations.append(node_vardec(self.token_to_dict(dtype_token), self.token_to_dict(id_token), const_b, init_val))
            
            if self.match(TokenType.separator):
                continue
            else:
                break
                
        self.expect(TokenType.terminator)
        return declarations

    def parse_function_dec(self):
        self.expect(TokenType.build)
        dtype_token = self.current_token
        self.advance()
        id_token = self.expect(TokenType.identifier)
        self.expect(TokenType.lparen)

        params = []
        if self.current_token.type != TokenType.rparen:
            p_dt = self.current_token
            self.advance()
            p_id = self.expect(TokenType.identifier)
            params.append(node_funcpar_var(self.token_to_dict(p_dt), self.token_to_dict(p_id)))
            while self.match(TokenType.separator):
                p_dt = self.current_token
                self.advance()
                p_id = self.expect(TokenType.identifier)
                params.append(node_funcpar_var(self.token_to_dict(p_dt), self.token_to_dict(p_id)))
        self.expect(TokenType.rparen)
        self.expect(TokenType.lbrace)
        body = self.parse_code_block()
        self.expect(TokenType.rbrace)
        return node_func_dec(self.token_to_dict(dtype_token), self.token_to_dict(id_token), params, body)

    def parse_main_func(self):
        self.expect(TokenType.frag)
        self.expect(TokenType.lobby)
        self.expect(TokenType.lparen)
        self.expect(TokenType.rparen)
        self.expect(TokenType.lbrace)
        body = self.parse_code_block()
        self.expect(TokenType.rbrace)
        return node_main_func(body)

    def parse_code_block(self):
        stmts = []
        while self.current_token.type not in (TokenType.rbrace, TokenType.eof, TokenType.choke, TokenType.choke_clutch):
            if self.current_token.type in (TokenType.frag, TokenType.elo, TokenType.ign, TokenType.surebol, TokenType.tag, TokenType.stun):
                stmts.extend(self.parse_declarations())
            elif self.current_token.type == TokenType.clutch:
                stmts.append(self.parse_if_stmt())
            elif self.current_token.type == TokenType.grind:
                stmts.append(self.parse_for_loop())
            elif self.current_token.type == TokenType.retry:
                stmts.append(self.parse_while_loop())
            elif self.current_token.type == TokenType.pick:
                stmts.append(self.parse_switch_stmt())
            elif self.current_token.type == TokenType.comsat:
                stmts.append(self.parse_input_stmt())
            elif self.current_token.type == TokenType.shout:
                stmts.append(self.parse_output_stmt())
            elif self.current_token.type == TokenType.afk:
                tok = self.expect(TokenType.afk)
                self.expect(TokenType.terminator)
                stmts.append(node_break_stmt(self.token_to_dict(tok)))
            elif self.current_token.type == TokenType.hop:
                tok = self.expect(TokenType.hop)
                self.expect(TokenType.terminator)
                stmts.append(node_continue_stmt(self.token_to_dict(tok)))
            elif self.current_token.type == TokenType.ggwp:
                self.advance()
                val = None
                if self.current_token.type != TokenType.terminator:
                    val = self.parse_expression()
                self.expect(TokenType.terminator)
                stmts.append(node_return_block(val))
            elif self.current_token.type == TokenType.identifier:
                stmts.append(self.parse_assign_or_call())
            else:
                self.errors.append(SemanticError(f"Ln {self.current_token.line}, Col {self.current_token.column}: Unexpected token {self.current_token.type}"))
                self.advance()
        return node_code_block(stmts)

    def parse_if_stmt(self):
        self.expect(TokenType.clutch)
        self.expect(TokenType.lparen)
        cond = self.parse_expression()
        self.expect(TokenType.rparen)
        self.expect(TokenType.lbrace)
        body = self.parse_code_block()
        self.expect(TokenType.rbrace)

        elifs = []
        while self.match(TokenType.choke_clutch):
            self.expect(TokenType.lparen)
            e_cond = self.parse_expression()
            self.expect(TokenType.rparen)
            self.expect(TokenType.lbrace)
            e_body = self.parse_code_block()
            self.expect(TokenType.rbrace)
            elifs.append(node_else_if_stmt(e_cond, e_body))
        
        else_blk = None
        if self.match(TokenType.choke):
            self.expect(TokenType.lbrace)
            else_blk = node_else_stmt(self.parse_code_block())
            self.expect(TokenType.rbrace)

        return node_if_stmt(cond, body, elifs, else_blk)

    def parse_for_loop(self):
        self.expect(TokenType.grind)
        self.expect(TokenType.lparen)
        init = None
        if self.current_token.type in (TokenType.frag, TokenType.elo, TokenType.ign, TokenType.surebol, TokenType.tag, TokenType.stun):
            init = self.parse_declarations() 
        elif self.current_token.type == TokenType.identifier:
            init = self.parse_assign_or_call() 
        else:
            self.expect(TokenType.terminator)

        cond = None
        if self.current_token.type != TokenType.terminator:
            cond = self.parse_expression()
        self.expect(TokenType.terminator)

        update = None
        if self.current_token.type != TokenType.rparen:
            update = self.parse_expression()
        self.expect(TokenType.rparen)

        self.expect(TokenType.lbrace)
        body = self.parse_code_block()
        self.expect(TokenType.rbrace)

        return node_loop_stmt("grind", init, cond, update, body)

    def parse_while_loop(self):
        self.expect(TokenType.retry)
        self.expect(TokenType.lparen)
        cond = self.parse_expression()
        self.expect(TokenType.rparen)
        self.expect(TokenType.lbrace)
        body = self.parse_code_block()
        self.expect(TokenType.rbrace)
        return node_loop_stmt("retry", None, cond, None, body)

    def parse_switch_stmt(self):
        self.expect(TokenType.pick)
        self.expect(TokenType.lparen)
        val = self.parse_expression()
        self.expect(TokenType.rparen)
        self.expect(TokenType.lbrace)
        
        cases = []
        default_blk = None

        while self.current_token.type in (TokenType.role, TokenType.noob):
            if self.match(TokenType.role):
                c_val = self.parse_expression()
                self.expect(TokenType.colon)
                c_body = self.parse_code_block()
                cases.append(node_case_stmt(c_val, c_body))
            elif self.match(TokenType.noob):
                self.expect(TokenType.colon)
                default_blk = node_default_stmt(self.parse_code_block())

        self.expect(TokenType.rbrace)
        return node_switch_stmt(val, cases, default_blk)

    def parse_input_stmt(self):
        self.expect(TokenType.comsat)
        targets = [self.parse_primary()] 
        while self.match(TokenType.separator):
            targets.append(self.parse_primary())
        self.expect(TokenType.terminator)
        return node_input(targets)

    def parse_output_stmt(self):
        self.expect(TokenType.shout)
        items = [self.parse_expression()]
        while self.match(TokenType.separator):
            items.append(self.parse_expression())
        self.expect(TokenType.terminator)
        return node_output(items)

    def parse_assign_or_call(self):
        id_token = self.current_token
        self.advance()

        if self.match(TokenType.dot):
            m_tok = self.current_token
            self.advance()
            self.expect(TokenType.lparen)
            args = []
            if self.current_token.type != TokenType.rparen:
                args.append(self.parse_expression())
                while self.match(TokenType.separator):
                    args.append(self.parse_expression())
            self.expect(TokenType.rparen)
            self.expect(TokenType.terminator)
            return node_method_call(self.token_to_dict(id_token), self.token_to_dict(m_tok), args)

        if self.match(TokenType.lparen):
            args = []
            if self.current_token.type != TokenType.rparen:
                args.append(self.parse_expression())
                while self.match(TokenType.separator):
                    args.append(self.parse_expression())
            self.expect(TokenType.rparen)
            self.expect(TokenType.terminator)
            return node_func_call(self.token_to_dict(id_token), args)

        if self.current_token.type == TokenType.lbracket:
            self.advance()
            idx1 = self.parse_expression()
            self.expect(TokenType.rbracket)
            idx2 = None
            if self.match(TokenType.lbracket):
                idx2 = self.parse_expression()
                self.expect(TokenType.rbracket)
            
            if self.current_token.type in (TokenType.increment, TokenType.decrement):
                op = self.current_token
                self.advance()
                self.expect(TokenType.terminator)
                return node_post_un_op(node_arr_idx(self.token_to_dict(id_token), idx1, idx2), self.token_to_dict(op))
            
            op = self.current_token
            self.advance()
            val = self.parse_expression()
            self.expect(TokenType.terminator)
            return node_arr_assign_stmt(node_arr_idx(self.token_to_dict(id_token), idx1, idx2), self.token_to_dict(op), val)

        if self.current_token.type in (TokenType.increment, TokenType.decrement):
            op = self.current_token
            self.advance()
            self.expect(TokenType.terminator)
            return node_post_un_op(node_iden(self.token_to_dict(id_token)), self.token_to_dict(op))

        op = self.current_token
        self.advance()
        val = self.parse_expression()
        self.expect(TokenType.terminator)
        return node_assign_stmt(self.token_to_dict(id_token), self.token_to_dict(op), val)

    def parse_expression(self):
        return self.parse_logic_or()

    def parse_logic_or(self):
        node = self.parse_logic_and()
        while self.current_token.type == TokenType.or_:
            op = self.current_token
            self.advance()
            node = node_bi_op(node, self.token_to_dict(op), self.parse_logic_and())
        return node

    def parse_logic_and(self):
        node = self.parse_equality()
        while self.current_token.type == TokenType.and_:
            op = self.current_token
            self.advance()
            node = node_bi_op(node, self.token_to_dict(op), self.parse_equality())
        return node

    def parse_equality(self):
        node = self.parse_relational()
        while self.current_token.type in (TokenType.eq, TokenType.neq):
            op = self.current_token
            self.advance()
            node = node_bi_op(node, self.token_to_dict(op), self.parse_relational())
        return node

    def parse_relational(self):
        node = self.parse_additive()
        while self.current_token.type in (TokenType.lt, TokenType.gt, TokenType.lte, TokenType.gte):
            op = self.current_token
            self.advance()
            node = node_bi_op(node, self.token_to_dict(op), self.parse_additive())
        return node

    def parse_additive(self):
        node = self.parse_multiplicative()
        while self.current_token.type in (TokenType.plus, TokenType.minus):
            op = self.current_token
            self.advance()
            node = node_bi_op(node, self.token_to_dict(op), self.parse_multiplicative())
        return node

    def parse_multiplicative(self):
        node = self.parse_unary()
        while self.current_token.type in (TokenType.mul, TokenType.div, TokenType.mod):
            op = self.current_token
            self.advance()
            node = node_bi_op(node, self.token_to_dict(op), self.parse_unary())
        return node

    def parse_unary(self):
        if self.current_token.type in (TokenType.plus, TokenType.minus, TokenType.not_, TokenType.increment, TokenType.decrement):
            op = self.current_token
            self.advance()
            return node_pre_un_op(self.token_to_dict(op), self.parse_unary())
        return self.parse_postfix()

    def parse_postfix(self):
        node = self.parse_primary()
        if self.current_token.type in (TokenType.increment, TokenType.decrement):
            op = self.current_token
            self.advance()
            return node_post_un_op(node, self.token_to_dict(op))
        return node

    def parse_primary(self):
        tok = self.current_token
        if self.match(TokenType.integer):
            return node_num(self.token_to_dict(tok), "frag")
        if self.match(TokenType.float):
            return node_num(self.token_to_dict(tok), "elo")
        if self.match(TokenType.string):
            return node_str(self.token_to_dict(tok))
        if self.match(TokenType.char):
            return node_char(self.token_to_dict(tok))
        if self.match(TokenType.buff) or self.match(TokenType.nerf):
            return node_bool(self.token_to_dict(tok))
        
        if self.match(TokenType.identifier):
            if self.match(TokenType.lparen):
                args = []
                if self.current_token.type != TokenType.rparen:
                    args.append(self.parse_expression())
                    while self.match(TokenType.separator):
                        args.append(self.parse_expression())
                self.expect(TokenType.rparen)
                return node_func_call(self.token_to_dict(tok), args)
            
            if self.match(TokenType.lbracket):
                idx1 = self.parse_expression()
                self.expect(TokenType.rbracket)
                idx2 = None
                if self.match(TokenType.lbracket):
                    idx2 = self.parse_expression()
                    self.expect(TokenType.rbracket)
                return node_arr_idx(self.token_to_dict(tok), idx1, idx2)
                
            if self.match(TokenType.dot):
                m_tok = self.current_token
                self.advance()
                self.expect(TokenType.lparen)
                args = []
                if self.current_token.type != TokenType.rparen:
                    args.append(self.parse_expression())
                    while self.match(TokenType.separator):
                        args.append(self.parse_expression())
                self.expect(TokenType.rparen)
                return node_method_call(self.token_to_dict(tok), self.token_to_dict(m_tok), args)

            return node_iden(self.token_to_dict(tok))

        if self.match(TokenType.lparen):
            expr = self.parse_expression()
            self.expect(TokenType.rparen)
            return expr
            
        self.errors.append(SemanticError(f"Ln {tok.line}, Col {tok.column}: Unexpected token in expression: {tok.type}"))
        raise SemanticError()

# ────────────────────────────────────────────────────────────────────────────────
# MAIN INTEGRATION EXPORT
# ────────────────────────────────────────────────────────────────────────────────

def analyze_semantics(tokens: List[Token]) -> Tuple[bool, str]:
    """
    Main entry point for semantic analysis.
    Consumes tokens, builds an AST, enforces GGScript rules, and returns results.
    """
    errors: List[SemanticError] = []
    
    # 1. Parse tokens into an Abstract Syntax Tree (AST) using the provided GGScript grammer classes
    builder = ASTBuilder(tokens, errors)
    try:
        ast = builder.parse_program()
    except SemanticError:
        return False, "\n".join(str(e) for e in errors)
    
    # 2. Visit AST to enforce detailed semantic rules (types, scopes, definitions)
    visitor = SemanticAnalyzer()
    visitor_errors = visitor.interpret(ast)
    
    if visitor.errors:
        return False, "\n".join(visitor.errors)
    
    return True, "Semantic analysis successful ✓ No errors."