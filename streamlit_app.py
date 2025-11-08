import streamlit as st
import pandas as pd
from lexer.lexer import Lexer  # Import your existing Lexer
from lexer.token_types import TokenType  # Import your TokenTypes

# --- Page Configuration ---
st.set_page_config(
    page_title="GGScript Lexer",
    layout="wide"  # Use the full width of the page
)

st.title("🎮 GGScript Lexical Analyzer")
st.write("A Streamlit web interface for the GGScript compiler's lexer.")

# --- Sample Code ---
sample_code = """/* Welcome to the GGScript Lexer! 
/* This is a web-based system

frag lobby() {
    ign message = "Hello, GGScript!";
    shout message;
}
"""

# --- Layout ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("GGScript Code Input")
    code_input = st.text_area(
        "Enter your code here:", 
        value=sample_code, 
        height=600,
        label_visibility="collapsed"
    )
    
    analyze_button = st.button("Analyze Tokens", type="primary", use_container_width=True)

with col2:
    st.subheader("Lexical Analysis Output")

    if analyze_button:
        if not code_input:
            st.warning("Please enter some code to analyze.")
        else:
            # 1. Create the Lexer instance
            lexer = Lexer(code_input)
            
            # 2. Tokenize the code
            tokens = lexer.tokenize()
            
            # 3. Process tokens for display
            token_data = []
            errors = []
            
            for t in tokens:
                if t.type == TokenType.EOF:
                    break  # Don't show EOF
                
                # Collect errors
                if t.type == TokenType.ERROR:
                    errors.append(f"Error: {t.value} (Line: {t.line}, Col: {t.column})")
                
                # Don't show newlines in the main table
                if t.type != TokenType.NEWLINE:
                    token_data.append({
                        "Token Type": t.type.name,
                        "Value": str(t.value).replace('\n', '\\n').replace('\t', '\\t'),
                        "Line": t.line,
                        "Column": t.column
                    })

            # 4. Display Errors (if any)
            if errors:
                st.error("Lexical Errors Found:", icon="🚨")
                st.code("\n".join(errors), language="bash")
            else:
                st.success("Lexical analysis completed successfully!", icon="✅")

            # 5. Display Tokens in a table
            df = pd.DataFrame(token_data)
            st.dataframe(df, use_container_width=True, height=500)

    else:
        st.info("Click the 'Analyze Tokens' button to see the output.")