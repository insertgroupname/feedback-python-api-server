from contextlib import redirect_stdout
import nltk
import os
import argparse
import json
import spacy
from collections import Counter
import module.text_processor as tp
import time
from module.db import Database


def process_nlp(videoUUID):
    start_process_time = time.time()
    filename = videoUUID.split(".")[0] + ".json"
    transcript_path = os.path.join("transcript", filename)
    file_ = tp.read_json(transcript_path)

    text_list = tp.create_textFromList(file_)
    hes_cnt, hes_txt_ = tp.count_hestiation(text_list)

    output_json = {}
    t = ""
    for i in hes_txt_:
        t = t + " " + i

    # Concat every words in every chunks
    wpm_list = []
    for i, v in enumerate(file_["results"]):
        list_ = v["timestamps"]
        for i in list_:
            wpm_list.append(i)

    # Count WPM
    wpm_dict = {}
    avg_wpm = 0
    count_min = 0
    total = 0
    for i in range(0, int(wpm_list[-1][2] + 1), 60):
        wpm_dict[f"{i}-{i+60}"] = {"wpm": 0, "words": []}
        count_min += 1
        for j, v in enumerate(wpm_list):
            if (v[2] > i) & (v[2] < i + 60):
                wpm_dict[f"{i}-{i+60}"]["words"].append(v)
        wpm_dict[f"{i}-{i+60}"]["wpm"] = len(wpm_dict[f"{i}-{i+60}"]["words"])
        total += len(wpm_dict[f"{i}-{i+60}"]["words"])

    avg_wpm = total / count_min

    # Count Silence Period
    silence_dict = {"total_silence": 0, "silence_list": []}
    silence_duration_count = 0
    silence_list = []
    for i, v in enumerate(wpm_list):
        if i == len(wpm_list) - 1:
            break
        if v[2] != wpm_list[i + 1][1]:
            silence_time = wpm_list[i + 1][1] - v[2]
            e = {
                "silence_period": silence_time,
                "silence_start": v[2],
                "silence_end": wpm_list[i + 1][1],
            }
            silence_duration_count += silence_time
            silence_list.append(e)

    # hestiation_marker = {}
    # for i in range(0, int(wpm_list[-1][2] + 1), 10):
    #     hestiation_marker[f"{i}-{i+10.0}"] = {"hes_count": 0, "words": []}
    #     for j, v in enumerate(wpm_list):
    #         if ((v[2] > i) and (v[2] < i + 10.0)) and v[0] == "%HESITATION":
    #             hestiation_marker[f"{i}-{i+10.0}"]["words"].append(v)
    #             hestiation_marker[f"{i}-{i+10.0}"]["hes_count"] = len(
    #                 hestiation_marker[f"{i}-{i+10.0}"]["words"]
    #             )

    chunk = round((wpm_list[-1][2]) / 10, ndigits=2)
    last_chunk = round((wpm_list[-1][2]), ndigits=2)
    value = 0
    hes_dict = {}
    while value <= last_chunk:
        temp = value
        value += chunk
        hes_dict[f"{temp}-{value}"] = {"hes_count": 0, "words": []}
        for j, v in enumerate(wpm_list):
            if ((v[2] > temp) and (v[2] < value)) and v[0] == "%HESITATION":
                hes_dict[f"{temp}-{value}"]["words"].append(v)
                hes_dict[f"{temp}-{value}"]["hes_count"] = len(
                    hes_dict[f"{temp}-{value}"]["words"]
                )

    nlp = spacy.load("en_core_web_lg")
    doc_ = nlp(t)
    txt_rm_stop = tp.remove_all(doc_)
    print(tp.calculate_word_frequency(nlp, text_list))

    # run nltk.download() if there are files missing
    # nltk.download()

    # words_fd = nltk.FreqDist(txt_rm_stop)
    bigram_fd = nltk.FreqDist(nltk.bigrams(txt_rm_stop))

    vocab_dict = {}
    counter = 0
    for i in doc_:
        if i.pos_ == "NOUN":
            if i.text in vocab_dict:
                vocab_dict[f"{i.text}"]["count"] += 1
            else:
                counter += 1
                vocab_dict[f"{i.text}"] = {"word": f"{i.text}", "count": 1}
    unique_dict = {}
    for i in doc_:
        if i.lemma_ in unique_dict:
            unique_dict[f"{i.lemma_}"]["count"] += 1
        else:
            counter += 1
            print(i.lemma_)
            unique_dict[f"{i.lemma_}"] = {"word": f"{i.lemma_}", "count": 1}

    keyword_ = nltk.FreqDist(txt_rm_stop).most_common(30)
    key_list = ""
    for i, v in keyword_:
        key_list = key_list + i + " "

    key_doc = nlp(key_list)
    keyword_list = set()
    for i in key_doc:
        for j in key_doc:
            if (i.pos_ == "NOUN" and j.pos_ == "NOUN") and i.text != j.text:
                if i.similarity(j) > 0.5 and i.similarity(j) != 1.0:
                    keyword_list.add(i.lemma_)

    output_json["hestiation_"] = {"marker": {}, "total_count": {}}
    output_json["hestiation_"]["marker"] = hes_dict
    output_json["hestiation_"]["total_count"] = hes_cnt
    output_json["word_frequency"] = {"word": {}, "bigram": {}}
    output_json["word_frequency"]["word"] = keyword_
    output_json["word_frequency"]["bigram"] = bigram_fd.most_common(10)
    output_json["wpm"] = wpm_dict
    silence_dict["silence_list"] = silence_list
    silence_dict["total_silence"] = silence_duration_count
    output_json["silence"] = silence_dict
    output_json["start_process_time"] = start_process_time
    output_json["end_process_time"] = time.time()
    output_json["video_len"] = wpm_list[-1][2]
    output_json["total_words"] = len(wpm_list)
    output_json["avg_wpm"] = avg_wpm

    output_json["vocab"] = vocab_dict
    output_json["len_unique_word"] = len(unique_dict)
    output_json["keyword"] = list(keyword_list)

    db = Database()
    queryObj = {"videoUUID": videoUUID}
    db.update(queryObj, {"postProcessing": output_json})
    return output_json
