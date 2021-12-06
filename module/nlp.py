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
import datetime


def process_nlp(videoUUID, soundUUID):
    db = Database()
    queryObj = {"videoUUID": videoUUID}
    db.update(
        queryObj,
        {
            "lastUpdate": datetime.datetime.today().isoformat(),
            "status": "processing_nlp",
        },
    )
    result = db.find({"videoUUID": f"{videoUUID}"}, {"userId": 1})
    result_2 = db.findUserById(result[0]["userId"])

    start_process_time = time.time()
    filename = videoUUID.split(".")[0] + ".json"
    transcript_path = os.path.join("transcript", filename)
    file_ = tp.read_json(transcript_path)

    text_list = tp.create_textFromList(file_)
    hes_cnt, hes_txt_ = tp.count_hestiation(text_list)

    # From Pre-trained STT model;f"{path}audio/{output_filename_ogg}"
    another_stt = tp.stt(f"upload/audio/{soundUUID}")
    repeat_list = {}
    prev = ""
    for i in another_stt.split():
        if i == prev:
            if i in repeat_list:
                repeat_list[f"{i}"] += 1
            else:
                repeat_list[f"{i}"] = 1
        else:
            prev = i

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
    timer = 0
    # assert int(wpm_list[-1][2] + 1) - timer < 60
    while timer < int(wpm_list[-1][2] + 1):
        plus_ = min(60, int(wpm_list[-1][2] + 1) - timer)
        wpm_dict[f"{timer}-{timer+plus_}"] = {"wpm": 0, "words": []}
        for j, v in enumerate(wpm_list):
            if timer < v[2] < timer + plus_:
                st_ = f"{timer}-{timer+plus_}"
                wpm_dict[st_]["words"].append(v)
        wpm_dict[st_]["wpm"] = (
            len(wpm_dict[st_]["words"])
            if plus_ == 60
            else (len(wpm_dict[st_]["words"]) * 60) / plus_
        )
        total += len(wpm_dict[st_]["words"])
        timer += plus_
        count_min += 1 if plus_ == 60 else round(plus_ / 60, ndigits=2)

    # print(f"minutes_count {count_min}")
    # print(wpm_list[-1][2])
    avg_wpm = (
        (total / count_min)
        if wpm_list[-1][2] > 60
        else wpm_dict[f"0-{int(wpm_list[-1][2] + 1)}"]["wpm"]
    )

    # Count Silence Period
    silence_dict = {"total_silence": 0, "silence_list": []}
    silence_duration_count = 0
    silence_list = []
    for i, v in enumerate(wpm_list):
        if i == len(wpm_list) - 1:
            break
        if v[2] != wpm_list[i + 1][1]:
            silence_time = wpm_list[i + 1][1] - v[2]
            if silence_time > 0.3:  # Can be custom
                e = {
                    "silence_period": round(silence_time, ndigits=5),
                    "silence_start": v[2],
                    "silence_end": wpm_list[i + 1][1],
                }
                silence_list.append(e)
            else:
                pass
            silence_duration_count += silence_time


    # chunk = round((wpm_list[-1][2]) / 10, ndigits=2)
    # last_chunk = round((wpm_list[-1][2]), ndigits=2)
    # value = 0
    # hes_dict = {}
    # hes_duration = 0
    # while value <= last_chunk:
    #     temp = value
    #     value += chunk
    #     hes_dict[f"{temp}-{value}"] = {"hes_count": 0, "words": []}
    #     for j, v in enumerate(wpm_list):
    #         if ((v[2] > temp) and (v[2] < value)) and v[0] == "%HESITATION":
    #             hes_duration += v[2] - v[1]
    #             hes_dict[f"{temp}-{value}"]["words"].append(v)
    #             hes_dict[f"{temp}-{value}"]["hes_count"] = len(
    #                 hes_dict[f"{temp}-{value}"]["words"]
    #             )
    timer_hes = 0
    hes_dict_2 = {}
    hes_duration_2 = 0
    while timer_hes < int(wpm_list[-1][2] + 1):
        plus_timer = min(60, int(wpm_list[-1][2] + 1) - timer_hes)
        hes_dict_2[f"{timer_hes}-{timer_hes+plus_timer}"] = {"hes_count": 0, "words": []}
        for j, v in enumerate(wpm_list):
            if (timer_hes < v[2] < timer_hes + plus_timer) and v[0] == "%HESITATION":
                st_ = f"{timer_hes}-{timer_hes+plus_timer}"
                hes_duration_2 += v[2] - v[1]
                hes_dict_2[st_]["words"].append(v)
                hes_dict_2[st_]["hes_count"] = len(hes_dict_2[st_]["words"])
        timer_hes += plus_timer



    nlp = spacy.load("en_core_web_lg")
    doc_ = nlp(t)
    receive_stopword = result_2[0]["stopwords"]

    txt_rm_stop, count_combine = tp.remove_all(doc_, receive_stopword)
    rm_text = ""

    for i in txt_rm_stop:
        rm_text = rm_text + " " + i

    # run nltk.download() if there are files missing
    # nltk.download()

    # words_fd = nltk.FreqDist(txt_rm_stop)
    bigram_fd = nltk.FreqDist(nltk.bigrams(txt_rm_stop))

    # **** DEPRECATED ****
    # vocab_dict = {}
    # counter = 0
    # for i in doc_:
    #     if i.pos_ == "NOUN":
    #         if i.text in vocab_dict:
    #             vocab_dict[f"{i.text}"]["count"] += 1
    #         else:
    #             counter += 1
    #             vocab_dict[f"{i.text}"] = {"word": f"{i.text}", "count": 1}
    # unique_dict = {}
    # for i in doc_:
    #     if i.lemma_ in unique_dict:
    #         unique_dict[f"{i.lemma_}"]["count"] += 1
    #     else:
    #         counter += 1
    #         # print(i.lemma_)
    #         unique_dict[f"{i.lemma_}"] = {"word": f"{i.lemma_}", "count": 1}
    # **************
    vocab_dict = {
        "total_vocab": 0,
        "vocab": {},
    }

    rm_doc = nlp(rm_text)
    vocab_dict["total_vocab"] = len(rm_doc)

    for i in rm_doc:
        # if i not in vocab_dict.keys():
        #     vocab_dict.update({i.pos_:1})

        # vocab_dict[i.pos_] = vocab_dict[i.pos_] + 1
        if i.text in vocab_dict and i.pos_ != "SPACE":
            vocab_dict["vocab"][f"{i.text}"]["count"] += 1
            vocab_dict["vocab"][f"{i.text}"]["%"] = round(
                (vocab_dict["vocab"][f"{i.text}"]["count"] / vocab_dict["total_words"])
                * 100,
                ndigits=5,
            )
        elif i.pos_ != "SPACE":
            vocab_dict["vocab"][f"{i.text}"] = {
                "word": f"{i.lemma_}",
                "count": 1,
                "pos": f"{i.pos_}",
                "%": round((1 / vocab_dict["total_vocab"]) * 100, ndigits=5),
            }

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
    output_json["hestiation_"]["marker"] = hes_dict_2
    output_json["hestiation_"]["total_count"] = hes_cnt
    output_json["hestiation_duration"] = round(hes_duration_2, ndigits=4)
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
    output_json["avg_wpm"] = round(avg_wpm, ndigits=3)

    output_json["vocab"] = vocab_dict
    output_json["repeat_list"] = repeat_list
    # output_json["len_unique_word"] = len(unique_dict)
    output_json["keyword"] = list(keyword_list)
    output_json["custom_stopwords"] = count_combine

    db.update(
        queryObj,
        {
            "lastUpdate": datetime.datetime.today().isoformat(),
            "status": "Done",
            "report.postProcessing": output_json,
        },
    )

    db.close()
    return output_json
