import streamlit as st
import pandas as pd
from streamlit_monaco import st_monaco
from src.lexer import Lexer
from src.token_types import TokenType
from src.parser import analyze_syntax

# ── PAGE CONFIG ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="GGScript Editor",
    page_icon="https://i.imgur.com/szLgNMG.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── STYLING ───────────────────────────────────────────────────────────
st.markdown("""
    <style>
        /* Hide default Streamlit UI */
        .stDeployButton { display: none !important; }
        #MainMenu { visibility: hidden; }
        header { visibility: hidden; }
        [data-testid="stDecoration"] { display: none; }
        
        /* Global theme */
        .stApp {
            background: #000000 !important;
            color: #ffffff !important;
            font-family: Consolas, "Courier New", monospace;
        }
            
        /* Buttons */
        div.stButton > button {
            background: #000000 !important;
            color: #ffffff !important;
            border: 1px solid #ffffff !important;
            border-radius: 0 !important;
            padding: 6px 16px !important;
            font-size: 0.92rem !important;
            margin: 0 !important;
            font-weight: bold;
            height: 42px !important;
            line-height: 1 !important;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        div.stButton > button:hover {
            background: #222222 !important;
            color: #ffffff !important;
            border-color: #ffffff !important;
        }
        
        /* Terminal */
        .terminal-panel {
            background: #000000 !important;
            border-radius: 6px;
            margin-top: 16px;
            border: 1px solid #444444 !important;
            overflow: hidden;
        }
        .terminal-header {
            background: #000000 !important;
            color: #aaaaaa !important;
            font-size: 13px;
            padding: 6px 12px;
            border-bottom: 1px solid #444444 !important;
            font-weight: bold;
        }
        .terminal-body {
            padding: 12px 16px;
            font-family: Consolas, monospace;
            color: #ffffff !important;
            font-size: 13.5px;
            min-height: 120px;
            white-space: pre-wrap;
            line-height: 1.45;
        }
        .error-line { color: #ffaaaa !important; }
        .success-line { color: #aaffaa !important; }
        
        .block-container { padding-top: 1rem !important; }
        
        /* Monaco editor styling */
        .monaco-editor,
        .monaco-editor .view-lines,
        .monaco-editor .view-overlays,
        .monaco-editor-background,
        .monaco-editor .margin-view-overlays,
        .monaco-editor .glyph-margin {
            background: #000000 !important;
            color: #ffffff !important;
        }
        .monaco-editor .token.comment, .monaco-editor .mtk9, .monaco-editor .mtk10 { color: #777777 !important; font-style: italic !important; }
        .monaco-editor .token.keyword, .monaco-editor .mtk4 { color: #ffffff !important; font-weight: bold !important; }
        .monaco-editor .token.string, .monaco-editor .mtk6, .monaco-editor .mtk7 { color: #dddddd !important; }
        .monaco-editor .token.number, .monaco-editor .mtk8 { color: #cccccc !important; }
        .monaco-editor .token.function, .monaco-editor .mtk5 { color: #eeeeee !important; }
        .monaco-editor .token.operator, .monaco-editor .token.punctuation, .mtk11, .mtk12 { color: #999999 !important; }
        .monaco-editor .line-numbers, .monaco-editor .margin-view-overlays .line-number { color: #555555 !important; }
        .monaco-editor .active-line-number { color: #888888 !important; }
        .monaco-editor .current-line, .monaco-editor .current-line-both { background: #1a1a1a !important; border: none !important; }
        .monaco-editor .selection { background: #444444 !important; }

        /* ── Custom scrollable table – tight columns, minimal spacing ── */
        .custom-table-container {
            height: 445px;
            overflow-y: auto;
            overflow-x: auto;
            border: 1px solid #444444;
            border-radius: 4px;
            background-color: #000000;
        }
        .custom-table-container table {
            width: 100%;
            border-collapse: collapse;
            border-spacing: 0;
            color: #ffffff;
            font-size: 14px;
            table-layout: auto;
        }
        .custom-table-container th,
        .custom-table-container td {
            padding: 5px 8px;               /* reduced padding */
            border: 1px solid #2a2a2a;      /* thin dark border */
            text-align: left;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .custom-table-container th {
            background-color: #111111;
            font-weight: bold;
            position: sticky;
            top: 0;
            z-index: 2;
            border-bottom: 2px solid #444444;
            padding: 6px 10px;
        }
        .custom-table-container tr:nth-child(even) {
            background-color: #0a0a0a;
        }
        .custom-table-container::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        .custom-table-container::-webkit-scrollbar-track {
            background: #111111;
        }
        .custom-table-container::-webkit-scrollbar-thumb {
            background: #444444;
            border-radius: 4px;
        }
        .custom-table-container::-webkit-scrollbar-thumb:hover {
            background: #666666;
        }
    </style>
""", unsafe_allow_html=True)

# ── TOKEN CATEGORY HELPER ─────────────────────────────────────────────
def get_token_category(raw_type: str) -> str:
    KEYWORDS = {
        'afk', 'buff', 'build', 'choke', 'choke_clutch', 'clutch', 'comsat',
        'count', 'craft', 'dodge', 'drop', 'elo', 'frag', 'ggwp', 'grind',
        'hop', 'ign', 'lobby', 'nerf', 'noob', 'pick', 'retry', 'role',
        'shout', 'split', 'stack', 'stun', 'surebol', 'tag', 'try'
    }
    raw_lower = raw_type.lower()
    if raw_lower in KEYWORDS:
        return "KEYWORD"
    if raw_lower == "identifier":
        return "IDENTIFIER"
    if raw_lower in ("integer", "int"):
        return "INTEGER LITERAL"
    if raw_lower in ("float", "double"):
        return "FLOAT LITERAL"
    if raw_lower == "string":
        return "STRING LITERAL"
    if raw_lower == "char":
        return "CHAR LITERAL"
    if raw_lower == "comment":
        return "COMMENT"
    
    OPERATORS = {
        '+', '-', '*', '/', '%', '=', '+=', '-=', '*=', '/=', '%=',
        '++', '--', '<', '>', '<=', '>=', '==', '!=', '!', '&&', '||'
    }
    if raw_lower in OPERATORS:
        return "OPERATOR"
    
    if raw_lower == "terminator":
        return "TERMINATOR"
    if raw_lower == "separator":
        return "SEPARATOR"
    if raw_lower == "bracket":
        return "BRACKET"
    
    return "OTHER"

# ── SAMPLE CODE ───────────────────────────────────────────────────────
SAMPLE_CODE = """/* Welcome to GGScript! */
frag lobby() {
    ign message = "ggwp team!";
    shout message;
    ggwp;
}"""

# ── NAVBAR ────────────────────────────────────────────────────────────
nav_col1, nav_run, nav_lex, nav_syn, nav_sem = st.columns(
    [5, 1, 1, 1, 1],
    vertical_alignment="center",
    gap="small"
)

with nav_col1:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px;">
            <img src="https://i.imgur.com/szLgNMG.png" width="80">
            <h1 style="color: #ffffff; font-size: 1.8rem; margin: 0; letter-spacing: 1px;">GGScript</h1>
        </div>
    """, unsafe_allow_html=True)

with nav_run:
    run_btn = st.button("RUN")

with nav_lex:
    lex_btn = st.button("LEXICAL")

with nav_syn:
    syn_btn = st.button("SYNTAX")

with nav_sem:
    sem_btn = st.button("SEMANTIC")

# ── MAIN WORKSPACE ────────────────────────────────────────────────────
col_editor, col_tokens = st.columns([1.8, 1])

with col_editor:
    code_content = st_monaco(
        value=SAMPLE_CODE,
        height="480px",
        language="plaintext",
        theme="hc-black",
        lineNumbers=True,
        minimap={"enabled": False}
    )

# ── LEXICAL ANALYSIS LOGIC ────────────────────────────────────────────
terminal_lines = ["ready."]

if lex_btn and code_content and code_content.strip():
    try:
        lexer = Lexer(code_content)
        tokens, errors = lexer.make_tokens()
        token_rows = []
        
        for t in tokens:
            if t.type in (TokenType.eof, TokenType.newline):
                continue
                
            raw_type_str = str(t.type).split('.')[-1] if '.' in str(t.type) else str(t.type)
            lexeme = str(t.value).replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r")
            
            token_display = lexeme if raw_type_str.lower() in ["comment", "terminator", "separator", "bracket"] else raw_type_str
            if raw_type_str.lower() == "choke_clutch":
                token_display = "choke clutch"
                
            token_rows.append({
                "Lexeme": lexeme,
                "Token": token_display,
                "Type": get_token_category(raw_type_str)
            })
        
        with col_tokens:
            if token_rows:
                # ── Build custom HTML table ──
                html = '<div class="custom-table-container">'
                html += '<table>'
                html += '<thead><tr><th>Lexeme</th><th>Token</th><th>Type</th></tr></thead>'
                html += '<tbody>'
                
                for row in token_rows:
                    # Escape to prevent HTML injection issues
                    lexeme_esc = row["Lexeme"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    token_esc  = row["Token"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    type_esc   = row["Type"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    
                    html += '<tr>'
                    html += f'<td>{lexeme_esc}</td>'
                    html += f'<td>{token_esc}</td>'
                    html += f'<td>{type_esc}</td>'
                    html += '</tr>'
                
                html += '</tbody>'
                html += '</table>'
                html += '</div>'
                
                st.markdown(html, unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div class="custom-table-container" style="display:flex; align-items:center; justify-content:center; color:#777777; font-size:16px;">'
                    'No tokens generated</div>',
                    unsafe_allow_html=True
                )
        
        terminal_lines = ["→ lexical analysis..."]
        
        if errors:
            terminal_lines.append(f"<span class='error-line'>Found {len(errors)} lexical error(s):</span>")
            for err in errors:
                formatted_error = err.as_string() if hasattr(err, 'as_string') else str(err)
                terminal_lines.append(f"<span class='error-line'>{formatted_error}</span>")
        else:
            terminal_lines.append("<span class='success-line'>Lexical analysis successful ✓ No errors.</span>")
            
    except Exception as e:
        terminal_lines = [
            "→ lexical analysis...",
            f"<span class='error-line'>Lexer crashed: {str(e)}</span>"
        ]

elif run_btn:
    terminal_lines = ["→ executing program...", "(not implemented yet)"]
elif syn_btn:
    terminal_lines = ["→ syntax analysis..."]
    if code_content and code_content.strip():
        try:
            lexer = Lexer(code_content)
            tokens, lex_errors = lexer.make_tokens()
            
            if lex_errors:
                terminal_lines.append(f"<span class='error-line'>Lexical errors found ({len(lex_errors)}). Cannot proceed to syntax.</span>")
                for err in lex_errors:
                    terminal_lines.append(f"<span class='error-line'>  {err.as_string()}</span>")
            else:
                success, message = analyze_syntax(tokens)
                if success:
                    terminal_lines.append(f"<span class='success-line'>{message}</span>")
                else:
                    terminal_lines.append(f"<span class='error-line'>{message}</span>")
                    
        except Exception as e:
            terminal_lines.append(f"<span class='error-line'>Parser crashed: {str(e)}</span>")
    else:
        terminal_lines.append("<span class='error-line'>No code to analyze.</span>")
elif sem_btn:
    terminal_lines = ["→ semantic analysis...", "(not implemented yet)"]

# ── RENDER TERMINAL ───────────────────────────────────────────────────
terminal_content = "\n".join(terminal_lines)
st.markdown(f"""
    <div class="terminal-panel">
        <div class="terminal-header">TERMINAL</div>
        <div class="terminal-body">{terminal_content}</div>
    </div>
""", unsafe_allow_html=True)