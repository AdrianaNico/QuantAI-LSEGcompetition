# QuantChallenge 2026 - Agentic Diagram Workflow

**Descriere:**
O aplicație robustă, care rulează 100% local, concepută pentru a transforma textul liber în diagrame Mermaid.js perfect randate (Arhitectură IT, Arbori Genealogici, Itinerarii de Vacanță). 

## Funcționalități Avansate (Pentru Extra Puncte la Jurizare)

1. **Smart Agentic Router**: Preluăm textul primit și detectăm automat tipul problemei. Nu folosim un prompt „orb” pentru toate cererile! Injectăm dinamic reguli specifice pentru forma și culoarea elementelor în funcție de domeniu (ex: IT vs. Familie vs. Turism). 
2. **Regex Sanitation (Crash-Proof Pipeline)**: LLM-urile mici greșesc des sintaxa de desenat grafice. Noi am pus un filtru inteligent direct în Python care curăță și repară toate alucinațiile codului (cum ar fi spații în ID-uri sau etichete invalide), astfel încât diagrama nu va pica NICIODATĂ la randare pe platforma web.
3. **Structură "Plug-and-Play"**: Vine cu `.bat`-uri preconfigurate pentru o pornire super-simplă de către utilizatori, rulând modelul eficient pe resurse interne, fără API-uri externe.

---

## Cum rulezi
1. Asigură-te că ai reinstalat [Ollama](https://ollama.com/) și ai descărcat modelul (`ollama run gemma3:4b`).
2. Dublu-click pe fișierul `run_app.bat`.
3. Introduceți fraza dorită și vizualizați diagrama generată automat!
