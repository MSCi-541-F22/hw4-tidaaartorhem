

import argparse
import gzip
import os.path
import pickle
import re
import time

from document import Document
from collections import Counter
from PorterStemmer import PorterStemmer

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('gzip')
    parser.add_argument('dir')
    parser.add_argument('--stem',required=False, default="False")
    args = parser.parse_args()
    return args.gzip, args.dir, args.stem


def create_raw_text_doc(doc_id, document, dir_path):
    file_path = dir_path + time.strftime('/%y/%m/%d/', time.strptime(document.date, '%B %d, %Y'))
    os.makedirs(file_path, exist_ok=True)
    file_path += document.docno.split('-')[1]
    file_path += '.p'

    with open(file_path, "wb") as text_file:
        pickle.dump(document, text_file)
    print("Document: {}".format(doc_id))


def get_match_strip_tags(re_search, text, re_strip_tags, re_strip_close_tags):
    matches = re.search(re_search, text)
    if matches:
        match = matches.group().strip()
        match = re_strip_tags.sub('', match)
        match = re_strip_close_tags.sub('', match)
        return match
    return ''


def build_doc_metadata(document):
    text = document.raw_document
    re_strip_tags = re.compile('<\w+>\n*')
    re_strip_close_tags = re.compile('<\/\w+>\n*')
    headline_match = re.compile('<HEADLINE>[\s\S]+<\/HEADLINE>')
    document.headline = get_match_strip_tags(headline_match, text, re_strip_tags, re_strip_close_tags)
    headline_match = re.compile('<GRAPHIC>[\s\S]+<\/GRAPHIC>')
    document.graphic = get_match_strip_tags(headline_match, text, re_strip_tags, re_strip_close_tags)
    headline_match = re.compile('<TEXT>[\s\S]+<\/TEXT>')
    document.text = get_match_strip_tags(headline_match, text, re_strip_tags, re_strip_close_tags)


def build_inversion_index(doc_id, document, stem):
    tokens = tokenize(document, stem)
    document.length = len(tokens)

    token_ids = convert_tokens_to_ids(tokens)
    add_to_postings(doc_id, token_ids)


def tokenize(document, stem):
    tokens = []
    p = PorterStemmer()
    for text in document.headline, document.graphic, document.text:
        text = text.lower()
        text_tokens = re.split('[\W]', text)
        if stem:
            stem_tokens = []
            for t in text_tokens:
                t = p.stem(t, 0, len(t) - 1)
                stem_tokens.append(t)
            text_tokens = stem_tokens
        tokens += text_tokens
    tokens = list(filter(None, tokens))
    return tokens


def convert_tokens_to_ids(tokens):
    token_ids = []
    for token in tokens:
        if token in token_token_id:
            token_ids.append(token_token_id[token])
        else:
            token_id = len(token_token_id)
            token_token_id[token] = token_id
            token_id_token[token_id] = token
            token_ids.append(token_id)
    return token_ids


def add_to_postings(doc_id, token_ids):
    token_counts = Counter(token_ids)

    for token_id, token_count in token_counts.items():
        if token_id not in token_id_postings:
            token_id_postings[token_id] = []
        token_id_postings[token_id].append(doc_id)
        token_id_postings[token_id].append(token_count)


gzip_path, dir_path, stem = parse_args()
stem = stem.lower() == "true"

# Create the directory if it doesn't exist, else throw an error
os.makedirs(dir_path, exist_ok=False)

# Check if gzip exists
if not os.path.exists(gzip_path):
    print("GZIP file isn't present.")
    exit(1)

doc_id_no = {}
token_id_token = {}
token_token_id = {}
token_id_postings = {}

with gzip.open(gzip_path, mode='rt') as gzip_file:
    document = None
    raw_document = []
    doc_id = 0

    for line in gzip_file:
        raw_document.append(line)

        if "<DOC>" in line:
            document = Document()
        elif "<DOCNO>" in line:
            docno = re.search('(LA|RF)\d{6}-\d{4}', line).group()
            docno_list = docno.split('-')
            date = docno_list[0][2:]
            doc_id += 1
            document.doc_id = doc_id
            document.docno = docno
            document.date = time.strftime('%B %d, %Y', time.strptime(date, '%m%d%y'))

        elif "</DOC>" in line:
            raw_document_string = "".join(raw_document)
            document.raw_document = raw_document_string
            doc_id_no[doc_id] = document.docno
            build_doc_metadata(document)
            build_inversion_index(doc_id, document, stem)
            create_raw_text_doc(doc_id, document, dir_path)
            raw_document.clear()

pickle.dump(doc_id_no, open(dir_path + '/doc_id_no.p', 'wb'))
pickle.dump(token_id_token, open(dir_path + '/token_id_token.p', 'wb'))
pickle.dump(token_token_id, open(dir_path + '/token_token_id.p', 'wb'))
pickle.dump(token_id_postings, open(dir_path + '/token_id_postings.p', 'wb'))