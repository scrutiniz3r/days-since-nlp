# days-since-nlp
{Fine-tuned intent + entity extraction for the NLP logging feature} for days-since application
# Days Since — NLP Logging Feature

Natural language intent classification and entity extraction for the Days Since habit tracker.

## Task

Convert free-form speech/text into structured activity log entries.

**Input:** `"I did football 5 days ago"`  
**Output:**
```json
{
  "intent": "log_entry",
  "activity": "Football",
  "days_ago": 5,
  "is_new": false,
  "label": null
}
```

## Intents

| Intent | Description | Example |
|---|---|---|
| `log_entry` | User logged a completed activity | "Did cricket today" |
| `new_activity` | User wants to create a new tracking item | "Add yoga to my list" |
| `assign_label` | User wants to label an activity | "Put football under sport" |
| `unclear` | Not enough info to act | "hmm", "hello" |

## Project Structure

```
data/
  dataset.jsonl        # 100 hand-labeled examples
  train.jsonl          # 70% split
  val.jsonl            # 15% split
  test.jsonl           # 15% split

notebooks/
  01_explore.ipynb     # Data exploration and stats
  02_baseline.ipynb    # Rule-based regex baseline
  03_train.ipynb       # Fine-tune DistilBERT for intent
  04_eval.ipynb        # Evaluation + confusion matrix

src/
  split.py             # Train/val/test split script
  predict.py           # Inference wrapper
  extract_entities.py  # Activity name + days_ago extraction

models/
  intent_classifier/   # Saved fine-tuned model
```

## Approach

**Stage 1 — Intent Classification**  
Fine-tune `distilbert-base-uncased` on the labeled dataset to classify input into one of 4 intents. Small, fast, deployable.

**Stage 2 — Entity Extraction**  
Rule-based + spaCy NER to extract `activity` name and `days_ago` from the raw text. Regex handles date expressions ("5 days ago", "yesterday", "last week").

**Stage 3 — Baseline Comparison**  
Compare fine-tuned model against a regex rule-based parser on the held-out test set. Report accuracy and F1 per class.

## Setup

```bash
pip install transformers datasets scikit-learn torch spacy
python -m spacy download en_core_web_sm
python src/split.py
```

Then open `notebooks/03_train.ipynb` in Google Colab (free GPU).

## Results

| Model | Accuracy | F1 (macro) |
|---|---|---|
| Rule-based baseline | TBD | TBD |
| DistilBERT fine-tuned | TBD | TBD |
