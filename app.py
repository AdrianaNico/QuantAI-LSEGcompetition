import streamlit as st
import json
import streamlit.components.v1 as components
from tool_financial_risk_scorer import tool_financial_risk_scorer
from tool_mermaid_generator import tool_mermaid_generator
st.set_page_config(page_title="ArchiBot LSEG", page_icon="🏗️", layout="wide")

# Selectie Tool - Simulare Intent Classifier
st.sidebar.title("🤖 Orchestrator")
tool_ales = st.sidebar.radio(
    "Alege Tool-ul activ:",
    ["Financial Risk Scorer", "Mermaid Diagram Generator"]
)

if tool_ales == "Financial Risk Scorer":
    st.title("📈 Financial Sentiment & Risk Scorer")
    st.markdown("Acest tool extrage **Sentimentul**, **Scorul de Risc (1-10)** și **Entitățile Cheie**.")
    placeholder_text = "Ex: The Federal Reserve unexpectedly raised interest rates..."
else:
    st.title("📊 Interactive Architecture Generator")
    st.markdown("Acest tool transformă descrierile tale într-o **diagramă interactivă și draggable**.")
    placeholder_text = "Ex: I want an orchestrator tool that receives a user query..."

st.divider()

# Input de la utilizator
user_input = st.text_area(
    "Introdu descrierea:",
    height=150,
    placeholder=placeholder_text
)

# Buton de rulare
if st.button("Analizează Textul 🚀", type="primary", use_container_width=True):
    if not user_input.strip():
        st.warning("⚠️ Te rog să introduci un text pentru analiză!")
    else:
        with st.spinner("⏳ Agentul lucrează (poate dura 30-60 sec)..."):
            
            if tool_ales == "Financial Risk Scorer":
                rezultat = tool_financial_risk_scorer(user_input)
                st.success("✅ Analiză finalizată!")
                st.code(rezultat, language="json")
            else:
                cod_mermaid = tool_mermaid_generator(user_input)
                
                html_code = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <script type="module">
                      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                      mermaid.initialize({{ startOnLoad: true }});
                    </script>
                </head>
                <body style="text-align: center; background-color: white; padding-top: 20px;">
                    <div class="mermaid">
                    {cod_mermaid}
                    </div>
                </body>
                </html>
                """
                
                st.success("✅ Diagramă generată cu succes!")
                with st.expander("🔍 Vezi codul Mermaid generat (Debugging)"):
                    st.code(cod_mermaid, language='mermaid')

                components.html(html_code, height=600, scrolling=True)
            
st.divider()
st.caption("🔍 Complet local, privat. Nu folosește API-uri externe.")
