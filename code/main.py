import random

from flask import Flask, render_template, request
from flask import redirect, url_for
from nltk.corpus import stopwords
from nltk import PorterStemmer, word_tokenize, pos_tag
import nltk 
# nltk.download('wordnet')
# nltk.download('punkt')
import string
import json
import re
import datetime
from difflib import SequenceMatcher
from userNLP import *
import pyttsx3
import threading
from queue import Queue
from flask import Flask, render_template, request
import pythoncom

# initialise the darwin LDB soap session
from nredarwin.webservice import DarwinLdbSession
darwin_sesh = DarwinLdbSession(wsdl="https://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx", api_key="089c48ee-4aaa-460b-a987-bc906bb54985")

from train_booker import *
from train_delay import *
# initial chatbot class
class ChatBot:
    # initialise the chatbot
    def __init__(self):
        self.name = "ChatBot"
        self.greeting = "Hello, I am Thomas. How can I help you?"
        self.intents = self.load_intents()
        self.state = "initial"
        self.train_booker = trainBooker()
        self.train_delay = trainDelay()
        self.words = []
        self.liveTrainSource = ""
        self.liveTrainDestination = ""
        

    def set_state(self, state):
        self.state = state
   
    # methods 

    def retrieve_first_available(self, source, destination):
        board_list = []
        # create a board that shows the next 10 trains from the source station to the destination station
        board = darwin_sesh.get_station_board(crs=source, rows=10,destination_crs=destination)  
        for service in board.train_services:
            if service.platform == None:
                platform = "to be announced"
            else:
                platform = service.platform
            board_list.append([service.std, service.etd, service.destination_text, platform])
        
        print("\n")
        print("board list = ", board_list)
        print("Service details for the first available service from: ", source, "to", destination)
        try:
            service_id = board.train_services[0].service_id
            service = darwin_sesh.get_service_details(service_id)
            for calling_point in service.subsequent_calling_points: 
                print(calling_point.location_name, calling_point.st, calling_point.et)
        

            first_available = "The first available train from " + source + " to " + destination + " is: " + "\n" + board_list[0][0] + " - the service is running " + board_list[0][1].lower() + " from platform " + str(board_list[0][3]) + "." + "\n"
            first_available = first_available.replace('\n', '<br>')

        
            return first_available
        except:
            
            return None
        
    def retrieve_remaining_services(self, source, destination):
        board_list = []
        board = darwin_sesh.get_station_board(crs=source, rows=100,destination_crs=destination)  
        for service in board.train_services:
            if service.platform == None:
                platform = "to be announced"
            else:
                platform = service.platform
            board_list.append([service.std, service.etd, platform,service.service_id])
        board_list_string = ""
        for board in board_list:
            board_list_string = board_list_string + source + " to " + destination + " " + board[0] + " - the service is departing " + board[1].lower() + " from platform " + str(board[2]) + "." + "<br>"
        return board_list_string

    # load the intents from the intents.json file to be used by the chatbot to classify user input
    def load_intents(self):
        with open("code/intents.json") as file:
            intents = json.load(file)
        return intents["intents"]
    
    
    #generate a response based on the predicted intent
    def generate_response(self, tag):
        #Returns a response based on the predicted intent
        for intent in self.intents:
            if intent["tag"] == tag:
                responses = intent["responses"]
                return random.choice(responses)

        # generate a response based on the user input and the intent
        #need to make it so that it can get to and from stations from the user, what time etc depending on what variable the user inputs
    def chatbot_response(self, user_input):
        # DEBUG display current chatbot mode
        print("Chatbot mode: " + self.state)
        print("User input: " + user_input)
        intent = predict_intent(user_input)
        
        
    

        
        # LIVE TRAIN TIMES CODE - used to retrieve live train times
        
        if intent == 'live-trains' and self.state == 'initial':
            self.set_state('live-trains')
            response = 'Okay, we can look up live train times. What is the station you are travelling from?'
            return response
        
        if self.state == 'live-trains':
            if user_input == 'stop':
                self.set_state('initial')
                response = 'Okay, I\'ve stopped looking up live train times. What else can I help you with?'
                return response
            with open('code/station_name_code.json') as f:
                station_codes = json.load(f)

            highest_match = {'ratio': 0, 'station': None}

            for station in station_codes:
                ratio = fuzz.ratio(user_input.lower(), station[0].lower())
                if ratio > highest_match['ratio']:
                    highest_match = {'ratio': ratio, 'station': station}

            if highest_match['ratio'] > 80:
                self.liveTrainSource = highest_match['station'][1]
                response = 'And what is the destination station?'
                self.set_state('live-trains-destination')
            else:
                response = 'I couldn\'t find that station. Could you please try again?<br> If you want to stop looking up live train times, please type "stop".'

            return response

        if self.state == 'live-trains-destination':
            with open('code/station_name_code.json') as f:
                station_codes = json.load(f)

            highest_match = {'ratio': 0, 'station': None}

            for station in station_codes:
                ratio = fuzz.ratio(user_input.lower(), station[0].lower())
                if ratio > highest_match['ratio']:
                    highest_match = {'ratio': ratio, 'station': station}

            if highest_match['ratio'] > 80:
                self.liveTrainDestination = highest_match['station'][1]
                first_available_response = self.retrieve_first_available(self.liveTrainSource, self.liveTrainDestination)
                if first_available_response is not None:
                    response = first_available_response + "<br>Do you want to see the full timetable?"
                    self.set_state('live-trains-full-timetable')
                else:
                    response = "There are no trains available for this journey at this time. Please try again later."
                    self.set_state('initial')
            else:
                response = 'I couldn\'t find that station. Could you please try again?'

            return response

        if self.state == 'live-trains-full-timetable':
            if user_input.lower() == 'yes':
                remaining_services_response = self.retrieve_remaining_services(self.liveTrainSource, self.liveTrainDestination)
                if remaining_services_response:
                    response = remaining_services_response
                else :
                    response = "There are no trains available for this journey. Please try again later."
            else:
                response = "Okay. Do you need help with anything else?"
                self.set_state('initial')  # Going back to the initial state
            return response


        
        # allows user to end the conversation

        if intent == 'goodbye' or user_input == 'end':
            self.set_state('end')
            response = 'Are you sure you want to end this conversation?'
            return response

        if self.state == 'end':
            if user_input.lower() == 'yes':
                response = 'Thanks for using our chatbot. Have a nice day!'
                self.set_state('initial')
                self.end_bool = True
            elif user_input.lower() == 'no':
                response = 'Okay, I will continue to help you.'
                self.set_state('initial')
            else:
                response = 'I\'m sorry, I didn\'t understand that. Please type yes or no.'
            return response

        # MAIN BOOKING CODE - used to book a train ticket
        # sends the user input to the train booker class to be processed
        if self.state == 'booking':
            response = self.train_booker.check_status(self, user_input)
            print(self.state)
            return response
        
        if self.state == 'train_delay':
            response = self.train_delay.check_status(self, user_input)
            print(self.state)
            return response
        
        # STATION LOOKUP CODE - used to find the name of a station based on user input
        
        if intent == "station-lookup" and self.state == "initial":
            self.set_state("station-lookup")
            response = self.generate_response(intent)
            return response

        if self.state == 'station-lookup':
            if user_input == 'stop':
                self.set_state('initial')
                return 'Okay, I will stop looking for stations.'
            
            closest_stations = []
            with open('code/station_name_code.json') as f:
                station_names = json.load(f)

            for station in station_names:
                ratio = fuzz.token_set_ratio(user_input, station)  
                if ratio > 80:
                    closest_stations.append((station, ratio))

            closest_stations.sort(key=lambda x: x[1], reverse=True)

            if len(closest_stations) == 1:
                self.set_state("initial")
                station = closest_stations[0][0]  # this should be a list with the station name and code
                station_name = station[0]  # the first element should be the station name
                station_link = station_name.lower().replace(" ", "-")
                return f"The station you are looking for is {station_name}.<br> Here is a <a href='https://www.nationalrail.co.uk/stations/{station_link}'>link</a> to the station for more information."


            elif len(closest_stations) > 1:
                station_names = [station[0][0] for station in closest_stations]  # get the station names from the tuples
                station_codes = [station[0][1] for station in closest_stations]  # get the station codes from the tuples
                station_list = "\n".join(f"{i+1}. {name} (Code: {code})" for i, (name, code) in enumerate(zip(station_names, station_codes)))
                return "I found multiple stations, here are the stations I found:<br><br>" + station_list.replace('\n', '<br>') + "<br><br>Please type the station code or name of the station you want more information about."


            else:
                return "I couldn't find any stations, please try again."


        if intent == "booking":
            self.set_state("booking")
            self.train_booker.set_state("booking")
            response = self.train_booker.check_status(self, user_input)
            return response

    

        if intent == "train-delay":
            self.set_state("train_delay")
            response = self.train_delay.check_status(self, user_input)
            return response

        elif intent is not None and user_input != 'end':
            response = self.generate_response(intent)
            return response

        else:
            response = "I'm sorry, I don't understand. Can you please rephrase your previous message, or provide more information?"
            return response

    #NER - extract stations from user input
    def time_check(self, user_input):
        ent = extract_time(user_input)
        if ent == None:
            return "I'm sorry, I didn't understand that. Please rephrase your previous message, or provide more information."
        else:
            return ent        
        
#tts messages held here
ttsq = Queue()

#do the tts in a seperate thread
def ttsFunction():
    pythoncom.CoInitialize()
    engine = pyttsx3.init()
    #while true say the messages
    while True:
        text = ttsq.get()
        engine.say(text)
        engine.runAndWait()
        ttsq.task_done()

# start the tts thread
ttst = threading.Thread(target=ttsFunction)
ttst.daemon = True
ttst.start()

# Flask app to run the chatbot
app = Flask(__name__)
app.static_folder = 'static'

# render the homepage
@app.route("/")
def home():
    return render_template("index.html")

# get the user input and return the chatbot response on the homepage
@app.route("/get")
def get_bot_response():
    user_input = request.args.get('msg')
    response = thomas.chatbot_response(user_input)
    edited_response = response.replace('<br>', '')
    edited_response.replace('<a href=', '')
    edited_response.replace('</a>', '')
    edited_response.replace('>', '')
    edited_response.replace('\n', '')
    if tts_on:
        ttsq.put(edited_response)
    history = {"message": user_input, "response": response}
    # load existing data
    with open("code/history.json", "r") as file:
        chatbot_history = json.load(file)
    # append new data 
    chatbot_history.append(history)
    # write updated data 
    with open("code/history.json", "w") as file:
        json.dump(chatbot_history, file, indent=5)
    return response

# tts on by default, allows user to toggle tts on/off via button on the interface
tts_on = True

@app.route("/enable_speech", methods=["POST"])
def toggle_tts():
    global tts_on
    tts_on = not tts_on
    if tts_on:
        return "TTS On"
    else:
        return "TTS Off"

if __name__ == "__main__":
    with open("code/history.json", "r") as file:
        chatbot_history = json.load(file)
    # create an instance of the chatbot
    thomas = ChatBot()
    # run the flask app
    # app.run(host='0.0.0.0',port=8000, debug=True)
    app.run()

    

