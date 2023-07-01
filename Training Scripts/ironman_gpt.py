# -*- coding: utf-8 -*-
"""ironman_gpt.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kDXIMutlfubWe98qN0KsSlCqs0tcMVbA
"""

import locale
def getpreferredencoding(do_setlocale = True):
    return "UTF-8"
locale.getpreferredencoding = getpreferredencoding

!pip install transformers==4.28.0

input_path="FullScript.txt"

with open (input_path,'r',encoding='utf-8') as f:
  text=f.read();

import re
def extract_tony_conversations(excerpt):
    lines = excerpt.strip().split('\n')
    tony_conversations = []
    current_conversation = []

    for line in lines:
        if re.match(r"Tony Stark:", line):
            if current_conversation:
                if re.match(r"Tony Stark:", current_conversation[-1]):
                    tony_conversations.append('\n'.join(current_conversation))
                else:
                    current_conversation.append(line)
                    tony_conversations.append('\n'.join(current_conversation))
                current_conversation = []
            else:
                current_conversation.append(line)
        else:
            current_conversation.append(line)

    if current_conversation and re.match(r"Tony Stark:", current_conversation[-1]):
        tony_conversations.append('\n'.join(current_conversation))

    return tony_conversations

ds=extract_tony_conversations(text)

len(ds)

from sklearn.model_selection import train_test_split

train_ls,test_ls=train_test_split(ds,test_size=0.1,random_state=1)

from google.colab import drive
drive.mount('/content/drive')

from transformers import GPT2Tokenizer
from transformers import GPT2LMHeadModel

tokenizer=GPT2Tokenizer.from_pretrained('gpt2')
model=GPT2LMHeadModel.from_pretrained('gpt2')

tokenizer.add_special_tokens({"pad_token": "<pad>",
                                "bos_token": "<|SOS|>",
                                "eos_token": "<|EOS|>"})
tokenizer.add_tokens(["<|IronMan|>:"])

model.resize_token_embeddings(len(tokenizer))

tokenizer

from transformers import DataCollatorForLanguageModeling
data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer,mlm=False,return_tensors='pt' )

model

def preprocess(ds):
  new_ds = [conv.replace("Tony Stark:", "<|IronMan|>:") for conv in ds]
  for index,conv in enumerate(new_ds):
    temp="<|SOS|>"+conv+"<|EOS|>"
    new_ds[index]=temp
  return new_ds

train_ls=preprocess(train_ls)

test_ls=preprocess(test_ls)

train_ls

max_length=512

from torch.utils.data import Dataset

class MyDataset(Dataset):
    def __init__(self, data, tokenizer, max_length):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        encoding = self.tokenizer(self.data[idx], max_length=self.max_length, truncation=True, padding='max_length', return_tensors='pt')
        return {'input_ids': encoding['input_ids'].squeeze(), 'attention_mask': encoding['attention_mask'].squeeze()}

train_ds = MyDataset(train_ls, tokenizer, max_length)
test_ds =MyDataset(test_ls,tokenizer,max_length)

output_path="./results"

from transformers import Trainer, TrainingArguments

# Define the training arguments, including the output directory for saving the model
training_args = TrainingArguments(
    output_dir=output_path,
    save_total_limit=1,  # Limit the total amount of saved models to 5
    save_steps=500,  # Evaluate the model every 100 steps
    eval_steps=100,  # Evaluate the model every 100 steps
    learning_rate=1e-4,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=30,
)

# Instantiate the Trainer object and start training
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_ds,
    eval_dataset=test_ds,
    data_collator=data_collator,  # Define the data collator here if necessary
    tokenizer=tokenizer
)

trainer.train()

import zipfile
import os

def zip_folder(folder_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                zip_file.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(folder_path, '..')))

folder_path = '/results/checkpoint-6000'
output_path = '/content/drive/MyDrive/Models/Iron Man/model.zip'
zip_folder(folder_path, output_path)

import torch
device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

print("Infer from model : ")
while True:
  inp = input()
  print(infer(inp))

def infer(inp):
    inp = "<|SOS|> "+inp+"<|Rick|>:"
    inp = tokenizer(inp, return_tensors="pt")
    X = inp["input_ids"].to(device)
    a = inp["attention_mask"].to(device)
    output = model.generate(X, attention_mask=a )
    output = tokenizer.decode(output[0])
    return output

