# -*- coding: utf-8 -*-

!pip install datasets

from datasets import load_dataset

import pandas as pd

# Login using e.g. `huggingface-cli login` to access this dataset
df = pd.read_json("hf://datasets/isaacus/open-australian-legal-qa/qa.jsonl", lines=True)

df.head()

!pip install transformers datasets evaluate accelerate

# Drop the specified columns from the DataFrame
df.drop(columns=['text', 'prompt', 'source'], inplace=True)
df.head()

# Data cleaning
import re
import string

def clean_text(text):
    """Cleans the input text by applying several preprocessing steps."""

    # Step 1: Convert to lowercase
    text = text.lower()

    # Step 2: Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

    # Step 3: Remove numbers
    text = re.sub(r'\d+', '', text)

    # Step 4: Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Step 5: Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Step 6: Remove specific unwanted phrases (if necessary)
    # Example: text = text.replace("unwanted phrase", "")

    return text

def clean_data(df):
    """Applies the cleaning function to the 'question' and 'answer' columns."""
    # Clean the 'question' and 'answer' columns
    df['question'] = df['question'].apply(clean_text)
    df['answer'] = df['answer'].apply(clean_text)
    return df
    
# Apply the cleaning function to the DataFrame
cleaned_df = clean_data(df.copy()) # Create a copy to avoid modifying the original df in place

print("Data cleaning complete!")

# Format data for GPT-2: Input + Expected Output = One String using the cleaned data
cleaned_df["text"] = cleaned_df["question"].apply(lambda x: "Question: " + x.strip()) + "\nAnswer: " + cleaned_df["answer"].apply(lambda x: x.strip())

# Save to new CSV
cleaned_df[["text"]].to_csv("formatted_legal_qa.csv", index=False)

cleaned_df

#Apply Prompt Template
cleaned_df["text"] = cleaned_df.apply(
    lambda row: f"You are a legal assistant. Read the question and provide a clear and accurate answer.\n\nQuestion: {row['question']}\nAnswer: {row['answer']}",
    axis=1
)

cleaned_df["text"][0]

# converting cleaned_df into hugging face dataset to further tokinization
from datasets import Dataset
dataset = Dataset.from_pandas(cleaned_df[["text"]])
print(dataset)

print(dataset[0]) 
print(dataset[5])

# data splitting
dataset = Dataset.from_pandas(cleaned_df[["text"]])
dataset = dataset.train_test_split(test_size=0.1)

# Tokenize
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("gpt2", use_fast=True)
tokenizer.pad_token = tokenizer.eos_token  # Fix for GPT-2's missing pad token

def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        padding="max_length",
        truncation=True,
        max_length=512,
    )

tokenized_dataset = dataset.map(tokenize_function, batched=True)

from transformers import AutoTokenizer

model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token  # GPT-2 has no pad token

#Load GPT-2 Model
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("gpt2")
model.resize_token_embeddings(len(tokenizer))  # Adjust for pad token

# Training Arguments & Trainer
from transformers import TrainingArguments, Trainer, DataCollatorForLanguageModeling

training_args = TrainingArguments(
    output_dir="./gpt2-legal-finetuned",
    overwrite_output_dir=True,
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    num_train_epochs=10,
    logging_steps=10,
    save_strategy="epoch",
    eval_strategy="epoch",
    fp16=True,  
    logging_dir="./logs",
)

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["test"],
    tokenizer=tokenizer,
    data_collator=data_collator,
)

# Train the model
trainer.train()

trainer.save_model("./gpt2-legal-finetuned")
tokenizer.save_pretrained("./gpt2-legal-finetuned")

from transformers import AutoTokenizer, AutoModelForCausalLM

model_path = "./gpt2-legal-finetuned"

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path)

import evaluate
bleu = evaluate.load("bleu")

sample = dataset["test"][1]["text"].split("Answer:")[1] + "Answer:"
reference = dataset["test"][1]["text"].split("Answer:")[1].strip()

inputs = tokenizer(sample, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=250, do_sample=False)

generated_answer = tokenizer.decode(outputs[0], skip_special_tokens=True).split("Answer:")[1].strip()
bleu_score = bleu.compute(predictions=[generated_answer], references=[[reference]])

print("Generated Answer:", generated_answer)
print("BLEU Score:", bleu_score)

import torch
import math

def compute_perplexity(text):
    encodings = tokenizer(text, return_tensors="pt")
    max_length = model.config.n_positions

    stride = 512
    nlls = []

    for i in range(0, encodings.input_ids.size(1), stride):
        begin_loc = max(i + stride - max_length, 0)
        end_loc = i + stride
        input_ids = encodings.input_ids[:, begin_loc:end_loc]
        target_ids = input_ids.clone()

        with torch.no_grad():
            outputs = model(input_ids, labels=target_ids)
            neg_log_likelihood = outputs.loss * (end_loc - begin_loc)

        nlls.append(neg_log_likelihood)

    ppl = torch.exp(torch.stack(nlls).sum() / end_loc)
    return ppl.item()

# Example
print("Perplexity:", compute_perplexity(dataset["test"][0]["text"]))

"""### The model demonstrates a decent performance with a BLEU score of 0.442, 
indicating moderate quality. The consistency in n-gram precision is a positive sign, 
although the excessive translation length suggests that the output may need refinement to achieve conciseness without losing meaning.
"""

def generate_answer(question):
    prompt = f"You are a legal assistant. Read the question and provide a clear and accurate answer.\n\nQuestion: {question}\nAnswer:"
    inputs = tokenizer(prompt, return_tensors="pt")

    outputs = model.generate(
        **inputs,
        max_new_tokens=250,
        do_sample=False,
        temperature=0.7,
        top_k=5,
        pad_token_id=tokenizer.eos_token_id
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.split("Answer:")[1].strip()

# Example
question = "What was the decision in R v NGUYEN [2001]?"
print("Answer:", generate_answer(question))






