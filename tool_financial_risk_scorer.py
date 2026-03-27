"""
Tool: Financial Sentiment & Risk Scorer
Hackathon Domain: Quant / Finance
Local inference via ollama (phi3) — no external API keys needed.

Cum functioneaza:
  - Primeste un text financiar (stire, raport, mesaj de user)
  - Llama3 este fortat prin prompt de sistem sa returneze DOAR un bloc JSON valid
  - JSON-ul contine: sentiment, risk_score, volatility_flag, key_entities, one_line_summary
  - Functia parseaza JSON-ul si returneaza un string formatat frumos pentru orchestrator
"""

import ollama
import json
import re


# ---------------------------------------------------------------------------
# SYSTEM PROMPT — testat pentru a elimina halucinatiile si text suplimentar
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a quantitative financial risk analyst AI.
Your ONLY job is to analyze the financial text provided and return a single, valid JSON object.

STRICT RULES:
1. Output ONLY the JSON object. No markdown, no code fences, no explanation, no prose.
2. The JSON must have exactly these keys:
   - "sentiment": one of ["BULLISH", "BEARISH", "NEUTRAL"]
   - "risk_score": integer from 1 (very low risk) to 10 (extreme risk)
   - "volatility_flag": boolean true/false
   - "key_entities": list of up to 5 strings (company names, tickers, assets, or macro events mentioned)
   - "one_line_summary": string, max 20 words, describing the core financial event or signal
3. If the text is unrelated to finance, still return the JSON with sentiment "NEUTRAL", risk_score 1, volatility_flag false, empty key_entities, and one_line_summary "Non-financial input detected."
4. Do NOT add trailing commas or comments inside the JSON.
5. Do NOT wrap the JSON in ```json or any other delimiters.

Example of a VALID response:
{"sentiment":"BEARISH","risk_score":8,"volatility_flag":true,"key_entities":["FED","S&P500","inflation","Treasury yields"],"one_line_summary":"Fed signals aggressive rate hikes amid rising inflation fears."}"""


# ---------------------------------------------------------------------------
# TOOL FUNCTION
# ---------------------------------------------------------------------------
def tool_financial_risk_scorer(text_input: str) -> str:
    """
    Analizeaza un text financiar si returneaza un scor de risc structurat (JSON).

    Args:
        text_input: Textul financiar de analizat (stire, raport, intrebare user).

    Returns:
        String formatat cu rezultatele analizei, gata de printat de orchestrator.
    """
    if not text_input or not text_input.strip():
        return "[FinancialRiskScorer] Eroare: textul de intrare este gol."

    try:
        response = ollama.chat(
            model="phi3",
            format="json",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze this financial text:\n\n{text_input.strip()}"},
            ],
            options={
                "temperature": 0.1,   # aproape determinist — consistent, fara creativitate
                "top_p": 0.9,
                "num_predict": 300,   # suficient pentru JSON, dar limitat pt a taia verbozitatea
            },
        )

        raw_output = response["message"]["content"].strip()

        # Acum putem parsa direct, ollama forteaza output sa fie JSON
        data = json.loads(raw_output)

        # --- Validare chei obligatorii ---
        required_keys = {"sentiment", "risk_score", "volatility_flag", "key_entities", "one_line_summary"}
        missing = required_keys - data.keys()
        if missing:
            return f"[FinancialRiskScorer] JSON incomplet — lipsesc cheile: {missing}\nOutput brut: {raw_output}"

        # --- Formatare output pentru orchestrator ---
        risk_bar = _risk_bar(data["risk_score"])
        entities_str = ", ".join(data["key_entities"]) if data["key_entities"] else "N/A"
        volatility_str = "⚠️  DA" if data["volatility_flag"] else "✅ NU"

        result = (
            f"\n{'='*52}\n"
            f"  📊 FINANCIAL RISK SCORER — Rezultat Analiza\n"
            f"{'='*52}\n"
            f"  Sentiment      : {data['sentiment']}\n"
            f"  Scor de Risc   : {data['risk_score']}/10  {risk_bar}\n"
            f"  Volatilitate   : {volatility_str}\n"
            f"  Entitati cheie : {entities_str}\n"
            f"  Rezumat        : {data['one_line_summary']}\n"
            f"{'='*52}\n"
        )
        return result

    except json.JSONDecodeError as e:
        return f"[FinancialRiskScorer] Eroare JSON parsing: {e}\nOutput brut: {raw_output}"
    except ollama.ResponseError as e:
        return f"[FinancialRiskScorer] Eroare ollama (modelul nu ruleaza?): {e}"
    except Exception as e:
        return f"[FinancialRiskScorer] Eroare neasteptata: {e}"


def _risk_bar(score: int) -> str:
    """Genereaza o bara vizuala pentru scorul de risc (1-10)."""
    score = max(1, min(10, score))
    filled = "█" * score
    empty = "░" * (10 - score)
    return f"[{filled}{empty}]"


# ---------------------------------------------------------------------------
# DEMO — ruleaza direct cu: python tool_financial_risk_scorer.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Un singur test rapid pentru verificare
    test_text = (
        "The Federal Reserve unexpectedly raised interest rates by 75 basis points. "
        "Treasury yields surged to 4.8%, and the S&P 500 dropped 3.2% in after-hours trading. "
        "Analysts warn of a potential recession in Q1 2025."
    )

    print("Se incarca modelul phi3 local... (poate dura 30-60 sec, nu opri!)")
    print(f"Input: {test_text[:80]}...\n")

    result = tool_financial_risk_scorer(test_text)
    print(result)
