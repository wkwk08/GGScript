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

st.markdown(f"<h1 style='text-align: center; margin-top: -10px;'><img src='{logo_url}' width='120'> GGScript Lexical Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888; font-size: 0.9rem;'>Automata Theory and Formal Languages</p>", unsafe_allow_html=True)

# ------------------------------------------------------------------
#  Token Category Helper
# ------------------------------------------------------------------
def token_category(tt: TokenType) -> str:
    KEYWORDS = {
        TokenType.AFK, TokenType.BUFF, TokenType.BUILD, TokenType.CHOKE,
        TokenType.CHOKE_CLUTCH, TokenType.CLUTCH, TokenType.COMSAT,
        TokenType.COUNT, TokenType.CRAFT, TokenType.DODGE, TokenType.DROP,
        TokenType.ELO, TokenType.FRAG, TokenType.GGWP, TokenType.GRIND,
        TokenType.HOP, TokenType.IGN, TokenType.LOBBY, TokenType.NERF,
        TokenType.NOOB, TokenType.PICK, TokenType.RETRY, TokenType.ROLE,
        TokenType.SHOUT, TokenType.SPLIT, TokenType.STACK, TokenType.STUN,
        TokenType.SUREBOL, TokenType.TAG, TokenType.TRY,
    }
    if tt in KEYWORDS:
        return "KEYWORD"
    if tt is TokenType.IDENTIFIER:
        return "IDENTIFIER"
    if tt in (TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING, TokenType.CHAR):
        return "LITERAL"
    if tt in {
        TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.DIV,
        TokenType.MOD, TokenType.ASSIGN, TokenType.PLUS_ASSIGN,
        TokenType.MINUS_ASSIGN, TokenType.MUL_ASSIGN, TokenType.DIV_ASSIGN,
        TokenType.MOD_ASSIGN, TokenType.INCREMENT, TokenType.DECREMENT,
        TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE,
        TokenType.EQ, TokenType.NEQ, TokenType.NOT, TokenType.AND, TokenType.OR
    }:
        return "OPERATOR"
    if tt in {
        TokenType.LPAREN, TokenType.RPAREN, TokenType.LBRACKET,
        TokenType.RBRACKET, TokenType.LBRACE, TokenType.RBRACE,
        TokenType.COMMA, TokenType.SEMICOLON, TokenType.COLON, TokenType.DOT
    }:
        return "DELIMITER"
    return "OTHER"


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
with st.container():
    code = st.text_area(
        "Enter GGScript code:",
        value=sample_code,
        height=300,
        label_visibility="collapsed",
        placeholder="// Paste or write your GGScript code here..."
    )

    col_btn1, col_btn2, _ = st.columns([1, 1, 3])
    with col_btn1:
        analyze = st.button("Analyze", type="primary", use_container_width=True)
    with col_btn2:
        if st.button("Clear", use_container_width=True):
            st.session_state.code = ""
            st.rerun()

    if 'code' in st.session_state:
        code = st.session_state.code

    if analyze:
        if not code.strip():
            st.warning("Please enter some code to analyze.")
        else:
            lexer = Lexer(code)
            tokens, errors = lexer.make_tokens()

            # Token Table
            rows = []
            for t in tokens:
                if t.type in (TokenType.EOF, TokenType.NEWLINE):
                    continue
                lexeme = str(t.value).replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r")
                rows.append({
                    "LEXEME": lexeme,
                    "TOKEN": t.type.name,
                    "TYPE": token_category(t.type)
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
                st.info("No visible tokens (only comments/whitespace?).")

    else:
        st.info("Paste code and click **Analyze** to see tokens.")