# Aadit Mehrotra 
# 20756049
import argparse
import getDocument
import math
import os
import pickle
import re

from collections import OrderedDict
from PorterStemmer import PorterStemmer




def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('documents')
    parser.add_argument('--stem',
                        required=False, default="False")
    args = parser.parse_args()
    return args.documents, args.stem


def cal_bm25(topic_id, topic, token_token_id, postings_list, doc_id_no, average_doc_length, stem, documents_path):
    tokens_query = tokenize(topic)
    score_doc_no = {}
    N = len(doc_id_no)

    p = PorterStemmer()

    for tok in tokens_query:
        qf = tokens_query.count(tok)
        token_tf = ((7 + 1)*qf) / (7 + qf)
        if stem:
            tok = p.stem(tok, 0, len(tok) - 1)


        token_id = token_token_id[tok]
        postings = postings_list[token_id]
        n_i = len(postings[::2])
        a = (N - n_i + 0.5) / (n_i + 0.5)
        token_idf = math.log(a)

        for i in range(0, len(postings), 2):
            doc_id = postings[i]
            doc_no = doc_id_no[doc_id]
            document = getDocument.retrieve_by_docno(documents_path, doc_no)
            K = 1.2 * ((1 - 0.75) + 0.75 * (document.length / average_doc_length))
            doc_tf = ((1.2 + 1)*postings[i+1]) / (K + postings[i+1])
            score = doc_tf * token_tf * token_idf
            if doc_no in score_doc_no:
                score_doc_no[doc_no] = score_doc_no[doc_no] + score
            else:
                score_doc_no[doc_no] = score
    sorted_doc_no_score = OrderedDict(sorted(score_doc_no.items(), key=lambda t: t[1], reverse=True))

    print("Scores for topic: {}".format(topic_id))
    return sorted_doc_no_score


def tokenize(query):
    tokens = []
    text = query.lower()
    text_tokens = re.split('[\W]', text)
    tokens += text_tokens

    tokens = list(filter(None, tokens))
    return tokens


dir_path, stem = parse_args()
stem = stem.lower() == "true"



topics = pickle.load(open('./topics.p', 'rb'))


print("Getting relevant dicts")
token_id_postings = pickle.load(open(dir_path + '/token_id_postings.p', 'rb'))
token_id_token = pickle.load(open(dir_path + '/token_id_token.p', 'rb'))
token_token_id = pickle.load(open(dir_path + '/token_token_id.p', 'rb'))
doc_id_no = pickle.load(open(dir_path + '/doc_id_no.p', 'rb'))
print("------DONE----- ")

print("Finding average length of docs")
avg_len = sum([getDocument.retrieve_by_docno(dir_path, doc_no).length for doc_id, doc_no in doc_id_no.items()]) / len(doc_id_no)


print(avg_len)

print("------DONE----- ")

filepath = './hw4-bm25-stem-asmehrot.txt' if stem else './hw4-bm25-baseline-asmehrot.txt'

with open(filepath, 'w') as file:
    for topic_id, topic in topics.items():
        o_dict = cal_bm25(topic_id, topic, token_token_id, token_id_postings, doc_id_no, avg_len, stem, dir_path)
        lim = min(len(o_dict), 1000)
        i = 1
        for doc_no, score in o_dict.items():
            file.write("{} Q0 {} {} {} asmehrot_bm25_baseline\n".format(topic_id, doc_no, i, score))
            i += 1
            if i > 1000:
                break
