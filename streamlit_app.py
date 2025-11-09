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
        TokenType.afk, TokenType.buff, TokenType.build, TokenType.choke,
        TokenType.choke_clutch, TokenType.clutch, TokenType.comsat,
        TokenType.count, TokenType.craft, TokenType.dodge, TokenType.drop,
        TokenType.elo, TokenType.frag, TokenType.ggwp, TokenType.grind,
        TokenType.hop, TokenType.ign, TokenType.lobby, TokenType.nerf,
        TokenType.noob, TokenType.pick, TokenType.retry, TokenType.role,
        TokenType.shout, TokenType.split, TokenType.stack, TokenType.stun,
        TokenType.surebol, TokenType.tag, TokenType.try_,
    }
    if tt in KEYWORDS:
        return "KEYWORD"
    if tt is TokenType.identifier:
        return "IDENTIFIER"
    if tt in (TokenType.integer, TokenType.float_, TokenType.string, TokenType.char):
        return "LITERAL"
    if tt in {
        TokenType.plus, TokenType.minus, TokenType.mul, TokenType.div,
        TokenType.mod, TokenType.assign, TokenType.plus_assign,
        TokenType.minus_assign, TokenType.mul_assign, TokenType.div_assign,
        TokenType.mod_assign, TokenType.increment, TokenType.decrement,
        TokenType.lt, TokenType.gt, TokenType.lte, TokenType.gte,
        TokenType.eq, TokenType.neq, TokenType.not_, TokenType.and_, TokenType.or_
    }:
        return "OPERATOR"
    if tt in {
        TokenType.lparen, TokenType.rparen, TokenType.lbracket,
        TokenType.rbracket, TokenType.lbrace, TokenType.rbrace,
        TokenType.comma, TokenType.semicolon, TokenType.colon, TokenType.dot
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
                if t.type in (TokenType.eof, TokenType.newline):
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