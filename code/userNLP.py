from nltk import PorterStemmer, word_tokenize, pos_tag
from nltk.corpus import stopwords
import string
from keras.models import load_model
#for creating pkl files
import pickle
import json
import numpy
from tqdm import tqdm
from pathlib import Path
import spacy
import random
from spacy.training import Example
from spacy.pipeline import EntityRecognizer
import re
from fuzzywuzzy import fuzz
import datetime
from datetime import timedelta
import numpy as np
import dateparser
from typing import Tuple, List

model = load_model('code/model.keras')
intents = json.loads(open('code/intents.json').read())["intents"]
words = pickle.load(open('code/words.pkl', 'rb'))
classes = pickle.load(open('code/classes.pkl', 'rb'))
nlp = spacy.load('en_core_web_sm')
from nltk.stem import WordNetLemmatizer

def bag_of_words(user_input, words):
    lemmatizer = WordNetLemmatizer()
    user_input = user_input.lower()
    word_tokens = word_tokenize(user_input)
    word_tokens = [lemmatizer.lemmatize(w) for w in word_tokens] # use lemmatization instead of stemming
    bag = [1 if w in word_tokens else 0 for w in words]
    return bag

def predict_intent(sentence):
    bag = bag_of_words(sentence, words)
    bag = [bag]
    bag = np.array(bag)
    results = model.predict(bag)[0]
    results = [[i, r] for i, r in enumerate(results) if r > 0.6]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    print('Predicted intents in order: ', return_list)
    #check if any of the values in return_list < 0.6
    if return_list == []:
        return_list.append({"intent": "unknown", "probability": "1"})
    return return_list[0]["intent"]




def get_response(user_input, intents):
    sorted_results = predict_intent(user_input)
    for intent in intents:
        if intent["tag"] == sorted_results[0]["intent"]:
            response = intent["responses"]
#sure there is a better way of doing this but it works sometimes
#changed get station codes so that it works with a single station input


def get_station_code(station_name, sentence):
    with open('code/station_name_code.json') as f:
        station_names = json.load(f)

    # Remove punctuation and split sentence into words
    sentence = re.sub(r'[^\w\s]', '', sentence)
    words = sentence.lower().split()
    
    variations = []
    if(station_name.lower() in words):
        for i in range(max(0, words.index(station_name.lower())-2), min(len(words), words.index(station_name.lower())+3)):
            if words[i] != station_name:
                variations.append(" ".join(words[max(0, i-2):min(len(words), i+3)]))  
    else:      
        for i in range(len(words)):
            if words[i] == station_name.lower():
                if i > 0:
                    variations.append(" ".join(words[i-1:i+1]))
                if i < len(words) - 1:
                    variations.append(" ".join(words[i:i+2]))
                variations.append(words[i])
    # Check if station name or any of its variations are in the station names list
    max_ratio = 75
    closest_match = None
    for name, code in station_names:
        if station_name.lower() == name.lower():
            return code
        ratio = fuzz.token_sort_ratio(station_name.lower(), name.lower())
        if ratio > max_ratio:
            max_ratio = ratio
            closest_match = code
        for variation in variations:
            variation_ratio = fuzz.token_sort_ratio(variation, name.lower())
            if variation_ratio > max_ratio:
                max_ratio = variation_ratio
                closest_match = code
    return closest_match


#uses the spacy model to extract entities from user input
def extract_stations(input_text):
    ret = []
    model1 = spacy.load("output/models/nlp")
    nlpmessage = model1(input_text)
    for ent in nlpmessage.ents:
        if ent.label_ == "FROM_STA" or ent.label_ == "TO_STA":
            ret.append([ent.text, ent.label_])

    #use regex to find stations that are not in the spacy model (following from or to)
    if [item for item in ret if item[1] == "FROM_STA"] == []:
        try:
            from_station = re.search(r'from (.*?) to', input_text)
            ret.append([from_station.group(1), "FROM_STA"])
        except:
            #check if the user input exists in the station list
            with open('code/station_name_code.json') as f:
                station_names = json.load(f)
            for name, code in station_names:
                if input_text.lower() == name.lower():
                    ret.append([input_text, "TO_STA"])
    if [item for item in ret if item[1] == "TO_STA"] == []:
        try:
            to_station = re.search(r'to (.*?) from', input_text)
            ret.append([to_station.group(1), "TO_STA"])
        except:
            #check if the user input exists in the station list
            with open('code/station_name_code.json') as f:
                station_names = json.load(f)
            for name, code in station_names:
                if input_text.lower() == name.lower():
                    ret.append([input_text, "TO_STA"])
    return ret

def extract_time(text):
    # remove punctiation from the text
    text = text.replace("?", "")
    
    # Try to parse date and time from text using dateparser
    parsed_date = dateparser.parse(text)

    if parsed_date is not None:
        # Format the parsed time
        parsed_time = parsed_date.strftime("%H:%M")

        # Create a regular expression to remove the parsed time from the text
        time_regex = re.escape(parsed_time)

        if "am" in text or "pm" in text:
            # If the text includes "am" or "pm", include it in the regex
            time_regex += r"\s*[ap]m"

        # Remove the parsed time from the text
        text = re.sub(time_regex, "", text, flags=re.IGNORECASE).strip()

        return parsed_time, text
    else:
        return None, text

def extract_time1(text):
    doc = nlp(text)
    #remove punctiation from the text
    text = text.replace("?","")
    for ent in doc.ents:
        if ent.label_ == "TIME":
            if ent.text == "now":
                #remove now from the text
                text = text.replace(ent.text, "")
                return datetime.datetime.now().strftime("%H:%M"), text
            #check if its laid out as 12am or 12pm - turn to datetime format
            else:
                #turn into datetime format
                try:
                    #remove the time from the text
                    text = text.replace(ent.text, "")
                    return datetime.datetime.strptime(ent.text, "%H:%M").strftime("%H:%M"), text
                except:
                    pass
    #check if there is any time in the text e.g " 11 " or " 3 "
        #check if there is any time in the text 10:30 - add 12 hours if its pm
    if re.search(r'\d{1,2}:\d{2}', text):
        time_text = re.search(r'\d{1,2}:\d{2}', text).group()
        time = datetime.datetime.strptime(re.search(r'\d{1,2}:\d{2}', text).group(), '%H:%M').time()
        #check if there is a pm followed by the time variable just found
        if re.search(fr'{time_text}pm', text):
            if time.hour < 12:
                #add 12 hours to the time
                return (datetime.datetime.combine(datetime.date.today(), time) + datetime.timedelta(hours=12)).time(), text.replace(re.search(r'\d{1,2}(pm)', text).group(), "")
        #turn into datetime format
        return time, text.replace(re.search(r'\d{1,2}:\d{2}', text).group(), "")
    #checks for 10am or 10pm, 10:15am, 10:15pm, 10:15 am, 10:15 pm
    elif re.search(r'\d{1,2}:\d{2}\s*[ap]m', text):
        time_match = re.search(r'\d{1,2}:\d{2}', text)
        time_str = time_match.group().replace(" ", "").replace(":", "")
        hour = int(time_str[:2])
        minute = int(time_str[2:])
        time_suffix = re.search(r'[ap]m', text).group()
        #remove the time from the text
        text = text.replace(time_match.group(), "")
        # Adjust hour based on am/pm
        if time_suffix == 'pm' and hour < 12:
            hour += 12
            # Create a time object
        return datetime.time(hour=hour, minute=minute), text
    #if now is entered
    elif text == "now":
        #remove now from the text
        text = text.replace("now", "")
        return datetime.datetime.now().strftime("%H:%M"), text
    #search for 10am or 10pm
    elif re.search(r'\d{1,2}(am|pm)', text):
        #if its pm add 12 hours e.g. 5pm -> 17:00 but 14pm -> 14:00
        time = datetime.datetime.strptime(re.search(r'\d{1,2}', text).group(), '%H').time()
        if re.search(r'\d{1,2}(pm)', text):
            #turn into datetime format
            if time.hour < 12:
                #add 12 hours to the time
                return (datetime.datetime.strptime(re.search(r'\d{1,2}', text).group(), '%H') + datetime.timedelta(hours=12)).strftime("%H:%M:%S"), text.replace(re.search(r'\d{1,2}(pm)', text).group(), "")
            #remove the time from the text
        return time, text.replace(re.search(r'\d{1,2}(pm)', text).group(), "")
    #search for number
    elif re.search(r'\d{1,2}', text):
        #turn into datetime format
        #remove the time from the text
        return datetime.datetime.strptime(re.search(r'\d{1,2}', text).group(), "%H").strftime("%H:%M"), text.replace(re.search(r'\d{1,2}', text).group(), "")
        
    return None, text
  
def extract_date(text: str, startdate: str = None) -> Tuple[List[str], str]:
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    months = ["january", "february", "march", "april", "may", "june", "july", "august","september", "october", "november", "december"]
    doc = nlp(text)
    dates = []
    for ent in doc.ents:
        if ent.label == "DATE":
            if ent.text.lower() == "today" or ent.text.lower() == "now":
                dates.append(datetime.datetime.now().strftime("%d-%m-%y"))
                text = text.replace(ent.text, "")
            elif ent.text.lower() == "tomorrow":
                dates.append((datetime.datetime.now() + datetime.timedelta(1)).strftime("%d-%m-%y"))
                text = text.replace(ent.text, "")
            elif ent.text.lower() in days:
                today = datetime.datetime.today()
                while today.weekday() != days.index(ent.text.lower()):
                    today += datetime.timedelta(1) 
                dates.append(today.strftime("%d-%m-%y"))
                text = text.replace(ent.text, "")
            elif ent.text.lower() in months:
                today = datetime.datetime.today()
                while today.month != months.index(ent.text.lower()) + 1:
                    today += datetime.timedelta(1)
                dates.append(today.strftime("%d-%m-%y"))
                text = text.replace(ent.text, "")
            else:
                try:
                    date = dateparser.parse(ent.text)
                    dates.append(date.strftime("%d-%m-%y"))
                    text = text.replace(ent.text, "")
                except:
                    pass
            return dates[0], text
    # if no specific date recognized by Spacy, use dateparser
    parsed_date = dateparser.parse(text)
    if parsed_date is not None:
        return parsed_date.strftime("%d-%m-%y"), text.replace(str(parsed_date), "")
    elif re.search(r'\d{1,2} days (later|after)', text):
        days = int(re.search(r'\d+', text).group())
        print("days",days)
        if startdate != None:
            #turn start date into datetime format so the addition works
            start_date = datetime.datetime.strptime(start_date, "%d-%m-%y")
            return (start_date + datetime.timedelta(days)).strftime("%d-%m-%y"), text.replace(re.search(r'\d+ days (later|after)', text).group(), "")
        else:
            return (datetime.datetime.now() + datetime.timedelta(days)).strftime("%d-%m-%y"), text.replace(re.search(r'\d+ days (later|after)', text).group(), "")
    return None, text

def extract_railcard(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "DISCOUNT":
            return ent.text
    if text.lower() == "no":
        return "no"
    #use fuzzy matching to find railcard only if its above 70
    railcards = ['16-17 Saver', '16-25 Railcard', '26-30 Railcard', 'Disabled Persons Railcard', 'Family & Friends Railcard', 'Highland Railcard', 'HM Forces Railcard', 'JobCentre Plus Travel Discount Card', 'New Deal Photocard Scotland', 'Network Railcard', 'Senior Railcard', 'Two Together Railcard', 'Veterans Railcard']
    max_ratio = 59
    closest_match = None
    for railcard in railcards:
        ratio = fuzz.token_sort_ratio(text.lower(), railcard.lower())
        if ratio > max_ratio:
            max_ratio = ratio
            closest_match = railcard
    return closest_match