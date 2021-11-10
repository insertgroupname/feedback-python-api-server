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
        text_list = text_list + " " + v["transcript"]
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


def remove_all(doc, custom_stopword=[]):
    rm = [token.lemma_ for token in doc if not (token.is_punct) and not (token.is_stop)]
    default_stop_list = [" "]
    combine_stopword = [*default_stop_list, *custom_stopword]
    rm = [t.lower() for t in rm if t not in combine_stopword]
    return rm # logic ยังผิด *** 


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


def stt(sound_file):
    import torch
    import zipfile
    import torchaudio
    from omegaconf import OmegaConf
    from glob import glob

    device = torch.device(
        "cpu"
    )  # gpu also works, but our models are fast enough for CPU
    model, decoder, utils = torch.hub.load(
        repo_or_dir="snakers4/silero-models",
        model="silero_stt",
        language="en",  # also available 'de', 'es'
        device=device,
    )
    (
        read_batch,
        split_into_batches,
        read_audio,
        prepare_model_input,
    ) = utils  # see function signature for details

    test_files = glob(sound_file)
    batches = split_into_batches(test_files, batch_size=100)
    input = prepare_model_input(read_batch(batches[0]), device=device)

    output = model(input)
    res_list = []
    for example in output:
        res_list = decoder(example.cpu())

    return res_list
