import pandas as pd
import torch
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.utils.data import Dataset, DataLoader
from pyngrok import ngrok
import uvicorn
import io
import re
import logging
import threading
import nest_asyncio

# Apply nest_asyncio for environments with existing event loops
nest_asyncio.apply()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(_name_)

# Initialize FastAPI app
app = FastAPI()

# Define batch size
BATCH_SIZE = 32

# Initialize models and tokenizers
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info("Loading classification models...")

sentiment_model_name = "j-hartmann/sentiment-roberta-large-english-3-classes"
sentiment_tokenizer = AutoTokenizer.from_pretrained(sentiment_model_name)
sentiment_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_name).to(device)

class16_model_path = "/kaggle/input/16class/transformers/default/1/modelout"
class16_tokenizer = AutoTokenizer.from_pretrained(class16_model_path)
class16_model = AutoModelForSequenceClassification.from_pretrained(class16_model_path).to(device)

logger.info("Models loaded successfully")

# Define label map for 16-class classifier
label_map = {
    "Accessibility": 0, "App Performance": 1, "Bans & Restrictions": 2, "Company Policies": 3,
    "Customer Support": 4, "Discounts & Offers": 5, "Driver Experience": 6, "Payment & Transactions": 7,
    "Pricing": 8, "Ratings & Reviews": 9, "Regulations & Legal": 10, "Ride Availability": 11,
    "Security": 12, "Sustainability & Environment": 13, "Trust & Safety": 14, "User Interface": 15
}
reverse_label_map = {v: k for k, v in label_map.items()}

# Custom Dataset class
class TextDataset(Dataset):
    def _init_(self, texts, tokenizer, max_length=384):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length

    def _len_(self):
        return len(self.texts)

    def _getitem_(self, idx):
        text = self.texts[idx]
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0)
        }

def preprocess_text(text):
    """Standard text preprocessing for NLP tasks"""
    text = str(text) if pd.notna(text) else ""
    text = re.sub(r'http\S+|www\S+', '', text)  # Remove URLs
    text = re.sub(r'[^a-zA-Z\s.,!?]', '', text)  # Keep letters and basic punctuation
    text = text.lower()  # Convert to lowercase
    text = ' '.join(text.split())  # Normalize whitespace
    return text

@app.post("/analyze_csv")
async def analyze_csv(file: UploadFile = File(...)):
    """Analyze CSV file for sentiment and 16-class classification using Dataset"""
    logger.info(f"Analyzing file: {file.filename}")
    
    try:
        # Read CSV file
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        # Preprocess text data
        df['text'] = df['text'].apply(preprocess_text)
        texts = df['text'].tolist()
        ids = df.get('id', [f"item_{i}" for i in range(len(df))]).tolist()
        review_ids = df.get('review_id', [None]*len(df)).tolist()

        # Create datasets
        sentiment_dataset = TextDataset(texts, sentiment_tokenizer)
        class16_dataset = TextDataset(texts, class16_tokenizer)

        # Create data loaders
        sentiment_loader = DataLoader(sentiment_dataset, batch_size=BATCH_SIZE, shuffle=False)
        class16_loader = DataLoader(class16_dataset, batch_size=BATCH_SIZE, shuffle=False)

        # Set models to evaluation mode
        sentiment_model.eval()
        class16_model.eval()

        # Process batches
        results = []
        with torch.no_grad():
            for (sentiment_batch, class16_batch), batch_ids, batch_review_ids in zip(
                zip(sentiment_loader, class16_loader), 
                [ids[i:i + BATCH_SIZE] for i in range(0, len(ids), BATCH_SIZE)],
                [review_ids[i:i + BATCH_SIZE] for i in range(0, len(review_ids), BATCH_SIZE)]
            ):
                # Move batches to device
                sentiment_inputs = {k: v.to(device) for k, v in sentiment_batch.items()}
                class16_inputs = {k: v.to(device) for k, v in class16_batch.items()}

                # Get predictions
                sentiment_outputs = sentiment_model(**sentiment_inputs)
                class16_outputs = class16_model(**class16_inputs)

                # Process sentiment predictions
                sentiment_probs = torch.nn.functional.softmax(sentiment_outputs.logits, dim=-1)
                sentiment_labels = sentiment_probs.argmax(dim=-1)
                sentiment_confidences = sentiment_probs.max(dim=-1).values

                # Process 16-class predictions
                class16_probs = torch.nn.functional.softmax(class16_outputs.logits, dim=-1)
                class16_labels = class16_probs.argmax(dim=-1)
                class16_confidences = class16_probs.max(dim=-1).values

                # Compile results
                for i in range(len(batch_ids)):
                    sentiment_label = sentiment_model.config.id2label[sentiment_labels[i].item()]
                    if sentiment_label.startswith("LABEL_"):
                        sentiment_label = sentiment_label[6:]

                    class16_label_idx = class16_labels[i].item()
                    category = reverse_label_map.get(class16_label_idx, f"Unknown_{class16_label_idx}")

                    results.append({
                        "id": batch_ids[i],
                        "review_id": batch_review_ids[i],
                        "text": texts[i][:200],
                        "sentiment": sentiment_label.lower(),
                        "sentiment_confidence": float(sentiment_confidences[i]),
                        "category": category,
                        "category_confidence": float(class16_confidences[i])
                    })

        # Generate CSV response
        output = io.StringIO()
        pd.DataFrame(results).to_csv(output, index=False)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=results.csv"}
        )

    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def start_ngrok():
    """Start ngrok tunnel in a separate thread"""
    try:
        ngrok.set_auth_token("2vOY40OJNTdX3vOUOcyMjAiN3F3_VrJBYHMNA9sFqc6JHgX6")
        tunnel = ngrok.connect(8000, "http")
        public_url = tunnel.public_url
        logger.info(f"Ngrok tunnel established at: {public_url}")
        print(f"Public URL: {public_url}")
        return public_url
    except Exception as e:
        logger.error(f"Error starting ngrok: {str(e)}")
        raise

def start_server():
    """Start FastAPI server with ngrok"""
    # Start ngrok tunnel first in a separate thread
    ngrok_thread = threading.Thread(target=start_ngrok)
    ngrok_thread.start()
    # Bind to localhost so ngrok can reach it
    uvicorn.run(app, host="127.0.0.1", port=8000)

if _name_ == "_main_":
    start_server()