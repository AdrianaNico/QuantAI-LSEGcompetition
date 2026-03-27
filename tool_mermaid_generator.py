import ollama
import re

BASE_PROMPT = """Ești un Expert Arhitect și Diagramator Mermaid.js (graph TD). Trebuie să transformi descrierea utilizatorului într-o diagramă vizuală corectă și avansată.

REGULI VITALE DE SINTAXĂ (RESPECTĂ-LE SAU VEI CRĂPA APLICAȚIA!):
1. ID-URI NODURI = DOAR NUMERE! Node ID-ul (partea din stânga înainte de paranteze) TREBUIE să fie strict `N1`, `N2`, `N3` etc. ESTE STRICT INTERZIS SĂ FOLOSEȘTI NICI MĂCAR UN CUVÂNT CA ID! 
   CORECT: `N1[Bucharest] -->|text| N2[Vienna]` 
   GREȘIT (CRASH): `Bucharest[Bucharest] --> Vienna[Vienna]` sau `Last Stop[Salzburg]`.
2. FĂRĂ GHILIMELE! Este strict interzis să adaugi ghilimele `"` în interiorul nodurilor sau pe etichete.
3. Toate nodurile trebuie să folosească paranteze, ex: `N1[Nume]`, `N2(Nume)`, `N3{Conditie}`. 

REGULI GENERALE:
- Analizează textul și conectează TOATE componentele logic (nimic în aer). Fii atent sa nu lasi noduri orfane.
- Săgeți cu sens: `-->|text|` pt flux normal, `-.->|text|` pt asincron. FARA text pe linii de tip `---`.
"""

RULES_SOFTWARE = """
REGULI ARHITECTURĂ SOFTWARE:
- Desenează clar pipeline-ul cerut. Respectă ordinea fluxului de date.
- Culori (adaugate la final cu 'style ID fill:#HEX,color:#fff'): Albastru (#3366cc) pt procese/gateway, Portocaliu (#cc8800) pt Guardrails/Validări, Indigo (#4252b5) pt User/UI, Verde (#33cc33) pt Succes.
- Dacă promptul cere explicit o culoare (ex "tools in red"), aplic-o!
"""

RULES_FAMILY = """
REGULI ARBORE GENEALOGIC:
- Părinții sunt sus, copiii jos. Folosește STRICT `-->` de la părinți la copii. (ex: `N1[Mama] --> N3[Copil]`)
- Căsătorii/Cupluri: Conectează-i cu `---` (FĂRĂ ETICHETE, FĂRĂ TEXT PE LINIE! STRICT DOAR `---`). 
- Pentru familii/oameni foloseste culori calde. Fără forme de baze de date (fără cilindri) pentru oameni! Folosește doar dreptunghiuri cu pante drepte `[Nume]`.
"""

RULES_TRAVEL = """
REGULI ITINERARIU DE VACANȚĂ / CĂLĂTORIE:
- Folosește neapărat un ROMB pentru decizia meteorologică: `N5{Ninge?}`.
- Săgețile din decizie: `N5 -->|Da, ninge| N6[Praga]`, `N5 -->|Altfel| N7[Munchen]`.
- Adaugă text pe săgeți cu durata cerută (ex: `-->|3 nights|`, `-->|rest for 1 night|`).
- SARCINĂ CRITICĂ: INVENTEAZĂ tu ultima locație (ex: Viena, Salzburg) și conecteaz-o la final ca sugestie.
"""

RULES_TRANSFORMER = """
REGULI ARHITECTURA TRANSFORMER (Attention):
- Folosește subgrafuri pentru a separa vizual componentele majore: `subgraph Encoder` și `subgraph Decoder`.
- Encoder flow: Inputs -> Input Embedding -> Positional Encoding -> Multi-Head Attention -> Add & Norm -> Feed Forward -> Add & Norm.
- Decoder flow: Outputs -> Output Embedding -> Positional Encoding -> Masked Multi-Head Attention -> Add & Norm -> Multi-Head Attention (conectat și de la Encoder) -> Add & Norm -> Feed Forward -> Add & Norm -> Linear -> Softmax.
- Culori recomandate: Attention = Roșu deschis (#ff4d4d), Feed Forward = Albastru deschis (#4d94ff), Add & Norm = Galben (#ccaa00).
"""

def get_dynamic_prompt(user_text):
    text_lower = user_text.lower()
    prompt = BASE_PROMPT
    if "father" in text_lower or "brother" in text_lower or "family" in text_lower or "mom is" in text_lower or "gigel" in text_lower:
        prompt += RULES_FAMILY
    elif "vacation" in text_lower or "itinerary" in text_lower or "bucharest" in text_lower:
        prompt += RULES_TRAVEL
    elif "transformer" in text_lower or "attention is all you need" in text_lower:
        prompt += RULES_TRANSFORMER
    else:
        prompt += RULES_SOFTWARE
    return prompt

def tool_mermaid_generator(text_input: str) -> str:
    """Genereaza cod Mermaid dintr-o descriere textuala folosind un Agentic Router intern."""
    if not text_input or not text_input.strip():
        return "Eroare: textul de intrare este gol."

    prompt_activ = get_dynamic_prompt(text_input)

    try:
        raspuns = ollama.chat(
            model='gemma3:4b', 
            messages=[
              {'role': 'system', 'content': prompt_activ},
              {'role': 'user', 'content': text_input.strip()}
            ]
        )
        
        text_brut = raspuns['message']['content']
        
        # --- CURĂȚENIA ANTI-BOMBĂ A SINTAXEI ---
        # Stergem eventuale etichete ilegale de pe legaturile de casatorie (ex: ---|married|)
        text_brut = re.sub(r'---\|.*?\|', '---', text_brut)
        
        cod_mermaid = text_brut
        if "```mermaid" in cod_mermaid:
            cod_mermaid = cod_mermaid.split("```mermaid")[1].split("```")[0]
        elif "```" in cod_mermaid:
            cod_mermaid = cod_mermaid.split("```")[1].split("```")[0]
        
        cod_mermaid = cod_mermaid.replace("Here is the Mermaid code:", "").replace("Here is the diagram:", "")
        cod_mermaid = cod_mermaid.strip()
        
        if not cod_mermaid.startswith("graph") and not cod_mermaid.startswith("flowchart"):
            cod_mermaid = "graph TD\n" + cod_mermaid
            
        return cod_mermaid

    except Exception as e:
        return f"graph TD\n    Error[Eroare parsare AI: {str(e)[:50]}]\n    style Error fill:#ff4c4c,color:#fff"