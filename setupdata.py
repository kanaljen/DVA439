#!/usr/bin/python

import sys
import nltk
import json
#nltk.download('stopwords')
#nltk.download('punkt')
#nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def read_file():
    """ tries to read <inputfile> and returns raw text """
    try:
      f = open("nordic_test.txt", "r")
      raw = f.read()
      #print(file,'-> raw')
      return raw
    except IOError:
      print("No such file or directory:")
      exit(0)
      

def processor(raw):
    """ tokenize, filters stopwords and lemmatizes raw text
        returns a list with word tokenized sentences"""
    # Split sentences into words
    #print(raw)
    tokenized = []
    for sentence in raw:
        sentence = sentence.lower()
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
    
    newOutput = []
    
    # Converts the output to fit the tfidf
    for innerlist in output:
        #print(innerlist)
        newItem = []
        newItem = ' '.join(str(item) for item in innerlist)
        newOutput.append(newItem)
    
    return newOutput


def calculate_weight(processed):
    
    vectorizer = TfidfVectorizer()
    
    freq_matrix = vectorizer.fit_transform(processed)
    cosSim = cosine_similarity(freq_matrix[-1], freq_matrix)
    
    return cosSim

def print_answer(data):
    
    # Gets the index for the possibly best anwser
    answrI = data['weights'].argsort()[0][-2]
    
    # As weights are in a 2d array
    flattenWeights = data['weights'].flatten()
    # Sorts the weights
    flattenWeights.sort()
    # Gets the best match weight
    bestMatch = flattenWeights[-2]
    
    # If the best match weight is 0, there was no matching answer
    if bestMatch == 0:
        print("Sorry, i did not understand.")
    else:
        print(data['raw'][answrI])
        


def write_json(data,file):
    """ writes a new json with provided data"""
    dot = file.find('.')
    filename = file[0:dot] + '.json'
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)
    print('data ->',filename)


def main(argv):
    #if len(argv)!=2:
    #    print('wrong number of arguments')
    #    print('usage:',argv[0],'<inputfile>')
    #    exit(0)
    # 1. Read data from file
    raw = read_file()
    
    #calculate_weight(nltk.sent_tokenize(raw))
    print("Question: ")
    user_response = input()
    raw = raw + "\n" + user_response
    
    data = {'raw': nltk.sent_tokenize(raw)}
    print('raw -> data')
    # 2. Process raw text
    data['processed'] = processor(data['raw'])
    print('processed -> data')
    # 3. Calculate weights for the words
    data['weights'] = calculate_weight(data['processed'])
    print('weights -> data')
    
    print_answer(data)
    # 4. Save output to json
    #write_json(data,"test.txt")


if __name__ == "__main__": main(sys.argv)