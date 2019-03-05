
# Start the question with a "wh-word"
WH_INPUTS_NE = ("where", "who", "when", "what")
# Labels for NE
NE_GROUPS = ("NE","ORGANIZATION","PERSON","LOCATION","DATE","TIME","MONEY","PERCENT","FACILITY","GPE")
        
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
        word = lemmatizer.lemmatize(word)
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

def sentencesToCompare(head_word,sent_tokens,entity_tag_to_check):
    # Returns all relevant sentences that includes either the head-word (what-question)
    # Or it will search for relevant labels (who-, where-, when-questions)
    new_sent = []
    lemmatized_sent = []
    i = 0
    for word in sent_tokens:
        # Lemmatize sentences, since the head word is already lemmatized
        word = lemmatizer.lemmatize(word)
        lemmatized_sent.append(word)    
    if head_word:
        # If what-question
        for sentence in lemmatized_sent:
            if any(c in sentence for c in (head_word)):  
                # If the sentence contains the head-word
                new_sent.append(sent_tokens[i])
            i += 1
    else:
        # If who-, where-, when-question
        for sentence in lemmatized_sent:
            if any(c in sentence for c in (entity_tag_to_check)): 
                # If the sentence contains a word with the right label
                new_sent.append(sent_tokens[i])
            i += 1
    return new_sent

# Generating response
def response(user_response,wh_word,entity_labels,entity_tag):
    robo_response=''
    head_word = []
    entity_to_save = []
    temp_sent_tokens = []
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
            sent_tokens.append(user_response)
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
    # Store the sentences that are relevant
    temp_sent_tokens = sentencesToCompare(head_word,sent_tokens,entity_tag_to_check)
    # Add question to sentences for comparing
    sent_tokens.append(user_response)
    if temp_sent_tokens:
        # Add question to sentences for comparing
        temp_sent_tokens.append(user_response)

def extract_entity_names(t):
    # Stores all words including labels for every word that has a label
    entity_names = []    
    for child in t:
        if hasattr(child, 'label') and t.label:
            if any(c in child.label() for c in (NE_GROUPS)):
                # If it contains a label, save it
                entity_names.append(child)
    return entity_names

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
            
flag=True
print("ROBO: My name is Robo. I will answer your queries about Chatbots. If you want to exit, type Bye!")

# Save a data base of NE
entities = train_entity()

while(flag==True):
    user_response = input()
    user_response=user_response.lower()
    wh_word = ''
    if(user_response!='bye'):
        wh_word = whWord(user_response)
        print('wh_word = ', wh_word)
        if(user_response=='thanks' or user_response=='thank you' ):
            flag=False
            print("ROBO: You are welcome..")
        else:
            if(greeting(user_response)!=None):
                print("ROBO: "+greeting(user_response))
            elif any(c in user_response for c in (WH_INPUTS_NE)):  
                #print("ROBO: ",end="")
                print("ROBO: ",response(user_response,wh_word,entities[:,2].tolist(),entities[:,0].tolist()))
                sent_tokens.remove(user_response)
            else:
                print("ROBO: You need to start with a wh-word",end="")
                #print(response(user_response,wh_word,entities_ne))
                #sent_tokens.remove(user_response)
    else:
        flag=False
        print("ROBO: Bye! take care..")    