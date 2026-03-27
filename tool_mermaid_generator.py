import ollama
import re

# Am creat un Prompt de Sistem ultra-avansat care învață modelul exact 
# ce forme și ce culori să folosească pentru un aspect corporate (ca în slide).
SYSTEM_PROMPT = """Ești un expert automat în arhitectură software. Generează o diagramă Mermaid.js (Type: graph TD) bazată STRICT pe descrierea utilizatorului. Nu inventa componente care nu sunt menționate sau deduse din flux.

REGULI CRITICE DE DESIGN ȘI SINTAXĂ:
1. FORMELE NODURILOR (OBLIGATORIU să deduci forma corectă vizual):
   - Actori umani, Endpoints, Răspunsuri (ex: User, Client, Response): Folosește forma de pilulă `([Nume])`. Ex: `U([User Input])`
   - Baze de date, Stocare (ex: History, Database, Storage): Folosește cilindru `[(Nume)]`. Ex: `DB[(Conversation File)]`
   - Orice alt proces, Serviciu sau Tool (ex: Orchestrator, Classifier): Folosește dreptunghi cu paranteze drepte `[Nume]`. Ex: `O[Orchestrator]`

2. SĂGEȚILE:
   - Creează un flux logic cronologic și conectează TOATE componentele între ele. Nu lăsa noduri "în aer".
   - Adaugă etichete scurte pe săgeți explicând acțiunea. Ex: `A -->|trimite query| B`
   - Pentru erori, blocaje sau stocare asincronă, folosește săgeți punctate `-.->|text|`.
   - Pentru fetch/store bidirectional, folosește `<-.->|text|`.

3. CULORILE (FOARTE IMPORTANT):
   Dacă utilizatorul specifică anume culori pentru anumite grupuri (ex: "the tools to be in red"), asignează acea culoare STRICT la nodurile respective!
   Dacă NU este specificat explicit în prompt, asignează culorile semantic din această paletă corporate:
   - Procese Core (Standard): fill:#3366cc,color:#fff,stroke:#333
   - Baze de Date / Actori Capăt: fill:#4252b5,color:#fff,stroke:#333
   - Securitate/Guardrails: fill:#cc8800,color:#fff,stroke:#333
   - Classifier/Validări: fill:#33cc33,color:#fff,stroke:#333
   - Tool-uri externe / Alarme: fill:#b30000,color:#fff,stroke:#333
   
   Adaugă CULORILE prin comenzi `style` scrise UNA SUB ALTA, pe rânduri SEPARATE, la final.

EXEMPLU GENERIC DE SINTAXĂ (Aplică aceste reguli pe ORICE flux cerut, oricât de complex sau simplu):
graph TD
    A([Client]) -->|request| B[API Gateway]
    B -->|read/write| C[(User Database)]
    B -.->|log error| D([Error Handler])
    
    style A fill:#4252b5,color:#fff,stroke:#333
    style B fill:#3366cc,color:#fff,stroke:#333
    style C fill:#4252b5,color:#fff,stroke:#333
    style D fill:#b30000,color:#fff,stroke:#333

5. Returnează DOAR codul Mermaid, începând cu 'graph TD'. NU adăuga text descriptiv.
"""

def tool_mermaid_generator(text_input: str) -> str:
    """Genereaza cod Mermaid dintr-o descriere textuala."""
    if not text_input or not text_input.strip():
        return "Eroare: textul de intrare este gol."

    try:
        raspuns = ollama.chat(
            model='gemma3:4b', 
            messages=[
              {'role': 'system', 'content': SYSTEM_PROMPT},
              {'role': 'user', 'content': text_input.strip()}
            ]
        )
        
        text_brut = raspuns['message']['content']
        
        # --- CURĂȚENIA ANTI-BOMBĂ ---
        cod_mermaid = text_brut
        if "```mermaid" in cod_mermaid:
            cod_mermaid = cod_mermaid.split("```mermaid")[1].split("```")[0]
        elif "```" in cod_mermaid:
            cod_mermaid = cod_mermaid.split("```")[1].split("```")[0]
        
        cod_mermaid = cod_mermaid.replace("Here is the Mermaid code:", "").replace("Here is the diagram:", "")
        
        # Curățare: Lăsăm AI-ul să facă treaba, nu înlocuim manual pipe-urile '|' 
        # deoarece Mermaid folosește pipe-uri pentru textul de pe săgeți (-->|text|)
        # cod_mermaid = cod_mermaid.replace(" | ", "\\nstyle ")  <-- ASTA STRICĂ SĂGEȚILE

        
        cod_mermaid = cod_mermaid.strip()
        
        if not cod_mermaid.startswith("graph") and not cod_mermaid.startswith("flowchart"):
            cod_mermaid = "graph TD\n" + cod_mermaid
            
        return cod_mermaid

    except Exception as e:
        return f"graph TD\n    Error[Eroare generare diagrama: {str(e)[:50]}]\n    style Error fill:#ff4c4c,color:#fff"