import json
import random
from transformers import GPT2Tokenizer
from transformers import GPT2LMHeadModel
import flask


SHERLOCK="Models/Sherlock-Model"
SHELDON="Models/Sheldon-Model"
IRONMAN="Models/IronMan-Model"
RICK="Models/Rick-Model"




sherlock_tokenizer=GPT2Tokenizer.from_pretrained(SHERLOCK)
sherlock_model=GPT2LMHeadModel.from_pretrained(SHERLOCK)


sheldon_tokenizer=GPT2Tokenizer.from_pretrained(SHELDON)
sheldon_model=GPT2LMHeadModel.from_pretrained(SHELDON)


ironman_tokenizer=GPT2Tokenizer.from_pretrained(IRONMAN)
ironman_model=GPT2LMHeadModel.from_pretrained(IRONMAN)



rick_tokenizer=GPT2Tokenizer.from_pretrained(RICK)
rick_model=GPT2LMHeadModel.from_pretrained(RICK)





def preprocess_sherlock(sentence):
    inp = "<|SOS|> "+sentence+"<|Sherlock|>:"
    return inp

def preprocess_ironman(sentence):
    inp = "<|SOS|> "+sentence+"<|IronMan|>:"
    return inp

def preprocess_rick(sentence):
    inp = "<|SOS|> "+sentence+"<|Rick|>:"
    return inp

def preprocess_sheldon(sentence):
    inp = "<|SOS|> "+sentence+"<|Sheldon|>:"
    return inp



def sherlock_response(inp):
    preprocess_sherlock(inp)
    inp = sherlock_tokenizer(inp, return_tensors="pt")
    X = inp["input_ids"]
    a = inp["attention_mask"]
    output = sherlock_model.generate(X, attention_mask=a )
    output = sherlock_tokenizer.decode(output[0])
    return output

def sheldon_response(inp):
    preprocess_sheldon(inp)
    inp = sheldon_tokenizer(inp, return_tensors="pt")
    X = inp["input_ids"]
    a = inp["attention_mask"]
    output = sheldon_model.generate(X, attention_mask=a )
    output = sheldon_tokenizer.decode(output[0])
    return output

def ironman_response(inp):
    preprocess_ironman(inp)
    inp = ironman_tokenizer(inp, return_tensors="pt")
    X = inp["input_ids"]
    a = inp["attention_mask"]
    output = ironman_model.generate(X, attention_mask=a )
    output = ironman_tokenizer.decode(output[0])
    return output

def rick_response(inp):
    preprocess_rick(inp)
    inp = rick_tokenizer(inp, return_tensors="pt")
    X = inp["input_ids"]
    a = inp["attention_mask"]
    output = rick_model.generate(X, attention_mask=a )
    output = rick_tokenizer.decode(output[0])
    return output


from flask import Flask, render_template, request

app = Flask(__name__)
app.static_folder = 'static'

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return sherlock_response(userText)


if __name__ == "__main__":
    app.run(debug=True)