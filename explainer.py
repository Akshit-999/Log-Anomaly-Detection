import os
import logging
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
import google.generativeai as genai
from config import EXPLAINER_MODEL


# Logging setup
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


# Load environment variables
load_dotenv(override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# Initialize Gemini
USE_GEMINI = False
client = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        client = genai.GenerativeModel(EXPLAINER_MODEL)
        USE_GEMINI = True
        logging.info(f"✅ GEMINI client initialized with key: {GEMINI_API_KEY[:8]}…")
    except Exception as e:
        logging.error(f"❌ Failed to init Gemini: {e}")
else:
    logging.warning("⚠️ No GEMINI_API_KEY found in .env, falling back to local mode")


# Prompt template
explanation_template = PromptTemplate(
    input_variables=["score", "top_tokens", "seq_text"],
    template="""An anomaly detector flagged the following log sequence with anomaly score {score}.
                Provide a concise explanation of the most likely root cause, things to check (config/metrics), and a short remediation plan.
                Highlight which tokens/parts of the sequence are important: {top_tokens}

                Log sequence:
                {seq_text}

                Answer in bullet points: cause, evidence, checks, remediation (2-3 lines each).
                """
                )


# Helpers
def build_prompt(sequence, score, tokens, token_importance, max_tokens: int = 15):
    if token_importance is not None and len(token_importance) > 0:
        sorted_tokens = sorted(
            zip(tokens, token_importance),
            key=lambda x: x[1],
            reverse=True
        )
        token_str = ", ".join([f"{tok} ({imp:.2f})" for tok, imp in sorted_tokens[:max_tokens]])
    else:
        token_str = "N/A"

    seq_text = "\n".join([f"{i}. {t}" for i, t in enumerate(sequence[-20:])])

    return explanation_template.format(
        score=f"{score:.3f}",
        top_tokens=token_str,
        seq_text=seq_text
    )

def explain_with_GEMINI(prompt: str):
    try:
        resp = client.generate_content(prompt)
        return resp.text if resp and resp.text else "⚠️ Gemini returned empty response"
    except Exception as e:
        return f"⚠️ Gemini API error: {str(e)}"


# Main entry point
def explain(sequence, score, tokens, token_importance):
    prompt = build_prompt(sequence, score, tokens, token_importance)
    if USE_GEMINI:
        return explain_with_GEMINI(prompt)
    else:
        # fallback: simple heuristic explanation
        top_tokens = []
        if token_importance is not None:
            top_idx = sorted(range(len(token_importance)), key=lambda i: token_importance[i], reverse=True)[:5]
            top_tokens = [tokens[i] for i in top_idx]
        return f"(No LLM key) Heuristics: high importance tokens {top_tokens}. Score {score:.3f}."
