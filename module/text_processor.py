import os
import argparse
import json
import spacy
from collections import Counter


def read_json(path):
    with open(path) as f:
        data = json.load(f)
    return data


def create_textFromList(list_):
    text_list = ""
    for i, v in enumerate(list_["results"]):
        text_list = text_list + " " + v["alternatives"][0]["transcript"]
    return text_list


def count_hestiation(text_list):
    counter = 0
    txt_ = []
    for i in text_list.split():
        if i != "%HESITATION":
            txt_.append(i)
        else:
            counter = counter + 1
    return counter, txt_


def remove_stopword(doc):
    return [token.text for token in doc if not token.is_stop]


def remove_punc(doc):
    return [token.text for token in doc if not token.is_punct]


def remove_all(doc):
    return [
        token.lemma_ for token in doc if not (token.is_punct) and not (token.is_stop)
    ]


def union_text(doc1, doc2):
    return [item for item in doc1 if item in doc2]


def calculate_word_frequency(nlp, txt_list):
    doc = nlp(txt_list)
    tokens_rm_stop = remove_stopword(doc)
    tokens_rm_punc = remove_punc(doc)
    union_txt = union_text(tokens_rm_stop, tokens_rm_punc)
    txt = ""
    for i in union_txt:
        txt = txt + " " + i
    doc2_ = nlp(txt)
    counts = Counter()
    for token in doc2_:
        counts[token.lemma_] += 1
    return counts.most_common(10)  # my_keys = [key for key, val in most_common]
