import nltk
#nltk.download()
from nltk.stem.lancaster import LancasterStemmer
stemmer=LancasterStemmer()

import numpy as np
import tflearn
import tensorflow as tf
import random
import json
import pickle


with open ('./indian_restaurant2.json') as file:
    data=json.load(file)

    #print(data['intents'])


#open pickle file- if cant open it, then go through the code and save it in pickle
#if model exists, we dont retrain the model
#pickle file tries to open everything (try statement)- if doesnt work= go to except statement and run the whole code
#and finally save the file(goal: not to run and train the model everytime we open the file)
try: #rb= read bytes
    with open('data.pickle2', 'rb') as f:
        #save the 4 variables in pickle file
        words,labels,training, output= pickle.load(f)
except:
    words=[]
    labels=[]
    docs_x=[] #list of all different patterns (user input) (nltk.word_tokenizer)
    docs_y=[] #corresponding tags

    #loops through every intent in json file
    for intent in data['indian_restaurant']:
        #loops through all patterns in json file
        for pattern in intent['patterns']:
        #stemming: taking words and bring it to the root word
        #to get stemmed word, we need to tokenize
            wrds=nltk.word_tokenize(pattern) #returns a list with all different words in it
            #we put all of our tokenized words in the words list
            words.extend(wrds)
            #docs_x correspond with docs_y
            docs_x.append(wrds) #contains list of the different tokenized words
            docs_y.append(intent['tag']) #corresponding entries in docs y

        if intent['tag'] not in labels:
            labels.append(intent['tag'])

    #stem every word in words list and remove every duplicate
    words=[stemmer.stem(w.lower())for w in words if w != '?'] #remove question mark, its common that people type it- we dont want it to have some kind of meaning
    words=sorted(list(set(words))) #set removes duplicate elements #list convers it back into a list
    labels=sorted(labels)

#neural networks only understand numbers, not strings
#bag of words (one hot encoding)- which represent words in any given pattern
#does a word occur?
#[0,0,1,0,1,0,0] #if a words occur(even 10 times)= we just put a 1


    training=[] #will have bunch of words (list with 0 and 1)
    output=[] # also words with 0 and 1
#list with the length of the amount of classes we have
    out_empty=[0 for _ in range(len(labels))]
#create bag of words
    for x, doc in enumerate(docs_x):
        bag=[]

        wrds=[stemmer.stem(w.lower()) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1) #1=word exists
            else:
                bag.append(0)#0= word is not here

        output_row=out_empty[:]

        #we check where the tag is in label list where a specific word is located and we set it to 1 in output row
        output_row[labels.index(docs_y[x])]=1

        training.append(bag) #training list has a bunch of words (0,1)
        output.append(output_row) #also list of 0 and 1
        #training and output list both hot encoded

#we need to work with arrays for tflearn
#take list and change to array so we can feed to our model
    training=np.array(training)
    output=np.array(output)

## NEXT PART- start building model with tflearn

    #write all these variables in a pickle file
    with open('data.pickle2', 'wb') as f:
        pickle.dump((words,labels,training, output),f)
#resetting previous graphs
tf.reset_default_graph()

#define input shape we expect for our model
#each training same length= thats why 0
net=tflearn.input_data(shape=[None, len(training[0])])

#2 hidden layers with 8 neurons

#8 neurons for hidden layer
net=tflearn.fully_connected(net, 8)


#8 neurons for hidden layer
net=tflearn.fully_connected(net, 8)


#output layer                                                          #softmax= probability for each neuron in layer
net=tflearn.fully_connected(net, len(output[0]), activation='softmax') #probabilities of each output
net=tflearn.regression(net)

#TRAIN THE MODEL

model=tflearn.DNN(net)

#SEHR WICHTIG! BEIM ERSTEN MAL TRY UND EXCEPT AUFFORDERUNG AUSKOMMENTIEREN!!!!!!  UND MODEL FIT UND MODEL SAVE GANZ NACH LINKS
try:
    model.load('model.tflearn2')
except:

#n_epoch= how many times it sees the data, hopefully it gets better the more it sees the data
    model.fit(training,output,n_epoch=1000,batch_size=8, show_metric=True)
#save model
    model.save('model.tflearn3')



#take bag of words, convert to numpy array and
#return to where we need it
def bag_of_words(s,words):
    bag=[0 for _ in range(len(words))] #create blank bag of words list- change elements to represent if word exists or not

    #get a list of tokenized words
    s_words=nltk.word_tokenize(s)
    #stem words we did the same way before
    s_words=[stemmer.stem(word.lower()) for word in s_words]


#generate bag of words
#convert to numpy array
#return to where we need it
    for se in s_words:
        for i,w in enumerate(words):
            # if the words we are looking for is in our sentence..
            if w== se:
                bag[i]=1
    return np.array(bag)


#interaction with user
#

def chat():
    print('start talking with the bot (type quit to stop)!')
    while True:
        #if the user enters quit, while loop will be broken and stops running
        #if user does not types ,,quit"- we take whatever the user typed and put it to the bag of words function
        inp=input('You: ')
        if inp.lower()== 'quit':
            break

        #put words in the bag of words function
        results= model.predict([bag_of_words(inp, words)])
        #pick the answer with highest probability
        #gives us index with greatest value(probability) in list
        results_index=np.argmax(results)
        #gives back the labels it thinks our message is
        tag=labels[results_index]
        #print(results)#-give back the probabilities


        #if results[results_index] > 0.7:

        #pick response which matches with the tag from line before
        for tg in data['indian_restaurant']: #>0.7 (wenn ich will, dass Bot mind. 70% Gewissheit hat und erst dann Antwort gibt)
            if tg['tag']==tag:
                responses=tg['responses']
        print('RestaurantBot: '+ random.choice(responses))
        #else:
        #    print('Sorry, I did not get your question- I am a Bot and try to learn every day-Can you repeat that question for me?')#- obiges Beispiel mit 70%- wenn keine 70% Gewissheit
chat()















