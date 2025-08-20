from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModel
import torch
import torch.nn.functional as F
from typing import List, Dict, Any

import numpy as np
from fetch_logs import tail_file
import json

from dotenv import load_dotenv
import os

from config import LOGBERT_MODEL, DRAIN_DEPTH, DRAIN_SIMILARITY




class LogBERTInference:
    def __init__(self, model_name=LOGBERT_MODEL, device=None):
        # pick device
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        try:
            # Try classification head
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                output_attentions=True,
                device_map="auto"  # <-- handles meta tensors safely
            )
            self.has_classifier = True
        except Exception:
            # Fallback to base model
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(
                model_name,
                output_attentions=True,
                device_map="auto"
            )
            self.has_classifier = False

        print(f"✅ Model loaded on {self.device}, classifier head: {self.has_classifier}")

    def sequence_to_text(self, sequence: List) -> str:
        """
        Convert a sequence of logs into a single text string for LogBERT.
        Supports:
        - Structured tuples: (ts, template, template_id, raw)
        - Raw strings
        """
        parts = []
        for item in sequence:
            if isinstance(item, tuple):
                # Expect tuple format: (timestamp, template, template_id, raw)
                try:
                    _, template, tid, _ = item
                    parts.append(f"[TID:{tid}] {template}")
                except Exception:
                    # If tuple shape is unexpected, just join all parts
                    parts.append(" ".join(str(x) for x in item))
            elif isinstance(item, str):
                # Raw log string
                parts.append(item)
            else:
                # Fallback: string conversion of whatever type
                parts.append(str(item))
        return " <sep> ".join(parts)


    def infer(self, sequence: List[tuple]) -> Dict[str, Any]:
        text = self.sequence_to_text(sequence)
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=1024).to(self.device)
        # forward with attentions
        with torch.no_grad():
            outputs = self.model(**inputs, output_attentions=True)
        # get attentions
        attentions = None
        if hasattr(outputs, "attentions"):
            # attentions: tuple(layer: (batch, heads, seq_len, seq_len))
            attentions = [a.detach().cpu().numpy() for a in outputs.attentions]

        # get anomaly score
        if self.has_classifier and hasattr(outputs, "logits"):
            logits = outputs.logits.detach().cpu()
            # some logBERT variants use single output with sigmoid or 2-class
            if logits.shape[-1] == 1:
                score = torch.sigmoid(logits).item()
            else:
                probs = F.softmax(logits, dim=-1)
                # assume class 1 is anomaly
                score = probs[0, 1].item() if probs.shape[-1] > 1 else probs[0, 0].item()
        else:
            # fallback heuristic: use embedding norm or CLS token similarity
            last_hidden = outputs.last_hidden_state.detach().cpu()  # (1, seq_len, dim)
            # simple heuristic: mean of CLS token vector magnitude
            score = float(last_hidden[0,0].norm().item())  # not normalized; map to 0-1
            # normalize to 0-1 using a running min-max or a fixed scale; we'll clamp later
            # for simplicity, map via tanh
            score = float((np.tanh(score/10.0) + 1.0) / 2.0)

        # produce token-level importance by aggregating attentions from last layer
        token_importance = None
        if attentions:
            # average heads in last layer, aggregate over heads and tokens
            last_layer = attentions[-1]  # shape (batch, heads, seq, seq)
            avg_over_heads = last_layer.mean(axis=1)[0]  # (seq, seq)
            # importance by sum of attention directed to each token
            token_importance = avg_over_heads.sum(axis=0)  # shape (seq,)
            # normalize to 0-1
            token_importance = (token_importance - token_importance.min()) / (token_importance.ptp() + 1e-12)

        return {
            "score": max(0.0, min(1.0, score)),
            "text": text,
            "attentions": attentions,
            "token_importance": token_importance,
            "tokens": self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0].cpu().tolist())
        }






# Example usage:
# inf = LogBERTInference()
# res = inf.infer(sequence)
# print(res['score'])