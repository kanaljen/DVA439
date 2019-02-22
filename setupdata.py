#!/usr/bin/python

import sys
import nltk
import json
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from collections import Counter

def read_file(file):
    """ tries to read <inputfile> and returns raw text """
    try:
      f = open(file, "r")
      raw = f.read()
      print(file,'-> raw')
      return raw
    except IOError:
      print("No such file or directory:",file)
      exit(0)


def processor(raw):
    """ tokenize, filters stopwords and lemmatizes raw text
        returns a list with word tokenized sentences"""
    # Split sentences into words
    tokenized = []
    for sentence in raw:
        sentence.lower()
        tokenized.append(nltk.word_tokenize(sentence))
    print('raw -> tokenized')
    # Filter stopwords from sentences
    stop = set(stopwords.words('english'))
    filtered = []
    for sentence in tokenized:
        filtered.append([w for w in sentence if not w in stop])
    print('tokenized -> filtered')
    # Lemmatize words
    output = []
    lmtzr = WordNetLemmatizer()
    print('filtered -> lemmatized')
    for sentence in filtered:
        lsentence = []
        for word in sentence:
            lsentence.append(lmtzr.lemmatize(word))
        output.append(lsentence)
    print('lemmatized -> processed')
    return output


def calculate_weight(processed):
    """ calculate words weights based on occurrence
        returns a dictionary with words and weights"""
    weights = Counter()
    for sentence in processed:
        weights.update(word for word in sentence)
    for item in weights:
        weights[item] = 1/weights[item]
    print('processed -> weights')
    return weights


def write_json(data,file):
    """ writes a new json with provided data"""
    dot = file.find('.')
    filename = file[0:dot] + '.json'
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)
    print('data ->',filename)


def main(argv):
    if len(argv)!=2:
        print('wrong number of arguments')
        print('usage:',argv[0],'<inputfile>')
        exit(0)
    # 1. Read data from file
    raw = read_file(argv[1])
    data = {'raw': nltk.sent_tokenize(raw)}
    print('raw -> data')
    # 2. Process raw text
    data['processed'] = processor(data['raw'])
    print('processed -> data')
    # 3. Calculate weights for the words
    data['weights'] = calculate_weight(data['processed'])
    print('weights -> data')
    # 4. Save output to json
    write_json(data,argv[1])


if __name__ == "__main__": main(sys.argv)