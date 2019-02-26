import json
import sys
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer


def check_argv(argv):
    if len(argv)!=2:
        print('wrong number of arguments')
        print('usage:', argv[0], '<jsonfile>')
        exit(0)
    dot = argv[1].find('.')
    if argv[1][dot:] != '.json':
        print('not a json file')
        print('usage:', argv[0], '<jsonfile>')
        exit(0)


def read_json(file):
    with open(file) as json_data:
        return json.load(json_data)


def preprocess(question):
    tokenized = nltk.word_tokenize(question.lower())
    stop = set(stopwords.words('english'))
    filtered = [w for w in tokenized if not w in stop]
    lmtzr = WordNetLemmatizer()
    output = []
    for word in filtered:
        output.append(lmtzr.lemmatize(word))
    return output


def compare(question,dataset):
    question = preprocess(question)
    sentence_weight = []
    for sentence in dataset['processed']:
        weight = 0
        for word in question:
            if word in sentence:
                weight += dataset['weights'][word]
        sentence_weight.append(weight)
    maximum = 0
    for i in range(0,len(sentence_weight)):
        if sentence_weight[i] > maximum:
            maximum = sentence_weight[i]
    print('--start--')
    if maximum > 0:
        for i in range(0,len(sentence_weight)):
            if sentence_weight[i] == maximum and sentence_weight[i] > 0:
                print(dataset['raw'][i])
                print('---')
    else:
        print('no matching sentence')
    print('--end--')


def main(argv):
    check_argv(argv)
    dataset = read_json(argv[1])
    question = ''
    while(question != 'exit'):
        print("type 'exit' to terminate execution")
        question = input("Ask a question: ")
        if question != 'exit':
            compare(question,dataset)


if __name__ == "__main__": main(sys.argv)