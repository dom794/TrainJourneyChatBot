from userNLP import *
from linear_regression import *

class trainDelay():
    def __init__(self):
        self.time = None
        self.state = None
        self.arrdeppass = None
        self.station = None
        self.stationtiploc = None
        self.stationcat = None

    def reset(self):
        self.time = None
        self.state = None
        self.arrdeppass = None
        self.station = None
        self.stationtiploc = None
        self.stationcat = None
    
    def set_time(self, time):
        self.time = "10:00:00"

    def set_state(self, state):
        self.state = state
    
    def set_arrdeppass(self, arrdeppass):
        self.arrdeppass = arrdeppass

    def set_station(self, station):
        self.station = station

    def set_tiploc(self, tiploc):
        self.stationtiploc = tiploc

    def set_stationcat(self, stationcat):
        self.stationcat = stationcat
    
    

    #initial extraction of data
    def extract_data(self,user_input):
        extracted_station = extract_stations(user_input)
        extracted_time = extract_time1(user_input)[0]
        extracted_type = self.extract_type(user_input)
        print("Extracted stations", extracted_station)
        print("Extracted time", extracted_time)

        if extracted_station and self.station == None:
            self.set_station(extracted_station[0][1])
            print(self.station)
        if extracted_time and self.time == None:
            self.set_time(extracted_time)
            print(self.time)
        if extracted_type and self.arrdeppass == None:
            self.set_arrdeppass(extracted_type)
            print(self.arrdeppass)
    
    #check if all data has been extracted
    def check_extracted(self, thomas):
        if self.station == None:
            response = "Please enter the station name you'd like to check"
            self.set_state("station")
            return response
        elif self.get_station_tiploc() == False:
            response = "Please enter a valid station name on the Waterloo to Weymouth line"
            self.set_station(None)
            self.set_state("station")
            return response
        elif self.time == None:
            response = "Please enter the the expected time of arrival, departure or passing"
            self.set_state("time")
            return response
        elif self.arrdeppass == None:
            response = "Please enter whether you'd like to see the predicted arrival, departure or passing time"
            self.set_state("arrdeppass")
            return response
        else:
            print("all data extracted", self.station, self.time, self.arrdeppass, self.stationtiploc, self.stationcat)
            if self.arrdeppass == "arrival":
                response = "The predicted {} time for {} is {}".format(self.arrdeppass, self.station, self.arrival_models())
                self.reset()
                thomas.set_state("initial")
                return response
            elif self.arrdeppass == "departure":
                response = "The predicted {} time for {} is {}".format(self.arrdeppass, self.station, self.departure_model())
                self.reset()
                thomas.set_state("initial")
                return response
            elif self.arrdeppass == "passing":
                response = "The predicted {} time for {} is {}".format(self.arrdeppass, self.station, self.passing_model())
                self.reset()
                thomas.set_state("initial")
                return response
            else:
                response = "Something went wrong"
                self.reset()
                return response



    def check_status(self,thomas,user_input):
        if user_input.lower() == "stop" and self.state != "initialise":
            self.reset()
            thomas.set_state("initial")
            return "Train delay prediction cancelled. Let me know if you need anything else! 😊 "
        
        elif self.state == "initialise":
            self.extract_data(user_input)
            response = self.check_extracted(thomas)
            return response
        
        elif self.state == "station":
            station = extract_stations(user_input)
            if station:
                self.set_station(station[0][0])
                if (self.get_station_tiploc() == False):
                    self.set_station(None)
                    return "Please enter a valid station name on the Waterloo to Weymouth line"
                else:
                    response = self.check_extracted(thomas)
                    return response
        
        elif self.state == "time":
            time = extract_time1(user_input)
            if time:
                #check if the time has seconds, if not add :00
                if len(time) == 5:
                    time = time + ":00"
                print("Extracted time", time)
                self.set_time(time)
            else:
                self.set_state("time")
                return "Please enter your time in the format HH:MM or HH am / HH pm <br> You can type 'stop' to exit this booking process."
            
        elif self.state == "arrdeppass":
            if self.extract_type(user_input) == None:
                return "Please enter whether you'd like to see the predicted arrival, departure or passing time <br> You can type 'stop' to exit this booking process."

        response = self.check_extracted(thomas)
        return response
#code\random_forest_actual_arrival.pkl
    def arrival_models(self):
        model = load_model("random_forest_actual_arrival.pkl", "output/models/random_forest/")
        tpl = self.stationtiploc
        x_column = "scheduled_arrival"
        y_column = "actual_arrival"
        x_value = self.time
        df = convert_user_input(tpl, x_column, y_column, x_value)
        df = predict_user_input(df, x_column, y_column, model)
        if df["actual_arrival"][0] != None:
            return df["actual_arrival"][0]
        else:
            return "Test departure model failed"
        
    def departure_model(self):
        model = load_model("random_forest_actual_departure.pkl", "output/models/random_forest/")
        tpl = self.stationtiploc
        x_column = "scheduled_departure"
        y_column = "actual_departure"
        x_value = self.time
        df = convert_user_input(tpl, x_column, y_column, x_value)
        df = predict_user_input(df, x_column, y_column, model)
        print(df)

        if df["actual_departure"][0] != None:
            return df["actual_departure"][0]
        else:
            return "Test departure model failed"
        
    def passing_model(self):
        model = load_model("random_forest_actual_passing.pkl", "output/models/random_forest/")
        tpl = self.stationtiploc
        x_column = "scheduled_passing"
        y_column = "actual_passing"
        x_value = self.time
        df = convert_user_input(tpl, x_column, y_column, x_value)
        df = predict_user_input(df, x_column, y_column, model)
        print(df)
        if df["actual_passing"][0] != None:
            return df["actual_passing"][0]
        else:
            return "Test departure model failed"
    

    def extract_type(self,userInput):
        #check if either arrival, departure or passing is in the user input
        if "arrival" in userInput:
            self.set_arrdeppass("arrival")
            return True
        elif "departure" in userInput:
            self.set_arrdeppass("departure")
            return True
        elif "passing" in userInput:
            self.set_arrdeppass("passing")
            return True
        else:
            return None
    
        
    def get_station_tiploc(self):
        with open("data/processed/tiploc.json", "r") as f:
            station_tiploc_dict = json.load(f)
        station_upper = str.upper(self.station)
        if station_upper in station_tiploc_dict.keys():
            self.set_tiploc(station_tiploc_dict[station_upper])
            with open("data/processed/categorical_dict.json", "r") as f:
                station_tiploc_dict = json.load(f)
            self.set_stationcat(station_tiploc_dict[self.stationtiploc])
            return True
        else:
            self.set_station(None)
            return False
        

