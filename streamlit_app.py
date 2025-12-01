import streamlit as st
import pandas as pd
from lexer.lexer import Lexer
from lexer.token_types import TokenType

# ------------------------------------------------------------------
#  Page Config & Logo
# ------------------------------------------------------------------
st.set_page_config(page_title="GGScript Lexer", layout="centered")

# Load and display logo
logo_url = "https://i.imgur.com/szLgNMG.png"

st.markdown(
    f"<h1 style='text-align: center; margin-top: -10px;'><img src='{logo_url}' width='120'> GGScript Lexical Analyzer</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align: center; color: #888; font-size: 0.9rem;'>Automata Theory and Formal Languages</p>",
    unsafe_allow_html=True
)

# ------------------------------------------------------------------
#  Token Category Helper
# ------------------------------------------------------------------
def token_category(tt: str) -> str:
    KEYWORDS = {
        'afk', 'buff', 'build', 'choke', 'choke_clutch', 'clutch', 'comsat',
        'count', 'craft', 'dodge', 'drop', 'elo', 'frag', 'ggwp', 'grind',
        'hop', 'ign', 'lobby', 'nerf', 'noob', 'pick', 'retry', 'role',
        'shout', 'split', 'stack', 'stun', 'surebol', 'tag', 'try'
    }
    if tt in KEYWORDS:
        return "KEYWORD"
    if tt == "identifier":
        return "IDENTIFIER"
    if tt == "integer":
        return "INTEGER LITERAL"
    if tt == "float":
        return "FLOAT LITERAL"
    if tt == "string":
        return "STRING LITERAL"
    if tt == "char":
        return "CHAR LITERAL"
    if tt == "comment":
        return "COMMENT"
    if tt in {
        '+', '-', '*', '/', '%', '=', '+=', '-=', '*=', '/=', '%=',
        '++', '--', '<', '>', '<=', '>=', '==', '!=', '!', '&&', '||'
    }:
        return "OPERATOR"
    if tt == "terminator":
        return "TERMINATOR"
    if tt == "separator":
        return "SEPARATOR"
    if tt == "bracket":
        return "BRACKET"
    return "Undetermined"


# ------------------------------------------------------------------
#  Sample Code
# ------------------------------------------------------------------
sample_code = '''/* Welcome to GGScript! */
frag lobby() {
    ign message = "GG WP!";
    shout message;
    ggwp;
}
'''

# ------------------------------------------------------------------
#  Layout: Centered Input + Output
# ------------------------------------------------------------------
if "code_text" not in st.session_state:
    st.session_state.code_text = sample_code

with st.container():
    code = st.text_area(
        "Enter GGScript code:",
        key="code_area",  # widget key separate from session var
        value=st.session_state.code_text,
        height=300,
        label_visibility="collapsed",
        placeholder="/* Paste or write your GGScript code here..."
    )

    col_btn1, col_btn2, _ = st.columns([1, 1, 3])
    with col_btn1:
        analyze = st.button("Analyze", type="primary", use_container_width=True)
    with col_btn2:
        if st.button("Clear", use_container_width=True):
            st.session_state.code_text = ""   # reset stored value
            st.rerun()                        # rerun to refresh text_area

    # Keep session state in sync with current text_area content
    st.session_state.code_text = code

    if analyze:
        if not code.strip():
            st.warning("Please enter some code to analyze.")
        else:
            lexer = Lexer(code)
            tokens, errors = lexer.make_tokens()

            # Token Table
            rows = []
            for t in tokens:
                if t.type in (TokenType.eof, TokenType.newline):
                    continue
                lexeme = str(t.value).replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r")
                raw_type = str(t.type)

                # Decide TOKEN display name
                if raw_type == "choke_clutch":
                    token_display = "choke clutch"
                elif raw_type in {"comment", "terminator", "separator", "bracket"}:
                    token_display = lexeme
                elif raw_type == "char":
                    token_display = "Character"
                elif raw_type == "string":
                    token_display = "String"
                elif raw_type == "integer":
                    token_display = "Integer"
                elif raw_type == "float":
                    token_display = "Float"
                elif raw_type == "identifier":
                    token_display = "Identifier"
                else:
                    token_display = raw_type  # keywords and operators stay as-is

                rows.append({
                    "LEXEME": lexeme,
                    "TOKEN": token_display,
                    "TYPE": token_category(raw_type)
                })

            # Errors
            if errors:
                st.error("Lexical Errors Found")
                for e in errors:
                    st.code(e.as_string(), language=None)
            else:
                st.success("Lexical analysis successful!")

            if rows:
                df = pd.DataFrame(rows)
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "LEXEME": st.column_config.TextColumn("LEXEME", width="medium"),
                        "TOKEN": st.column_config.TextColumn("TOKEN", width="medium"),
                        "TYPE": st.column_config.TextColumn("TYPE", width="small"),
                    }
                )

    else:
        st.info("Paste code and click **Analyze** to see tokens.")