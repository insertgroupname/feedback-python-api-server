from contextlib import redirect_stdout
import nltk
import os
import argparse
import json
import spacy
from collections import Counter
import text_processor as tp
import time


def process_nlp(filename):
    start_process_time = time.time()
    filename = filename.split(".")[0]
    transcript_path = os.path.join("trancript", filename)
    file_ = tp.read_json(transcript_path)

    text_list = tp.create_textFromList(file_)
    hes_cnt, hes_txt_ = tp.count_hestiation(text_list)

    output_json = {}
    t = ""
    for i in hes_txt_:
        t = t + " " + i

    wpm_list = []
    for i, v in enumerate(file_["results"]):
        list_ = v["alternatives"][0]["timestamps"]
        for i in list_:
            wpm_list.append(i)

    wpm_dict = {}
    for i in range(0, int(wpm_list[-1][2] + 1), 60):
        wpm_dict[f"{i}-{i+60}"] = {"wpm": 0, "words": []}
        for j, v in enumerate(wpm_list):
            if (v[2] > i) & (v[2] < i + 60):
                wpm_dict[f"{i}-{i+60}"]["words"].append(v)
        wpm_dict[f"{i}-{i+60}"]["wpm"] = len(wpm_dict[f"{i}-{i+60}"]["words"])

    silence_list = []
    for i, v in enumerate(wpm_list):
        # Count Silence Period
        if i == len(wpm_list) - 1:
            break
        if v[2] != wpm_list[i + 1][1]:
            silence_time = wpm_list[i + 1][1] - v[2]
            e = {
                "silence_period": silence_time,
                "silence_start": v[2],
                "silence_end": wpm_list[i + 1][1],
            }
            silence_list.append(e)

    nlp = spacy.load("en_core_web_lg")
    doc_ = nlp(t)
    txt_rm_stop = tp.remove_all(doc_)
    print(tp.calculate_word_frequency(nlp, text_list))

    # run nltk.download() if there are files missing
    # nltk.download()

    words_fd = nltk.FreqDist(txt_rm_stop)
    bigram_fd = nltk.FreqDist(nltk.bigrams(txt_rm_stop))

    output_json["hestiation_"] = {"marker": {}, "total_count": {}}
    # output_json["hestiation_"]["marker"] = hes_txt_
    output_json["hestiation_"]["total_count"] = hes_cnt
    output_json["word_frequency"] = {"word": {}, "bigram": {}}
    output_json["word_frequency"]["word"] = words_fd.most_common(15)
    output_json["word_frequency"]["bigram"] = bigram_fd.most_common(10)
    output_json["wpm"] = wpm_dict
    output_json["silence"] = silence_list
    output_json["start_process_time"] = start_process_time
    output_json["end_process_time"] = time.time()

    return output_json