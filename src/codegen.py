import builtins

class CodeGen:
    def __init__(self):
        self.generated_code = ""
        self.indent_level = 0
        self.global_vars = set()
        self.current_function = None
        
        # GGScript to Python default values mapping
        self.type_defaults = {
            'frag': '0',       # int
            'elo': '0.0',      # float
            'ign': '""',       # string
            'tag': "''",       # char
            'surebol': 'False' # boolean
        }

    def indent(self):
        return "    " * self.indent_level

    def get_runtime_environment(self):
        """Injects GGScript built-in classes (like arrays) into the Python execution space"""
        return """
class GGScriptArray:
    def __init__(self, dtype, dims=1, initial_values=None):
        self.dtype = dtype
        self.dims = dims
        self.default = {'frag': 0, 'elo': 0.0, 'ign': "", 'tag': '', 'surebol': False}.get(dtype, None)
        
        self.data = []
        if dims == 1:
            if initial_values is not None:
                for val in initial_values:
                    if dtype == 'frag': self.data.append(int(val))
                    elif dtype == 'elo': self.data.append(float(val))
                    elif dtype == 'surebol': self.data.append(bool(val))
                    else: self.data.append(str(val))
        elif dims == 2:
            if initial_values is not None:
                for row in initial_values:
                    new_row = []
                    for val in row:
                        if dtype == 'frag': new_row.append(int(val))
                        elif dtype == 'elo': new_row.append(float(val))
                        elif dtype == 'surebol': new_row.append(bool(val))
                        else: new_row.append(str(val))
                    self.data.append(new_row)

    def append(self, val):
        if self.dtype == 'frag': val = int(val)
        elif self.dtype == 'elo': val = float(val)
        elif self.dtype == 'surebol': val = bool(val)
        self.data.append(val)

    def pop(self):
        return self.data.pop() if self.data else self.default

    def insert(self, idx, val):
        if self.dtype == 'frag': val = int(val)
        elif self.dtype == 'elo': val = float(val)
        elif self.dtype == 'surebol': val = bool(val)
        self.data.insert(idx, val)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        if isinstance(index, tuple):   
            row, col = index
            if row >= len(self.data) or col >= len(self.data[row]): return self.default
            return self.data[row][col]
        else: 
            if index >= len(self.data): return self.default
            return self.data[index]
    
    def __setitem__(self, index, value):
        if isinstance(index, tuple): 
            row, col = index
            while row >= len(self.data): self.data.append([])
            while col >= len(self.data[row]): self.data[row].append(self.default)
            if self.dtype == 'frag': self.data[row][col] = int(value)
            elif self.dtype == 'elo': self.data[row][col] = float(value)
            else: self.data[row][col] = value
        else: 
            while index >= len(self.data): self.data.append(self.default)
            if self.dtype == 'frag': self.data[index] = int(value)
            elif self.dtype == 'elo': self.data[index] = float(value)
            else: self.data[index] = value
    
    def __repr__(self):
        return str(self.data)
"""

    def compile(self, ast_node) -> tuple[bool, str]:
        """Main entry point called by the IDE pipeline."""
        try:
            # Setup imports and Runtime Env
            self.generated_code = "import math\n\n"
            self.generated_code += self.get_runtime_environment()
            self.generated_code += "\n# --- COMPILED GGSCRIPT ---\n\n"
            
            # Start AST Traversal
            self.visit(ast_node)
            
            # Direct Execution Trigger (Bypassing __main__ isolation for IDE exec threads)
            self.generated_code += "\nif 'lobby' in locals() or 'lobby' in globals():\n"
            self.generated_code += "    lobby()\n"
            
            return True, self.generated_code
        except Exception as e:
            import traceback
            return False, f"Code Generation Failed: {str(e)}\n{traceback.format_exc()}"

    def visit(self, node):
        """Recursively visits AST nodes and dispatches to specific visit_ methods."""
        if node is None:
            return ""
        
        if isinstance(node, list):
            res = []
            for n in node:
                res.append(self.visit(n))
            return "".join(filter(None, res))
        
        node_type = type(node).__name__
        visit_method = getattr(self, f"visit_{node_type}", self.generic_visit)
        return visit_method(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"No visit method implemented for AST node: {type(node).__name__}")

    # ==========================================
    # CORE STRUCTURES
    # ==========================================
    def visit_node_program(self, node):
        for glob in node.globals_n:
            if hasattr(glob, 'id_t'):
                self.global_vars.add(glob.id_t["tokenName"])
            self.visit(glob)
            
        for func in node.funcs_n:
            self.visit(func)
            
        if node.main_n:
            self.visit(node.main_n)
        return ""

    def visit_node_main_func(self, node):
        self.current_function = "lobby"
        self.generated_code += f"{self.indent()}def lobby():\n"
        self.indent_level += 1
        
        # FIX: Explicitly bind the IDE terminal commands to the global scope to prevent Thread execution NameErrors
        self.generated_code += f"{self.indent()}global console_disp, console_insp\n"
        
        if self.global_vars:
            safe_globals = [f"_{g}" if g in dir(builtins) else g for g in self.global_vars]
            self.generated_code += f"{self.indent()}global {', '.join(safe_globals)}\n"
            
        if not node.body_n.statements_n:
            self.generated_code += f"{self.indent()}pass\n"
        else:
            self.visit(node.body_n)
            
        self.indent_level -= 1
        self.generated_code += "\n"
        self.current_function = None
        return ""

    def visit_node_code_block(self, node):
        for stmt in node.statements_n:
            self.visit(stmt)
        return ""

    def visit_node_func_dec(self, node):
        func_name = node.id_t["tokenName"]
        if func_name in dir(builtins): func_name = f"_{func_name}"
        self.current_function = func_name
        
        params = []
        if node.params_n:
            for p in node.params_n:
                p_name = p.id_t["tokenName"]
                if p_name in dir(builtins): p_name = f"_{p_name}"
                params.append(p_name)
                
        self.generated_code += f"{self.indent()}def {func_name}({', '.join(params)}):\n"
        self.indent_level += 1
        
        # FIX: Explicitly bind the IDE terminal commands to the global scope
        self.generated_code += f"{self.indent()}global console_disp, console_insp\n"
        
        if self.global_vars:
            safe_globals = [f"_{g}" if g in dir(builtins) else g for g in self.global_vars]
            self.generated_code += f"{self.indent()}global {', '.join(safe_globals)}\n"
            
        if not node.body_n.statements_n:
            self.generated_code += f"{self.indent()}pass\n"
        else:
            self.visit(node.body_n)
            
        self.indent_level -= 1
        self.generated_code += "\n"
        self.current_function = None
        return ""

    # ==========================================
    # DECLARATIONS & ASSIGNMENTS
    # ==========================================
    def visit_node_vardec(self, node):
        var_name = node.id_t["tokenName"]
        if var_name in dir(builtins): var_name = f"_{var_name}"
        var_type = node.dtype_t["tokenName"]
        
        if node.init_value_n:
            val = self.visit(node.init_value_n)
            if var_type == 'frag': val = f"int({val})"
            elif var_type == 'elo': val = f"float({val})"
            elif var_type == 'surebol': val = f"bool({val})"
            self.generated_code += f"{self.indent()}{var_name} = {val}\n"
        else:
            default_val = self.type_defaults.get(var_type, 'None')
            self.generated_code += f"{self.indent()}{var_name} = {default_val}\n"
        return ""

    def visit_node_arr_dec(self, node):
        var_name = node.id_t["tokenName"]
        if var_name in dir(builtins): var_name = f"_{var_name}"
        var_type = node.dtype_t["tokenName"]
        dims = len(node.sizes_n)
        
        if node.init_values_n:
            def build_init_list(vals):
                if not vals: return "[]"
                if isinstance(vals[0], list):
                    return "[" + ", ".join(build_init_list(v) for v in vals) + "]"
                else:
                    return "[" + ", ".join(str(self.visit(v)) for v in vals) + "]"
            init_str = build_init_list(node.init_values_n)
            self.generated_code += f"{self.indent()}{var_name} = GGScriptArray('{var_type}', {dims}, {init_str})\n"
        else:
            self.generated_code += f"{self.indent()}{var_name} = GGScriptArray('{var_type}', {dims})\n"
        return ""

    def visit_node_assign_stmt(self, node):
        var_name = node.id_t["tokenName"]
        if var_name in dir(builtins): var_name = f"_{var_name}"
        op = node.op_t["tokenName"]
        val = self.visit(node.value_n)
        self.generated_code += f"{self.indent()}{var_name} {op} {val}\n"
        return ""

    def visit_node_arr_assign_stmt(self, node):
        var_name = node.arr_idx_n.id_t["tokenName"]
        if var_name in dir(builtins): var_name = f"_{var_name}"
        op = node.op_t["tokenName"]
        val = self.visit(node.value_n)
        
        indices = [str(self.visit(idx)) for idx in node.arr_idx_n.indices_n]
        idx_str = f"[{indices[0]}]" if len(indices) == 1 else f"[{', '.join(indices)}]"
            
        self.generated_code += f"{self.indent()}{var_name}{idx_str} {op} {val}\n"
        return ""

    # ==========================================
    # I/O STATEMENTS
    # ==========================================
    def visit_node_input(self, node):
        for target in node.targets_n:
            if type(target).__name__ == "node_iden":
                var_name = target.id_t["tokenName"]
                safe_name = f"_{var_name}" if var_name in dir(builtins) else var_name
                self.generated_code += f"{self.indent()}{safe_name} = console_insp('{var_name}')\n"
            elif type(target).__name__ == "node_arr_idx":
                var_name = target.id_t["tokenName"]
                safe_name = f"_{var_name}" if var_name in dir(builtins) else var_name
                indices = [str(self.visit(idx)) for idx in target.indices_n]
                idx_str = f"[{', '.join(indices)}]" if len(indices) > 1 else f"[{indices[0]}]"
                self.generated_code += f"{self.indent()}{safe_name}{idx_str} = console_insp('{var_name}{idx_str}')\n"
        return ""

    def visit_node_output(self, node):
        parts = []
        for item in node.print_params_n:
            parts.append(str(self.visit(item)))
            
        joined_args = ", ".join(parts)
        self.generated_code += f"{self.indent()}console_disp({joined_args})\n"
        return ""

    # ==========================================
    # CONTROL FLOW
    # ==========================================
    def visit_node_if_stmt(self, node):
        cond = self.visit(node.condition_n)
        self.generated_code += f"{self.indent()}if {cond}:\n"
        
        self.indent_level += 1
        if not node.body_n.statements_n: self.generated_code += f"{self.indent()}pass\n"
        else: self.visit(node.body_n)
        self.indent_level -= 1
        
        if node.else_chain_n:
            for elif_stmt in node.else_chain_n:
                self.visit(elif_stmt)
                
        if node.else_stmt_n:
            self.visit(node.else_stmt_n)
        return ""

    def visit_node_else_if_stmt(self, node):
        cond = self.visit(node.condition_n)
        self.generated_code += f"{self.indent()}elif {cond}:\n"
        
        self.indent_level += 1
        if not node.body_n.statements_n: self.generated_code += f"{self.indent()}pass\n"
        else: self.visit(node.body_n)
        self.indent_level -= 1
        return ""

    def visit_node_else_stmt(self, node):
        self.generated_code += f"{self.indent()}else:\n"
        
        self.indent_level += 1
        if not node.body_n.statements_n: self.generated_code += f"{self.indent()}pass\n"
        else: self.visit(node.body_n)
        self.indent_level -= 1
        return ""

    def visit_node_switch_stmt(self, node):
        val = self.visit(node.value_n)
        self.generated_code += f"{self.indent()}match {val}:\n"
        self.indent_level += 1
        
        for case_stmt in node.cases_n:
            self.visit(case_stmt)
            
        if node.default_n:
            self.visit(node.default_n)
            
        self.indent_level -= 1
        return ""

    def visit_node_case_stmt(self, node):
        val = self.visit(node.case_value_n)
        self.generated_code += f"{self.indent()}case {val}:\n"
        self.indent_level += 1
        if not node.body_n.statements_n: self.generated_code += f"{self.indent()}pass\n"
        else: self.visit(node.body_n)
        self.indent_level -= 1
        return ""

    def visit_node_default_stmt(self, node):
        self.generated_code += f"{self.indent()}case _:\n"
        self.indent_level += 1
        if not node.body_n.statements_n: self.generated_code += f"{self.indent()}pass\n"
        else: self.visit(node.body_n)
        self.indent_level -= 1
        return ""

    def visit_node_loop_stmt(self, node):
        if node.loop_type == "grind":
            if node.init_n:
                if isinstance(node.init_n, list):
                    for init in node.init_n: self.visit(init)
                else:
                    self.visit(node.init_n)
                    
            cond = self.visit(node.condition_n) if node.condition_n else "True"
            self.generated_code += f"{self.indent()}while {cond}:\n"
            
            self.indent_level += 1
            if not node.body_n.statements_n:
                if node.update_n:
                    self.visit(node.update_n) 
                else:
                    self.generated_code += f"{self.indent()}pass\n"
            else: 
                self.visit(node.body_n)
                if node.update_n:
                    self.visit(node.update_n) 
            self.indent_level -= 1

        elif node.loop_type == "retry":
            cond = self.visit(node.condition_n)
            self.generated_code += f"{self.indent()}while {cond}:\n"
            self.indent_level += 1
            if not node.body_n.statements_n: self.generated_code += f"{self.indent()}pass\n"
            else: self.visit(node.body_n)
            self.indent_level -= 1

        elif node.loop_type == "try":
            self.generated_code += f"{self.indent()}while True:\n"
            self.indent_level += 1
            if not node.body_n.statements_n: self.generated_code += f"{self.indent()}pass\n"
            else: self.visit(node.body_n)
            
            cond = self.visit(node.condition_n)
            self.generated_code += f"{self.indent()}if not ({cond}):\n"
            self.generated_code += f"{self.indent()}    break\n"
            self.indent_level -= 1
        return ""

    # ==========================================
    # EXPRESSIONS, METHOD CALLS, & OPERATORS
    # ==========================================
    def visit_node_func_call(self, node):
        func_name = node.id_t["tokenName"]
        if func_name in dir(builtins): func_name = f"_{func_name}"
        args = [str(self.visit(arg)) for arg in node.args_n]
        return f"{func_name}({', '.join(args)})"

    def visit_node_method_call(self, node):
        var_name = node.id_t["tokenName"]
        if var_name in dir(builtins): var_name = f"_{var_name}"
        method_name = node.method_t["tokenName"]
        args = [str(self.visit(arg)) for arg in node.args_n]
        
        # Translate native GGScript Array and String Methods natively to python logic
        if method_name == "stack":
            self.generated_code += f"{self.indent()}{var_name}.append({', '.join(args)})\n"
            return ""
        elif method_name == "drop":
            return f"{var_name}.pop()"
        elif method_name == "craft":
            self.generated_code += f"{self.indent()}{var_name}.insert({args[0]}, {args[1]})\n"
            return ""
        elif method_name == "count":
            return f"len({var_name})"
        elif method_name == "split":
            return f"{var_name}.split({', '.join(args)})"
            
        return f"{var_name}.{method_name}({', '.join(args)})"

    def visit_node_bi_op(self, node):
        left = self.visit(node.left_n)
        op = node.op_t["tokenName"]
        right = self.visit(node.right_n)
        if op == '&&': op = 'and'
        elif op == '||': op = 'or'
        return f"({left} {op} {right})"

    def visit_node_pre_un_op(self, node):
        op = node.op_t["tokenName"]
        right = self.visit(node.right_n)
        if op == '!': return f"(not {right})"
        elif op == '++':
            self.generated_code += f"{self.indent()}{right} += 1\n"
            return right
        elif op == '--':
            self.generated_code += f"{self.indent()}{right} -= 1\n"
            return right
        return f"({op}{right})"

    def visit_node_post_un_op(self, node):
        left = self.visit(node.left_n)
        op = node.op_t["tokenName"]
        if op == '++':
            self.generated_code += f"{self.indent()}{left} += 1\n"
        elif op == '--':
            self.generated_code += f"{self.indent()}{left} -= 1\n"
        return left

    def visit_node_iden(self, node):
        var_name = node.id_t["tokenName"]
        if var_name in dir(builtins): var_name = f"_{var_name}"
        return var_name

    def visit_node_arr_idx(self, node):
        var_name = node.id_t["tokenName"]
        if var_name in dir(builtins): var_name = f"_{var_name}"
        indices = [str(self.visit(idx)) for idx in node.indices_n]
        if len(indices) == 1: return f"{var_name}[{indices[0]}]"
        return f"{var_name}[{indices[0]}, {indices[1]}]"

    def visit_node_num(self, node):
        return node.val_t["tokenName"]

    def visit_node_str(self, node):
        val = node.val_t["tokenName"]
        if not val.startswith('"'): val = f'"{val}"'
        return val

    def visit_node_char(self, node):
        val = node.val_t["tokenName"]
        if not val.startswith("'"): val = f"'{val}'"
        return val

    def visit_node_bool(self, node):
        val = node.val_t["tokenName"]
        if val == "buff": return "True"
        if val == "nerf": return "False"
        return "False"

    # ==========================================
    # JUMP STATEMENTS
    # ==========================================
    def visit_node_break_stmt(self, node):
        self.generated_code += f"{self.indent()}break\n"
        return ""

    def visit_node_continue_stmt(self, node):
        self.generated_code += f"{self.indent()}continue\n"
        return ""

    def visit_node_return_block(self, node):
        if node.ret_value_n:
            val = self.visit(node.ret_value_n)
            self.generated_code += f"{self.indent()}return {val}\n"
        else:
            self.generated_code += f"{self.indent()}return\n"
        return ""