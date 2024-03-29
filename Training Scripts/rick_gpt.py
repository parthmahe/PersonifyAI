# -*- coding: utf-8 -*-
"""rick-gpt.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12UJvLmqFqnRfD33ovAxBkO8y_DseB1G8
"""

!pip install transformers==4.28.0

INPUT_PATH="/kaggle/input/rick-and-morty-full-script-txt/Rick-Final.txt"
with open (INPUT_PATH,'r') as f:
  text=f.read();

import re

ds=re.findall(r".+:.+\nRick:.+|Rick:.+",text)

len(ds)

from sklearn.model_selection import train_test_split

train_ls,test_ls=train_test_split(ds,test_size=0.1,random_state=42,shuffle=False)

from transformers import GPT2Tokenizer
from transformers import GPT2LMHeadModel

tokenizer=GPT2Tokenizer.from_pretrained('gpt2')
model=GPT2LMHeadModel.from_pretrained('gpt2')

tokenizer.add_special_tokens({"pad_token": "<pad>",
                                "bos_token": "<|SOS|>",
                                "eos_token": "<|EOS|>"})
tokenizer.add_tokens(["<|Rick|>:"])

model.resize_token_embeddings(len(tokenizer))

tokenizer

from transformers import DataCollatorForLanguageModeling
data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer,mlm=False,return_tensors='pt' )

model

def preprocess_ds(ds):
  for idx,i in enumerate(ds):
    txt=i.split('\n')
    if len(txt)==1:
      colonidx=txt[0].find(":")
      ds[idx]="<|SOS|>"+"<|Rick|>:"+txt[0][colonidx+1:]+"<|EOS|>"
    else:
      s=""
      colonidx0=txt[0].find(":")
      colonidx1=txt[1].find(":")
      temp1=txt[0][colonidx0+1:]
      temp2="<|Rick|>:"+txt[1][colonidx1+1:]
      if txt[0][:colonidx0]=="Rick":
        s="<|SOS|>"+"<|Rick|>"+temp1+temp2+"<|EOS|>"
      else:
        s="<|SOS|>"+temp1+temp2+"<|EOS|>"
      ds[idx]=s
  return ds

train_ls1=preprocess_ds(train_ls)
test_ls1=preprocess_ds(test_ls)

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

train_ds = MyDataset(train_ls1, tokenizer, max_length)
test_ds =MyDataset(test_ls1,tokenizer,max_length)

from transformers import Trainer, TrainingArguments

# Define the training arguments, including the output directory for saving the model
training_args = TrainingArguments(
    output_dir='./results',
    save_total_limit=1,  # Limit the total amount of saved models to 5
    save_steps=500,  # Evaluate the model every 100 steps
    eval_steps=100,  # Evaluate the model every 100 steps
    learning_rate=1e-4,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=20,
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

folder_path = '/kaggle/working/results'
output_path = '/kaggle/working/results.zip'
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

trainer.save_best_model()
best_model_checkpoint = trainer.best_model_checkpoint

import zipfile
import os

# Define the path to the directory where you want to save the zipped model
save_path = "/content/drive/MyDrive/Models/Sherlock"

# Define the name for the zipped model
zip_name = "Sherlock.zip"

# Zip the best model checkpoint
with zipfile.ZipFile(os.path.join(save_path, zip_name), mode='w') as zip_file:
    zip_file.write(best_model_checkpoint, os.path.basename(best_model_checkpoint))

import torch
torch.cuda.empty_cache()

print(torch.cuda.memory_summary(device='cuda', abbreviated=False))

