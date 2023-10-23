import json
import nltk
import numpy as np
import random
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.optimizers import SGD
import numpy as np
from keras.models import load_model
from sklearn.utils import shuffle
from userNLP import *
from nltk.stem import WordNetLemmatizer
from sklearn.utils import shuffle
from keras.optimizers import SGD
import numpy as np
import nltk



# load the data from the json file 
def load_data(file_name):
        with open(file_name) as json_data:
            intents = json.load(json_data)
        return intents


def preprocess():
    lemmatizer = WordNetLemmatizer()
    intents = load_data('code/intents.json')
    ignore_letters = ['?', '!', '.', ',']

    words, classes, documents = [], [], []
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            word_tokens = [lemmatizer.lemmatize(w.lower()) for w in nltk.word_tokenize(pattern) if w not in ignore_letters]
            words.extend(word_tokens)
            documents.append((word_tokens, intent['tag']))
        classes.append(intent['tag'])
        
    words = sorted(list(set(words)))
    classes = sorted(list(set(classes)))

    return words, classes, documents


def create_training_data(documents, words, classes):
    lemmatizer = WordNetLemmatizer()
    training = []
    output = []

    for doc in documents:
        bag = [0] * len(words)

        for word in doc[0]:
            lemmatized_word = lemmatizer.lemmatize(word) 
            if lemmatized_word in words:
                bag[words.index(lemmatized_word)] = 1

        training.append(bag)
        output_row = [0] * len(classes)
        output_row[classes.index(doc[1])] = 1
        output.append(output_row)

    training, output = shuffle(training, output) 
    training = np.array(training)
    output = np.array(output)

    return training, output

def create_model(train_x, train_y):
    model = Sequential()
    model.add(Dense(128, input_shape=(train_x.shape[1],), activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(train_y.shape[1], activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(train_x, train_y, epochs=200, batch_size=5, verbose=1, validation_split=0.2) # moved fitting here
    return model # remove fitting from create_model()


def main():
    words, classes, documents = preprocess()
    training_x, training_y = create_training_data(documents, words, classes)
    model = create_model(training_x, training_y)
    model.save('code/model.keras')
    print("Model created and saved successfully")
    pickle.dump(words, open('code/words.pkl', 'wb'))
    pickle.dump(classes, open('code/classes.pkl', 'wb'))


if __name__ == "__main__":
     main()