import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import platform
import os
import re
import threading
import builtins
import traceback

# ── COMPILER MODULE IMPORTS ──
from src.lexer import Lexer
from src.token_types import TokenType
from src.parser import analyze_syntax
from src.semantic import analyze_semantics, ASTBuilder

# ── TOKEN CATEGORY HELPER ──
def get_token_category(raw_type: str) -> str:
    KEYWORDS = {
        'afk', 'buff', 'build', 'choke', 'choke_clutch', 'clutch', 'comsat',
        'count', 'craft', 'dodge', 'drop', 'elo', 'frag', 'ggwp', 'grind',
        'hop', 'ign', 'lobby', 'nerf', 'noob', 'pick', 'retry', 'role',
        'shout', 'split', 'stack', 'stun', 'surebol', 'tag', 'try'
    }
    raw_lower = raw_type.lower()
    if raw_lower in KEYWORDS: return "KEYWORD"
    if raw_lower == "identifier": return "IDENTIFIER"
    if raw_lower in ("integer", "int"): return "INTEGER LITERAL"
    if raw_lower in ("float", "double"): return "FLOAT LITERAL"
    if raw_lower == "string": return "STRING LITERAL"
    if raw_lower == "char": return "CHAR LITERAL"
    if raw_lower == "comment": return "COMMENT"
    
    OPERATORS = {
        '+', '-', '*', '/', '%', '=', '+=', '-=', '*=', '/=', '%=',
        '++', '--', '<', '>', '<=', '>=', '==', '!=', '!', '&&', '||'
    }
    if raw_lower in OPERATORS: return "OPERATOR"
    if raw_lower == "terminator": return "TERMINATOR"
    if raw_lower in ("separator", ":"): return "SEPARATOR"
    if raw_lower in ("(", ")", "{", "}", "[", "]"): return "BRACKET"
    
    return "OTHER"


# ============================================================================
# MAIN IDE CLASS
# ============================================================================
class GGScriptIDE:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GGScript Compiler")
        self.root.geometry("1280x800")
        self.root.configure(bg="#000000")

        self.setup_styles()
        self.build_ui()
        self.bind_events()
        self.dark_title_bar()
        
        # Insert sample code
        sample = """/* Welcome to GGScript! */
frag lobby() {
    ign message = "ggwp team!";
    shout(message);
    
    ign username;
    shout("Enter your username: ");
    comsat username;
    
    shout("Hello, " + username + "!");
    ggwp;
}"""
        self.editor.insert("1.0", sample)
        self.update_line_numbers()

    def dark_title_bar(self):
        self.root.update()
        if platform.system() == "Windows":
            try:
                import ctypes as ct
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
                get_parent = ct.windll.user32.GetParent
                hwnd = get_parent(self.root.winfo_id())
                value = ct.c_int(2)
                set_window_attribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ct.byref(value), ct.sizeof(value))
            except Exception:
                pass

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("default")
        
        style.configure("Dark.Treeview", background="#0a0a0a", fieldbackground="#0a0a0a", 
                        foreground="#ffffff", borderwidth=0, rowheight=25)
        style.configure("Dark.Treeview.Heading", background="#111111", foreground="#ffffff", 
                        font=('Consolas', 10, 'bold'), borderwidth=1, relief="solid")
        style.map("Dark.Treeview.Heading", background=[('active', '#222222')])
        style.map("Dark.Treeview", background=[('selected', '#333333')])

    def build_ui(self):
        nav_frame = tk.Frame(self.root, bg="#000000", height=50)
        nav_frame.pack(side="top", fill="x", pady=10, padx=15)
        
        title_lbl = tk.Label(nav_frame, text="GGScript Compiler", bg="#000000", fg="#ffffff", font=("Consolas", 18, "bold"))
        title_lbl.pack(side="left")
        
        self.btn_run = self.create_nav_button(nav_frame, "RUN", self.run_pipeline)
        self.btn_run.pack(side="right", padx=(10, 0))
        
        self.btn_sem = self.create_nav_button(nav_frame, "SEMANTIC", self.run_semantic)
        self.btn_sem.pack(side="right", padx=(10, 0))
        
        self.btn_syn = self.create_nav_button(nav_frame, "SYNTAX", self.run_syntax)
        self.btn_syn.pack(side="right", padx=(10, 0))
        
        self.btn_lex = self.create_nav_button(nav_frame, "LEXICAL", self.run_lexical)
        self.btn_lex.pack(side="right", padx=(10, 0))

        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#444444", bd=0, sashwidth=8, sashrelief="raised", opaqueresize=True)
        main_paned.pack(side="top", fill="both", expand=True, padx=15, pady=(0, 15))

        left_paned = tk.PanedWindow(main_paned, orient=tk.VERTICAL, bg="#444444", bd=0, sashwidth=8, sashrelief="raised", opaqueresize=True)
        main_paned.add(left_paned, stretch="always", minsize=600)
        
        right_frame = tk.Frame(main_paned, bg="#000000", highlightbackground="#444444", highlightthickness=1)
        main_paned.add(right_frame, stretch="never", minsize=350)

        editor_container = tk.Frame(left_paned, bg="#000000", highlightbackground="#444444", highlightthickness=1)
        left_paned.add(editor_container, stretch="always", minsize=300)
        
        self.line_numbers = tk.Text(editor_container, width=4, bg="#0a0a0a", fg="#555555", font=("Consolas", 13),
                                    state="disabled", borderwidth=0, highlightthickness=0, pady=10)
        self.line_numbers.pack(side="left", fill="y")
        
        self.editor = tk.Text(editor_container, bg="#000000", fg="#ffffff", font=("Consolas", 13), 
                              insertbackground="#ffffff", borderwidth=0, highlightthickness=0, pady=10, padx=10, undo=True)
        self.editor.pack(side="left", fill="both", expand=True)

        term_container = tk.Frame(left_paned, bg="#000000", highlightbackground="#444444", highlightthickness=1)
        left_paned.add(term_container, stretch="never", minsize=200)
        
        term_header = tk.Label(term_container, text="TERMINAL", bg="#111111", fg="#aaaaaa", font=("Consolas", 10, "bold"), anchor="w", padx=10, pady=5)
        term_header.pack(side="top", fill="x")
        
        self.terminal = tk.Text(term_container, bg="#000000", fg="#ffffff", font=("Consolas", 12), 
                                insertbackground="#ffffff", borderwidth=0, highlightthickness=0, padx=10, pady=10, state=tk.DISABLED, height=6)
        self.terminal.pack(side="bottom", fill="both", expand=True)
        
        self.terminal.tag_config("error", foreground="#ffaaaa")
        self.terminal.tag_config("success", foreground="#aaffaa")
        self.terminal.tag_config("info", foreground="#aaaaaa")
        self.terminal.tag_config("output", foreground="#ffffff")
        self.terminal.tag_config("input", foreground="#dddddd", font=("Consolas", 12, "italic"))

        self.terminal.tag_config("error_border", foreground="#ff5555", font=("Consolas", 12, "bold"))
        self.terminal.tag_config("error_lineno", foreground="#666666")
        self.terminal.tag_config("error_code", foreground="#eeeeee")
        self.terminal.tag_config("error_pointer", foreground="#ff5555", font=("Consolas", 12, "bold"))

        self.table = ttk.Treeview(right_frame, columns=("Lexeme", "Token", "Type"), show="headings", style="Dark.Treeview")
        self.table.heading("#1", text="Lexeme")
        self.table.heading("#2", text="Token")
        self.table.heading("#3", text="Type")
        self.table.column("#1", width=120, anchor="w")
        self.table.column("#2", width=120, anchor="w")
        self.table.column("#3", width=100, anchor="w")
        self.table.pack(fill="both", expand=True)

    def create_nav_button(self, parent, text, command):
        btn = tk.Button(parent, text=text, bg="#000000", fg="#ffffff", font=("Consolas", 10, "bold"),
                        activebackground="#222222", activeforeground="#ffffff", relief="solid", bd=1,
                        cursor="hand2", command=command, width=12, pady=6)
        btn.bind("<Enter>", lambda e: btn.config(bg="#222222"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#000000"))
        return btn

    def bind_events(self):
        self.editor.bind("<KeyRelease>", self.on_text_change)
        self.editor.bind("<MouseWheel>", self.sync_scroll)
        self.editor.bind("<Tab>", self.insert_tab)
        for char in ['{', '[', '(', '"', "'"]:
            self.editor.bind(char, self.auto_close_brackets)
        self.editor.bind("<Return>", self.handle_editor_enter)

    def on_text_change(self, event=None):
        self.update_line_numbers()
        self.sync_scroll()

    def sync_scroll(self, event=None):
        self.line_numbers.yview_moveto(self.editor.yview()[0])
        
    def update_line_numbers(self):
        line_count = int(self.editor.index('end-1c').split('.')[0])
        line_numbers = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")
        self.line_numbers.insert("1.0", line_numbers, "right")
        self.line_numbers.config(state="disabled")

    def insert_tab(self, event):
        self.editor.insert(tk.INSERT, "    ")
        return "break"

    def auto_close_brackets(self, event):
        char = event.char
        pairs = {'{': '}', '[': ']', '(': ')', '"': '"', "'": "'"}
        if char in pairs:
            self.editor.insert(tk.INSERT, char + pairs[char])
            self.editor.mark_set(tk.INSERT, "insert-1c")
            return "break"
            
    def handle_editor_enter(self, event):
        cursor_pos = self.editor.index(tk.INSERT)
        line_text = self.editor.get(f"{cursor_pos} linestart", cursor_pos)
        current_indent = len(line_text) - len(line_text.lstrip(' '))
        indent_str = " " * current_indent
        prev_char = self.editor.get(f"{cursor_pos}-1c")
        next_char = self.editor.get(cursor_pos)
        
        if prev_char == '{' and next_char == '}':
            self.editor.insert(tk.INSERT, f"\n{indent_str}    \n{indent_str}")
            self.editor.mark_set(tk.INSERT, "insert - 1 line lineend")
            self.update_line_numbers()
            self.editor.see(tk.INSERT)
            return "break"
        
        self.editor.insert(tk.INSERT, f"\n{indent_str}")
        self.update_line_numbers()
        self.editor.see(tk.INSERT)
        return "break"

    # ========================================================================
    # INTERACTIVE THREADED TERMINAL LOGIC
    # ========================================================================
    def clear_term(self):
        self.terminal.config(state=tk.NORMAL)
        self.terminal.delete("1.0", tk.END)
        self.terminal.config(state=tk.DISABLED)

    def print_term(self, text, tag="output", end="\n"):
        self.terminal.config(state=tk.NORMAL)
        self.terminal.insert(tk.END, str(text) + end, tag)
        self.terminal.see(tk.END)
        self.terminal.config(state=tk.DISABLED)

    def request_input(self, prompt=""):
        """
        Thread-safe method that unlocks the terminal to allow user typing.
        Captures the text and returns it to the executed Python code.
        """
        user_val = [""]
        input_done = threading.Event()
        
        def setup_terminal_input():
            # 1. Unlock the terminal and print the prompt
            self.terminal.config(state=tk.NORMAL)
            if prompt:
                self.terminal.insert("end", prompt, "output")
            self.terminal.see("end")
            
            # 2. Mark the exact spot where the user starts typing
            self.terminal.mark_set("input_start", "end-1c")
            self.terminal.mark_gravity("input_start", "left")
            
            # Force cursor to the end
            self.terminal.mark_set("insert", "end-1c")
            self.terminal.focus_set()
            
            def on_keypress(event):
                # Let Enter be handled by on_enter below
                if event.keysym == "Return":
                    return

                # 1. Handle Cut (Ctrl+X)
                if event.keysym.lower() == "x" and (event.state & 4 or event.state & 8):
                    try:
                        sel_start = self.terminal.index("sel.first")
                        sel_end = self.terminal.index("sel.last")
                        if self.terminal.compare(sel_start, "<", "input_start"):
                            # Manually copy to clipboard
                            self.root.clipboard_clear()
                            self.root.clipboard_append(self.terminal.get(sel_start, sel_end))
                            
                            # Only delete the part after the prompt
                            if self.terminal.compare(sel_end, ">", "input_start"):
                                self.terminal.delete("input_start", sel_end)
                            
                            self.terminal.tag_remove("sel", "1.0", "end")
                            self.terminal.mark_set("insert", "end-1c")
                            return "break"
                    except tk.TclError:
                        pass
                
                # 2. Handle Paste (Ctrl+V)
                if event.keysym.lower() == "v" and (event.state & 4 or event.state & 8):
                    try:
                        sel_start = self.terminal.index("sel.first")
                        if self.terminal.compare(sel_start, "<", "input_start"):
                            self.terminal.tag_remove("sel", "1.0", "end")
                    except tk.TclError:
                        pass
                    
                    if self.terminal.compare("insert", "<", "input_start"):
                        self.terminal.mark_set("insert", "end-1c")
                    return # Let Tkinter handle the actual paste text at the corrected cursor

                # Check if the keystroke modifies the text
                is_modifying = event.keysym in ("BackSpace", "Delete") or (event.char and event.char.isprintable())
                if not is_modifying:
                    return

                try:
                    # 3. Handling active selections (like Ctrl+A)
                    sel_start = self.terminal.index("sel.first")
                    sel_end = self.terminal.index("sel.last")
                    
                    # If selection overlaps the read-only area
                    if self.terminal.compare(sel_start, "<", "input_start"):
                        # Delete ONLY the part of the selection that the user is allowed to edit
                        if self.terminal.compare(sel_end, ">", "input_start"):
                            self.terminal.delete("input_start", sel_end)
                        
                        # Clear selection highlight and move cursor to end
                        self.terminal.tag_remove("sel", "1.0", "end")
                        self.terminal.mark_set("insert", "end-1c")
                        
                        # Insert the character if they typed one (instead of hitting Backspace)
                        if event.char and event.char.isprintable() and event.keysym not in ("BackSpace", "Delete"):
                            self.terminal.insert("end-1c", event.char)
                            
                        self.terminal.see("end")
                        return "break"
                except tk.TclError:
                    # 4. Standard Typing/Deletion without selection
                    if event.keysym == "BackSpace" and self.terminal.compare("insert", "<=", "input_start"):
                        return "break"
                    if event.keysym == "Delete" and self.terminal.compare("insert", "<", "input_start"):
                        return "break"
                    if event.char and event.char.isprintable() and self.terminal.compare("insert", "<", "input_start"):
                        self.terminal.mark_set("insert", "end-1c")
                        self.terminal.see("end")

            def on_enter(event):
                # Get everything typed between the end of the prompt and the enter key
                val = self.terminal.get("input_start", "end-1c")
                user_val[0] = val.strip()
                
                # Visual newline and lock the terminal back down
                self.terminal.insert("end", "\n")
                self.terminal.unbind("<Return>")
                self.terminal.unbind("<Key>")
                self.terminal.config(state=tk.DISABLED)
                
                # Signal the worker thread to continue execution
                input_done.set()
                return "break"
                
            # Bind the unified event logic
            self.terminal.bind("<Key>", on_keypress)
            self.terminal.bind("<Return>", on_enter)
            
        # Execute the UI interaction securely on the main GUI thread
        self.root.after(0, setup_terminal_input)
        
        # Pause the code execution thread until the user presses Enter
        input_done.wait()
        return user_val[0]

    def print_error_box(self, error_str, code_text):
        match = re.search(r'Ln (\d+), Col (\d+)', error_str)
        if not match:
            self.print_term(error_str, "error")
            return
            
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
            
            self.print_term(error_str, "error")
            self.print_term("")  # Add blank line for spacing
            box_width = 80 
            
            self.terminal.config(state=tk.NORMAL)
            self.terminal.insert(tk.END, " ▌ ", "error_border")
            self.terminal.insert(tk.END, f"{ln:02d} | ", "error_lineno")
            code_pad = max(0, box_width - len(f" ▌ {ln:02d} | {expanded_line}"))
            self.terminal.insert(tk.END, expanded_line + (" " * code_pad) + "\n", "error_code")
            
            self.terminal.insert(tk.END, " ▌ ", "error_border")
            pointer_line = f"     {pointer_spaces}^"
            pointer_pad = max(0, box_width - len(f" ▌ {pointer_line}"))
            self.terminal.insert(tk.END, pointer_line + (" " * pointer_pad) + "\n\n", "error_pointer")
            self.terminal.see(tk.END)
            self.terminal.config(state=tk.DISABLED)
        else:
            self.print_term(error_str, "error")

    def populate_table(self, tokens):
        for item in self.table.get_children(): self.table.delete(item)
        for t in tokens:
            if t.type in (TokenType.eof, TokenType.newline, TokenType.whitespace): continue
            raw_type_str = str(t.type).split('.')[-1] if '.' in str(t.type) else str(t.type)
            lexeme = str(t.value).replace("\n", "\\n").replace("\t", "\\t")
            token_display = lexeme if raw_type_str.lower() in ["comment", "terminator", "separator", "lparen", "rparen", "lbrace", "rbrace", "lbracket", "rbracket"] else raw_type_str
            if raw_type_str.lower() == "choke_clutch": token_display = "choke clutch"
            self.table.insert("", "end", values=(lexeme, token_display, get_token_category(raw_type_str)))

    # ========================================================================
    # COMPILER PIPELINE STAGES
    # ========================================================================
    def run_lexical(self):
        self.clear_term()
        self.print_term("→ running lexical analysis...", "info")
        code = self.editor.get("1.0", "end-1c")
        try:
            lexer = Lexer(code)
            tokens, errors = lexer.make_tokens()
            self.populate_table(tokens)
            
            if errors:
                self.print_term(f"Found {len(errors)} lexical error(s):", "error")
                for err in errors:
                    err_str = err.as_string() if hasattr(err, 'as_string') else str(err)
                    self.print_error_box(err_str, code)
            else:
                self.print_term("Lexical analysis successful ✓ No errors.", "success")
        except Exception as e:
            self.print_term(f"Lexer crashed: {str(e)}", "error")

    def run_syntax(self):
        self.clear_term()
        self.print_term("→ running syntax analysis...", "info")
        code = self.editor.get("1.0", "end-1c")
        try:
            tokens, errors = Lexer(code).make_tokens()
            self.populate_table(tokens)
            if errors:
                self.print_term("Lexical errors found. Cannot proceed to syntax.", "error")
                for err in errors:
                    self.print_error_box(err.as_string() if hasattr(err, 'as_string') else str(err), code)
                return

            success, msg = analyze_syntax(tokens)
            if success:
                self.print_term(msg, "success")
            else:
                self.print_error_box(msg, code)
        except Exception as e:
            self.print_term(f"Parser crashed: {str(e)}", "error")

    def run_semantic(self):
        self.clear_term()
        self.print_term("→ running semantic analysis...", "info")
        code = self.editor.get("1.0", "end-1c")
        try:
            tokens, errors = Lexer(code).make_tokens()
            self.populate_table(tokens)
            if errors: return self.print_term("Lexical errors found. Cannot proceed.", "error")
            
            syn_ok, syn_msg = analyze_syntax(tokens)
            if not syn_ok: 
                self.print_term("Syntax errors found:", "error")
                return self.print_error_box(syn_msg, code)
                
            sem_ok, sem_msg = analyze_semantics(tokens)
            if sem_ok:
                self.print_term(sem_msg, "success")
            else:
                for err_msg in sem_msg.split('\n'):
                    if err_msg.strip(): self.print_error_box(err_msg, code)
        except Exception as e:
            self.print_term(f"Semantic Analyzer crashed: {str(e)}", "error")

    def run_pipeline(self):
        self.clear_term()
        self.print_term("→ executing compilation pipeline...", "info")
        code = self.editor.get("1.0", "end-1c")
        
        try:
            tokens, errors = Lexer(code).make_tokens()
            self.populate_table(tokens)
            if errors: return self.print_term("Lexical Errors found. Cannot Run.", "error")
            
            syn_ok, syn_msg = analyze_syntax(tokens)
            if not syn_ok: 
                self.print_term("Syntax Error:", "error")
                return self.print_error_box(syn_msg, code)
            
            sem_ok, sem_msg = analyze_semantics(tokens)
            if not sem_ok: 
                self.print_term("Semantic Error:", "error")
                for err_msg in sem_msg.split('\n'):
                    if err_msg.strip(): self.print_error_box(err_msg, code)
                return
            
            self.print_term("Semantic analysis successful ✓ No errors.", "success")
            
            ast_errors = []
            ast = ASTBuilder(tokens, ast_errors).parse_program()
            if ast_errors: return self.print_term("AST Building Failed:\n" + "\n".join(str(e) for e in ast_errors), "error")
                
            self.print_term("→ Code Generation successful ✓ Executing program...\n", "success")
            
            # --- CODE GENERATION EXECUTION ---
            try:
                from src.codegen import CodeGen
                
                # 1. Translate the GGScript AST into a massive Python string
                cg = CodeGen()
                success, py_code = cg.compile(ast)
                
                if not success:
                    return self.print_term(f"CodeGen Error:\n{py_code}", "error")
                    
                # 2. Expose specific UI commands to the generated Python code
                def console_disp(*args):
                    output_text = "".join(map(str, args))
                    # Don't add automatic newline - user controls via \n in code
                    self.root.after(0, self.print_term, output_text, "output", "")

                def console_insp(prompt_var=""):
                    # Uses updated terminal typing function safely handling empty strings
                    user_val = self.request_input("")
                    if not user_val: 
                        return 0 # Default fallback if user hits enter with no text
                    try:
                        if '.' in user_val: return float(user_val)
                        return int(user_val)
                    except ValueError:
                        return user_val

                # 3. Create the execution environment
                exec_env = {
                    'console_disp': console_disp,
                    'console_insp': console_insp,
                    'builtins': builtins
                }
                
                # 4. Run the code generator's script inside a background thread!
                def execute_thread():
                    try:
                        exec(py_code, exec_env)
                        self.root.after(0, self.print_term, "\n\n[Code Executed]", "info")
                    except Exception as e:
                        error_trace = traceback.format_exc()
                        self.root.after(0, self.print_term, f"\nExecution failed: {str(e)}\n{error_trace}", "error")
                
                threading.Thread(target=execute_thread, daemon=True).start()

            except ImportError:
                self.print_term("\n[Notice] 'src.codegen' module not found.", "error")
                
        except Exception as e:
            self.print_term(f"Pipeline crashed: {str(e)}", "error")

if __name__ == "__main__":
    app = GGScriptIDE()
    app.root.mainloop()