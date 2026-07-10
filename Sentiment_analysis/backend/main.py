from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for local demo, restrict later
    allow_methods=["*"],
    allow_headers=["*"],
)

tokenizer = AutoTokenizer.from_pretrained("sentiment_model")
model = AutoModelForSequenceClassification.from_pretrained("sentiment_model")
model.eval()

labels = ["negative", "positive"]  # adjust to your label mapping

class TextIn(BaseModel):
    text: str

@app.post("/predict")
def predict(data: TextIn):
    inputs = tokenizer(data.text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=1)[0]
    pred_idx = torch.argmax(probs).item()
    return {
        "label": labels[pred_idx],
        "confidence": round(probs[pred_idx].item(), 4)
    }