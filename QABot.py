#!/usr/bin/python

import sys
import nltk
import json
import numpy as np
#nltk.download('stopwords')
#nltk.download('punkt')
#nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from collections import Counter
lmtzr = WordNetLemmatizer()

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Start the question with a "wh-word"
WH_INPUTS_NE = ("where", "who", "when", "what")
# Labels for NE
NE_GROUPS = ("NE","ORGANIZATION","PERSON","LOCATION","DATE","TIME","MONEY","PERCENT","FACILITY","GPE")

def read_file():
    """ tries to read <inputfile> and returns raw text """
    try:
      f = open("corpus.txt", "r")
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
    #lmtzr = WordNetLemmatizer()
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

# Calculates the weights for each sentence based on the quetion sentence
def calculate_weight(processed):
    
    # Gets the TF-IDF feature vectors
    vectorizer = TfidfVectorizer()
    
    # Gets the frequencie matrix
    freq_matrix = vectorizer.fit_transform(processed)
    
    # Calculates the cosine similarity based on the feature vectors
    cosSim = cosine_similarity(freq_matrix[-1], freq_matrix)
    
    # Prints the weights for each sentence
    #print(cosSim)
    
    return cosSim


""" #OLD PRINT FUNCTION
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
        print(data['raw'][answrI])"""
        

def write_json(data,file):
    """ writes a new json with provided data"""
    dot = file.find('.')
    filename = file[0:dot] + '.json'
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)
    print('data ->',filename)

     
# Checking for wh-word
def whWord(sentence):
    # Loop the question to search for wh-word, then return it
    for word in sentence.split():
        if word.lower() in WH_INPUTS_NE:
            return word


# Generate headword
def headWord(user_response):
    # Returns the first noun or noun-phrase after what in the question
    lemmatized_tokens = []
    # Tokenize question
    tokens = nltk.word_tokenize(user_response)
    # Lemmatize question
    for word in tokens:
        word = lmtzr.lemmatize(word)
        lemmatized_tokens.append(word)    
    # POS of each word. E.g. noun, verb, etc...
    tagged = nltk.pos_tag(lemmatized_tokens)
    phrase_to_return = []
    nnp = 0
    for word in user_response.split():
        if word in WH_INPUTS_NE:
            for part in tagged:
                # Look for nouns and noun-phrases
                if part[1] == 'NN' or part[1] == 'NNP':
                    nnp = 1
                    #print('returning headword:', part[0])
                    phrase_to_return.append(part[0])
                elif nnp == 1:
                    # Return when a noun-phrase is complete
                    return phrase_to_return
    # Return an empty list if no head word was found
    return phrase_to_return

def sentencesToCompare(head_word,sent_tokens,entity_tag_to_check, weights, raw):
    # Returns all relevant sentences that includes either the head-word (what-question)
    # Or it will search for relevant labels (who-, where-, when-questions)
    new_sent = []
    new_weights = []
    new_raw = []
    
    # Flatten weithts to be able to loop through
    weights = weights.flatten()
    
    i = 0

    if head_word:
        # If what-question
        for sentence in sent_tokens:
            if any(c in sentence for c in (head_word)):  
                # If the sentence contains the head-word
                new_sent.append(sent_tokens[i])
                new_weights.append(weights[i])
                new_raw.append(raw[i])
            i += 1
    else:
        # If who-, where-, when-question
        for sentence in sent_tokens:
            if any(c in sentence for c in (entity_tag_to_check)): 
                # If the sentence contains a word with the right label
                new_sent.append(sent_tokens[i])
                new_weights.append(weights[i])
                new_raw.append(raw[i])
            i += 1
    return new_sent, new_weights, new_raw


# Generating response
def response(user_response,wh_word,entity_labels,entity_tag, data):
    robo_response=''
    head_word = []
    entity_to_save = []
    temp_sent_tokens = []
    temp_weights = []
    temp_raw = []
    entity_label_to_check = []
    entity_tag_to_check = []
    # Define what wh-word
    if wh_word == 'where':
        entity_to_save = ("LOCATION","GPE")
    elif wh_word == 'when':
        entity_to_save = ("DATE","TIME")
    elif wh_word == 'who':
        entity_to_save = ("ORGANIZATION","PERSON")
    else:
        # Wh-word = 'What'
        # All labels are relevant
        entity_to_save = NE_GROUPS
        # Get the head-word
        head_word = headWord(user_response)
        print('Head word/phrase = ',head_word)
        if not head_word:
            # If no head-word, return
            #sent_tokens.append(user_response)
            return 'Head word missing from what-question'
        
    i = 0
    if not head_word:
        # If not what-question
        for label in entity_labels:
            if any(c in label for c in (entity_to_save)):  
                # Save the labels that are relevant
                entity_label_to_check.append(label)
                # Save words that corresponds to that label
                entity_tag_to_check.append(entity_tag[i])
            i += 1
            
    # Store the sentences, weights and raw text that are relevant
    temp_sent_tokens, temp_weights, temp_raw = sentencesToCompare(head_word, data['processed'][0:-1] ,entity_tag_to_check, data['weights'], data['raw'])

    # Converts the weigts to an numpy array
    temp_weights = np.asarray(temp_weights)
    
    # Gets index for the highest/best mathing weight/sentence
    answrI = temp_weights.argsort()[-1]
    
    # Prints the final answer
    print(temp_raw[answrI])
    
    return temp_sent_tokens, temp_weights


def train_entity():
    # Data base
    with open('training_NE.txt', 'r') as f:
        data = f.readlines()
        filtered_data = []
        # Remove empty rows
        for line in data:
            if line.strip():
                filtered_data.append(line)
        entity_names = []
        entity_label = []
        entity_pos = []
        # Split into words and store its name, label and POS
        for line in filtered_data:
            words = line.split()
            entity_names.append(words[0])
            entity_pos.append(words[1])
            entity_label.append(words[3])

        # Replace the labels with other names
        entity_label = [w.replace('B-LOC', 'LOCATION') for w in entity_label]
        entity_label = [w.replace('I-LOC', 'LOCATION') for w in entity_label]
        entity_label = [w.replace('B-PER', 'PERSON') for w in entity_label]
        entity_label = [w.replace('I-PER', 'PERSON') for w in entity_label]
        entity_label = [w.replace('B-MISC', 'NE') for w in entity_label]
        entity_label = [w.replace('I-MISC', 'NE') for w in entity_label]
        entity_label = [w.replace('B-ORG', 'ORGANIZATION') for w in entity_label]
        entity_label = [w.replace('I-ORG', 'ORGANIZATION') for w in entity_label]
        
        final_entity_names = []
        final_entity_pos = []
        final_entity_label = []
        i = 0
        # Store all words that does not have a label called 'O' (Other)
        for label in entity_label:
            if not label == 'O':
                final_entity_names.append(entity_names[i])
                final_entity_pos.append(entity_pos[i])
                final_entity_label.append(label)
            i += 1
    # Store the words, labels and POS's in a matrix
    np.asarray(final_entity_names)
    np.asarray(final_entity_pos)
    np.asarray(final_entity_label)
    entities_to_return = np.vstack((final_entity_names, final_entity_pos,final_entity_label)).T
    # Return matrix (data base)
    return entities_to_return
            

def main(argv):
    #if len(argv)!=2:
    #    print('wrong number of arguments')
    #    print('usage:',argv[0],'<inputfile>')
    #    exit(0)
    # 1. Read data from file
    raw = read_file()
    
    # Save a data base of NE
    entities = train_entity()
    
    #calculate_weight(nltk.sent_tokenize(raw))
    print("Enter a question. Type 'bye' to end.")
    flag = True
    while(flag == True):
        
        print("Question: ")
        user_response = input()
        user_response = user_response.lower()
        if user_response == 'bye':
            flag = False
        else:
            wh_word = whWord(user_response)
            print('wh_word = ', wh_word)
        if wh_word:  
    
            raw = raw + "\n" + user_response
            
            data = {'raw': nltk.sent_tokenize(raw)}
            print('raw -> data')
            # 2. Process raw text
            data['processed'] = processor(data['raw'])
            print('processed -> data')
            # 3. Calculate weights for the words
            data['weights'] = calculate_weight(data['processed'])
            print('weights -> data')
        
            # Calculates and prints the response
            response(user_response,wh_word,entities[:,2].tolist(),entities[:,0].tolist(), data)
            
            #print_answer(data)
            # 4. Save output to json
            #write_json(data,"test.txt")
    
        else:
            print("ROBO: You need to start with a wh-word",end="")
            #print(response(user_response,wh_word,entities_ne))
            #sent_tokens.remove(user_response)
        

if __name__ == "__main__": main(sys.argv)



