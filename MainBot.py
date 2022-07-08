import nltk
import numpy as np
import string
import warnings
from sklearn.feature_extraction.text import TfidfVectorizer   # For Tfid Vectorizer
from sklearn.metrics.pairwise import cosine_similarity  
from decouple import config

API_TOKEN = config('TOKEN')

warnings.filterwarnings("ignore")
f = open('file.txt','r',errors = 'ignore', encoding = 'utf-8')
paragraph = f.read()

greetings = ['Hey', 'Hello', 'Hi', 'It’s great to see you', 'Nice to see you', 'Good to see you']
bye = ['Bye', 'Bye-Bye', 'Goodbye', 'Have a good day','Stop']
thank_you = ['Thanks', 'Thank you', 'Thanks a bunch', 'Thanks a lot.', 'Thank you very much', 'Thanks so much', 'Thank you so much']
thank_response = ['You\'re welcome.' , 'No problem.', 'No worries.', ' My pleasure.' , 'It was the least I could do.', 'Glad to help.']



sent_tokens = nltk.sent_tokenize(paragraph)
word_tokens = nltk.word_tokenize(paragraph)

# Lemmitization

lemmer = nltk.stem.WordNetLemmatizer()

def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]   

# string.punctuation has all the punctuations
# ord(punct) convert punctuation to its ASCII value
# dict contains {ASCII: None} for punctuation mark

remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

# remove_punct_dict

# This will return the word to LemTokens after Word tokenize, lowering its case and removing punctuation mark
# translate will find punctuation mark in remove_punct_dict and if found replace it with None

def Normalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))


def response(user_response):
    robo_response = ''
    
    sent_tokens.append(user_response)   # Appending the Question user ask to sent_tokens to find the Tf-Idf and cosine_similarity between User query and the content.
    TfidfVec = TfidfVectorizer(tokenizer = Normalize, stop_words='english')    #tokenizer ask about Pre-processing parameter and it will consume the Normalize() function and it will also remove StopWords
    tfidf = TfidfVec.fit_transform(sent_tokens)

    vals = cosine_similarity(tfidf[-1], tfidf)    # It will do cosine_similarity between last vectors and all the vectors because last vector contain the User query
    idx = vals.argsort()[0][-2]     # argsort() will sort the tf_idf in ascending order. [-2] means second last index i.e. index of second highest value after sorting the cosine_similarity. Index of last element is not taken as query is added at end and it will have the cosine_similarity with itself.

    flat = vals.flatten()   # [[0,...,0.89,1]] -> [0,...,0.89,1] this will make a single list of vals which had list inside a list.
    flat.sort()
    req_tfidf = flat[-2]  # this contains tfid value of second highest cosine similarity

    if(req_tfidf == 0):    # 0 means there is no similarity between the question and answer
        robo_response = robo_response + "I am sorry! I don't understand you. Please rephrase you query."
        return robo_response
    
    else:
        robo_response = robo_response + sent_tokens[idx]    # return the sentences at index -2 as answer
        return robo_response


import random

def bot_initialize(user_msg):
    flag=True
    while(flag==True):
        user_response = user_msg
        if(user_response not in bye):
            if(user_response == '/start'):
                bot_resp = """Hi! There. I am your Corona Protector. I can tell you all the Facts and Figures, Signs and Symptoms related to spread of Covid-19 in India. \nType Bye to Exit.""" 
                return bot_resp
            elif(user_response in thank_you):
                bot_resp = random.choice(thank_response)
                return bot_resp
            elif(user_response in greetings):
                bot_resp = random.choice(greetings) + ", What information you what related to Covid-19 in India"
                return bot_resp
            else:
                user_response = user_response.lower()
                bot_resp = response(user_response)
                sent_tokens.remove(user_response)   # remove user question from sent_token that we added in sent_token in response() to find the Tf-Idf and cosine_similarity
                return bot_resp
        else:
            flag = False
            bot_resp = random.choice(bye)
            return bot_resp


import requests
import json

class telegram_bot():
    def __init__(self):
        self.token = API_TOKEN    #write your token here!
        self.url = f"https://api.telegram.org/bot{self.token}"

    def get_updates(self,offset=None):
        url = self.url+"/getUpdates?timeout=100"   # In 100 seconds if user input query then process that, use it as the read timeout from the server
        if offset:
            url = url+f"&offset={offset+1}"
        url_info = requests.get(url)
        return json.loads(url_info.content)

    def send_message(self,msg,chat_id):
        url = self.url + f"/sendMessage?chat_id={chat_id}&text={msg}"
        if msg is not None:
            requests.get(url)

    def grab_token(self):
        return tokens


tbot = telegram_bot()

update_id = None

def make_reply(msg):     # user input will go here
  
    if msg is not None:
        reply = bot_initialize(msg)     # user input will start processing from bot_initialize function
    return reply

try:       
    while True:
        # print("...")
        updates = tbot.get_updates(offset=update_id)
        updates = updates['result']
        # print(updates)
        if updates:
            for item in updates:
                update_id = item["update_id"]
                # print(update_id)
                try:
                    message = item["message"]["text"]
                    # print(message)
                except:
                    message = None
                from_ = item["message"]["from"]["id"]
                # print(from_)

                reply = make_reply(message)
                tbot.send_message(reply,from_)
except Exception as err:
    print(err)