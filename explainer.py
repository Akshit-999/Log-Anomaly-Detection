import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
import google.generativeai as genai
from config import EXPLAINER_MODEL

# Load environment variables
load_dotenv(override=True)

# Read from env ONLY (not from config.py)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini
USE_GEMINI = False
client = None
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    client = genai.GenerativeModel(EXPLAINER_MODEL)
    USE_GEMINI = True
    print("✅ GEMINI client initialized with key:", GEMINI_API_KEY[:8] + "…")
else:
    print("⚠️ No GEMINI_API_KEY found in .env, falling back to local mode")


# Define the template once
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

def build_prompt(sequence, score, tokens, token_importance):
    if token_importance is not None and len(token_importance) > 0:
        sorted_tokens = sorted(
            zip(tokens, token_importance),
            key=lambda x: x[1],
            reverse=True
        )
        token_str = ", ".join([f"{tok} ({imp:.2f})" for tok, imp in sorted_tokens])
    else:
        token_str = "N/A"

    seq_text = "\n".join([f"{i}. {t}" for i, t in enumerate(sequence[-20:])])

    return explanation_template.format(
        score=f"{score:.3f}",
        top_tokens=token_str,
        seq_text=seq_text
    )


def explain_with_GEMINI(prompt: str):
    resp = client.generate_content(prompt)
    return resp.text if resp and resp.text else "No response"


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
