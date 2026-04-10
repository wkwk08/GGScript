from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
import re
import builtins

# ── COMPILER MODULE IMPORTS ──
from src.lexer import Lexer
from src.parser import analyze_syntax
from src.semantic import analyze_semantics, ASTBuilder
from src.codegen import CodeGen

app = Flask(__name__)

# ==========================================
# 🔒 SECURITY LAYERS
# ==========================================
# 1. Limit incoming requests to 1 Megabyte to prevent server crashes
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 

# 2. Only allow your specific Vercel URL and local testing URLs
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://ggscript-ide.vercel.app", 
            "http://127.0.0.1:5000",
            "http://localhost:5000"
        ]
    }
})
# ==========================================

# ── 1. EXACT TOKEN CATEGORY HELPER FROM MAIN.PY ──
def get_token_category(raw_type: str) -> str:
    KEYWORDS = {'afk', 'buff', 'build', 'choke', 'choke_clutch', 'clutch', 'comsat', 'count', 'craft', 'dodge', 'drop', 'elo', 'frag', 'ggwp', 'grind', 'hop', 'ign', 'lobby', 'nerf', 'noob', 'pick', 'retry', 'role', 'shout', 'split', 'stack', 'stun', 'surebol', 'tag', 'try'}
    raw_lower = raw_type.lower()
    if raw_lower in KEYWORDS: return "KEYWORD"
    if raw_lower == "identifier": return "IDENTIFIER"
    if raw_lower in ("integer", "int"): return "INTEGER LITERAL"
    if raw_lower in ("float", "double"): return "FLOAT LITERAL"
    if raw_lower == "string": return "STRING LITERAL"
    if raw_lower == "char": return "CHAR LITERAL"
    if raw_lower == "comment": return "COMMENT"
    OPERATORS = {'+', '-', '*', '/', '%', '=', '+=', '-=', '*=', '/=', '%=', '++', '--', '<', '>', '<=', '>=', '==', '!=', '!', '&&', '||'}
    if raw_lower in OPERATORS: return "OPERATOR"
    if raw_lower == "terminator": return "TERMINATOR"
    if raw_lower in ("separator", ":", "."): return "SEPARATOR"
    if raw_lower in ("(", ")", "{", "}", "[", "]"): return "BRACKET"
    return "OTHER"

def format_tokens(tokens):
    formatted = []
    for t in tokens:
        if t.type in ["eof", "newline", "whitespace"]: continue
        raw_type_str = str(t.type)
        if raw_type_str.startswith("TokenType."):
            raw_type_str = raw_type_str.split('.')[-1]
        lexeme = str(t.value).replace("\n", "\\n").replace("\t", "\\t")
        token_display = lexeme if raw_type_str.lower() in ["comment", "terminator", "separator", "lparen", "rparen", "lbrace", "rbrace", "lbracket", "rbracket"] else raw_type_str
        if raw_type_str.lower() == "choke_clutch": token_display = "choke clutch"
        formatted.append({"lexeme": lexeme, "token": token_display, "type": get_token_category(raw_type_str)})
    return formatted

# ── 2. EXACT ERROR BOX FORMATTER FROM MAIN.PY ──
def print_error_box(error_str, code_text):
    match = re.search(r'Ln (\d+), Col (\d+)', error_str)
    if not match: return error_str
    
    ln = int(match.group(1))
    col = int(match.group(2))
    cleaned_text = code_text.rstrip('\n\r\t ')
    lines = cleaned_text.split('\n') if cleaned_text else [""]
    
    if ln > len(lines):
        ln = len(lines)
        col = len(lines[-1]) + 2 if lines else 1
        
    if 1 <= ln <= len(lines):
        line_str = lines[ln - 1].rstrip('\n\r')
        expanded_line = ""
        pointer_col = 0
        for i in range(col - 1):
            if i < len(line_str) and line_str[i] == '\t':
                expanded_line += "    "
                pointer_col += 4
            else:
                if i < len(line_str): expanded_line += line_str[i]
                pointer_col += 1
        if col - 1 < len(line_str): expanded_line += line_str[col-1:]
        pointer_spaces = " " * pointer_col
        
        err_out = f"{error_str}\n\n"
        err_out += f" ▌ {ln:02d} | {expanded_line}\n"
        err_out += f" ▌      {pointer_spaces}^\n"
        return err_out
    return error_str

# ── 3. ASYNC CODE GENERATOR OVERRIDE FOR WEB TERMINAL ──
class WebAsyncCodeGen(CodeGen):
    def visit_node_main_func(self, node):
        self.current_function = "lobby"
        self.generated_code += f"{self.indent()}async def lobby():\n"
        self.indent_level += 1
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

    def visit_node_func_dec(self, node):
        func_name = node.id_t["tokenName"]
        if func_name in dir(builtins): func_name = f"_{func_name}"
        self.current_function = func_name
        params = [p.id_t["tokenName"] for p in node.params_n] if node.params_n else []
        params = [f"_{p}" if p in dir(builtins) else p for p in params]
        
        self.generated_code += f"{self.indent()}async def {func_name}({', '.join(params)}):\n"
        self.indent_level += 1
        self.generated_code += f"{self.indent()}global console_disp, console_insp\n"
        if self.global_vars:
            safe_globals = [f"_{g}" if g in dir(builtins) else g for g in self.global_vars]
            self.generated_code += f"{self.indent()}global {', '.join(safe_globals)}\n"
            
        if not node.body_n.statements_n: self.generated_code += f"{self.indent()}pass\n"
        else: self.visit(node.body_n)
        
        self.indent_level -= 1
        self.generated_code += "\n"
        self.current_function = None
        return ""

    def visit_node_input(self, node):
        for target in node.targets_n:
            if type(target).__name__ == "node_iden":
                var_name = target.id_t["tokenName"]
                safe_name = f"_{var_name}" if var_name in dir(builtins) else var_name
                self.generated_code += f"{self.indent()}{safe_name} = await console_insp('{var_name}')\n"
            elif type(target).__name__ == "node_arr_idx":
                var_name = target.id_t["tokenName"]
                safe_name = f"_{var_name}" if var_name in dir(builtins) else var_name
                indices = [str(self.visit(idx)) for idx in target.indices_n]
                idx_str = f"[{', '.join(indices)}]" if len(indices) > 1 else f"[{indices[0]}]"
                self.generated_code += f"{self.indent()}{safe_name}{idx_str} = await console_insp('{var_name}{idx_str}')\n"
        return ""

    def visit_node_func_call(self, node):
        func_name = node.id_t["tokenName"]
        if func_name in dir(builtins): func_name = f"_{func_name}"
        args = [str(self.visit(arg)) for arg in node.args_n]
        return f"(await {func_name}({', '.join(args)}))"

    def compile(self, ast_node) -> tuple[bool, str]:
        try:
            self.generated_code = "import math\nimport asyncio\n\n"
            self.generated_code += self.get_runtime_environment()
            self.generated_code += "\n# --- COMPILED GGSCRIPT ---\n\n"
            self.visit(ast_node)
            return True, self.generated_code
        except Exception as e:
            return False, f"Code Generation Failed: {str(e)}\n{traceback.format_exc()}"

# ── 4. THE COMPILER PIPELINE ──
@app.route('/api/compile', methods=['POST'])
def compile_code():
    data = request.get_json()
    code = data.get('code', '')
    action = data.get('action', 'run')

    try:
        tokens, errors = Lexer(code).make_tokens()
        token_data = format_tokens(tokens)
        
        if errors:
            err_strs = [print_error_box(e.as_string() if hasattr(e, 'as_string') else str(e), code) for e in errors]
            return jsonify({"success": False, "stage": "Lexical", "errors": err_strs, "tokens": token_data})
        if action == 'lexical':
            return jsonify({"success": True, "stage": "Lexical", "message": "Lexical analysis successful ✓ No errors.", "tokens": token_data})

        syn_ok, syn_msg = analyze_syntax(tokens)
        if not syn_ok:
            return jsonify({"success": False, "stage": "Syntax", "errors": [print_error_box(syn_msg, code)], "tokens": token_data})
        if action == 'syntax':
            return jsonify({"success": True, "stage": "Syntax", "message": syn_msg, "tokens": token_data})

        sem_ok, sem_msg = analyze_semantics(tokens)
        if not sem_ok:
            errors_list = [print_error_box(e.strip(), code) for e in sem_msg.split('\n') if e.strip()]
            return jsonify({"success": False, "stage": "Semantic", "errors": errors_list, "tokens": token_data})
        if action == 'semantic':
            return jsonify({"success": True, "stage": "Semantic", "message": sem_msg, "tokens": token_data})

        ast_errors = []
        ast = ASTBuilder(tokens, ast_errors).parse_program()
        if ast_errors:
            return jsonify({"success": False, "stage": "AST Building", "errors": [print_error_box(str(e), code) for e in ast_errors], "tokens": token_data})

        cg = WebAsyncCodeGen()
        success, py_code = cg.compile(ast)
        if not success:
            return jsonify({"success": False, "stage": "Code Generation", "errors": [py_code], "tokens": token_data})

        return jsonify({"success": True, "stage": "Run", "python_code": py_code, "tokens": token_data})

    except Exception as e:
        # SECURITY LAYER 3: Hides server paths from the user but logs them for you
        print(f"CRITICAL CRASH: {traceback.format_exc()}")
        return jsonify({"success": False, "stage": "Pipeline Crash", "errors": [f"Internal Compiler Error: {str(e)}"], "tokens": []})

if __name__ == '__main__':
    app.run(debug=True, port=5000)