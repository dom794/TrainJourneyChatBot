from userNLP import *
# initialise the darwin LDB soap session
from nredarwin.webservice import DarwinLdbSession
darwin_sesh = DarwinLdbSession(wsdl="https://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx", api_key="089c48ee-4aaa-460b-a987-bc906bb54985")
from scraper import *
from main import *

class trainBooker:
    def __init__(self):
        self.source = None
        self.destination = None
        self.end_bool = False
        self.railcard = None
        self.date = None
        self.time = None
        self.state = False
        self.returnbool = True
        self.retdate = None
        self.rettime = None
        self.depart_arrive = None

    def reset(self):
        self.source = None
        self.destination = None
        self.end_bool = False
        self.railcard = None
        self.date = None
        self.time = None
        self.state = False
        self.returnbool = True
        self.retdate = None
        self.rettime = None
        self.depart_arrive = None

    def set_state(self, state):
        self.state = state

    def set_source(self, source):
        self.source = source
    
    def set_destination(self, destination):
        self.destination = destination
    
    def set_date(self, date):
        self.date = date
    
    def set_time(self, time):
        self.time = time
    
    def set_railcard(self, railcard):
        self.railcard = railcard

    def set_returnbool(self, returnbool):
        self.returnbool = returnbool
    
    def set_retdate(self, retdate):
        self.retdate = retdate
    
    def set_rettime(self, rettime):
        self.rettime = rettime
    
    def set_depart_arrive(self, depart_arrive):
        self.depart_arrive = depart_arrive

    
    def extract_data(self,user_input):
        extracted_stations = extract_stations(user_input)
        extracted_time, user_input2 = extract_time1(user_input)
        extracted_date, user_input3 = extract_date(user_input2, None)
        extracted_railcard = extract_railcard(user_input)
        print("Extracted stations", extracted_stations)
        print("Extracted time", extracted_time)
        print("Extracted date", extracted_date)
        print("Extracted railcard", extracted_railcard)

        print(user_input2)

        if "return" or "come back" in user_input.lower():
            #try to extract a second return date and time
            self.set_returnbool(True)
            extracted_retdate, user_input4 = extract_date(user_input3, extracted_date)
            extracted_rettime, text = extract_time1(user_input4)
        print("Extracted return date", extracted_retdate)
        print("Extracted return time", extracted_rettime)

        #check if the stations exist in the station list
        extracted_stations = list(filter(None, extracted_stations))
        print('Filtered station codes = ', extracted_stations)

        #check what data has been pulled and ask for the rest

        #source station
        if any(subarray[1] == 'FROM_STA' for subarray in extracted_stations) and self.source == None:
            print([subarray[0] for subarray in extracted_stations if subarray[1] == 'FROM_STA' ][0])
            self.set_source(get_station_code([subarray[0] for subarray in extracted_stations if subarray[1] == 'FROM_STA' ][0],user_input))
            print('Source = ', self.source)
        #destination station
        if any(subarray[1] == 'TO_STA' for subarray in extracted_stations) and self.destination == None:
            self.set_destination(get_station_code([subarray[0] for subarray in extracted_stations if subarray[1] == 'TO_STA' ][0],user_input))
            print('Destination = ', self.destination)
        #date
        if extracted_date != None and self.date == None:
            self.set_date(extracted_date)
            print('Date = ', self.date)
        #time
        if extracted_time != None and self.time == None:
            self.set_time(extracted_time)
            print('Time = ', self.time)
        #railcard
        if extracted_railcard != None and self.railcard == None:
            self.set_railcard(extracted_railcard)
            print('Railcard = ', self.railcard)
        #rettime
        if extracted_rettime != None and self.retdate == None:
            self.set_rettime(extracted_rettime)
            print('rettime = ', self.rettime)
        #retdate
        if extracted_retdate != None and self.retdate == None:
            self.set_retdate(extracted_retdate)
            print('retdate = ', self.retdate)

    
    def check_extracted(self):
        # checking all the extracted data is valid

        if self.source == None:
            response = "What station are you travelling from?"
            self.set_state("source")
            return response
      
        if self.destination == None:
            response = "What station are you travelling to?"
            self.set_state("destination")
            return response
        
        elif not self.station_identical_check():
            response = "You cannot book a ticket to the same location. Please enter a different destination."
            self.set_destination(None)
            self.set_state("destination")
            return response
        elif self.date == None:
            response = "What date are you travelling?"
            self.set_state("date")
            return response
        #check date is not in the past
        if self.date != None and self.date_check() == False:
            response = "Please enter a valid date in the future"
            self.set_date(None)
            self.set_state("date")
            return response
        elif self.time == None:
            response = "What time are you travelling?"
            self.set_state("time")
            return response
        #check time isnt in the past
        elif self.time != None and self.time_check() == False:
            response = "Please enter a valid time in the future"
            self.set_time(None)
            self.set_state("time")
            return response
        elif self.railcard == None:
            response = "Do you have a railcard?"
            self.set_state("railcard")
            return response        
        elif self.returnbool == True and self.retdate == None and self.rettime == None:
            response = "Do you want to book a return ticket?"
            self.set_state("return")
            return response
        elif self.retdate == None and self.returnbool == True:
            response = "What day do you want to return?"
            self.set_state("retdate")
            return response
        elif self.rettime == None and self.returnbool == True:
            response = "What time do you want to return?"
            self.set_state("rettime")
            return response
        else:
            print("all data extracted", self.source, self.destination, self.date, self.time, self.railcard, self.retdate, self.rettime)
            cheapest_ticket_url = get_cheapest_ticket(self.source, self.destination, self.date, self.time, self.railcard, self.retdate, self.rettime)
            print("Cheapest ticket url: ", cheapest_ticket_url)
            response = cheapest_ticket_url
            self.reset()
            return response

        
    
    #checks what it should do next deepending on the state
    def check_status(self,thomas,user_input):
        if user_input.lower() == "stop" and self.state != "booking":
            self.reset()
            thomas.set_state("initial")
            return "Booking process cancelled. Let me know if you need anything else! 😊 "
        #if else dependent on state - if trying to get a single variable
        if self.state == "booking":
            self.extract_data(user_input)
            response = self.check_extracted()
            return response
        elif self.state == "source":
            if self.station_ambiguous_check(user_input) == True:
                print("station ambig return TRUE")
                if (get_station_code(user_input, user_input) != None):
                    station_code = get_station_code(user_input, user_input)
                else:
                    print('station ambig return else')
                    station = extract_stations(user_input)
                    if station:
                        station_code = get_station_code([subarray[0] for subarray in station if subarray[1] == 'FROM_STA' ][0],user_input)
                    else:
                        return "Sorry, I couldn't find that station. Please try again. <br> You can type 'stop' to exit this booking process."
                self.set_source(station_code)
            else:
                return self.station_ambiguous_check(user_input)
        elif self.state == "destination":
            if self.station_ambiguous_check(user_input) == True:
                print("station dest ambig return TRUE")
                if (get_station_code(user_input, user_input) != None):
                    station_code = get_station_code(user_input, user_input)
                else:
                    station = extract_stations(user_input)
                    if station:
                        station_code = get_station_code([subarray[0] for subarray in station if subarray[1] == 'FROM_STA' ][0],user_input)
                    else:
                        return "Sorry, I couldn't find that station. Please try again. <br> You can type 'stop' to exit this booking process."
                self.set_destination(station_code)
            else:
                    return self.station_ambiguous_check(user_input)
        elif self.state == "date":
            date, text = extract_date(user_input, None)
            if date:
                self.set_date(date)
            else:
                return "Please enter your date in the format DD/MM/YYYY. <br> You can type 'stop' to exit this booking process."
            
        elif self.state == "time":
            time, text = extract_time(user_input)
            if time:
                self.set_time(time)
            else:
                return "Please enter your time in the format HH:MM or HH am / HH pm <br> You can type 'stop' to exit this booking process."
        elif self.state == "railcard":
            railcard = extract_railcard(user_input)
            if railcard:
                self.set_railcard(railcard)
            else:
                return "Please enter the name of your railcard. For information about railcards you can visit our <a href='https://www.nationalrail.co.uk/tickets-railcards-and-offers/railcards/'>railcard page.</a> <br> You can type 'stop' to exit this booking process."
            
        elif self.state == "return":
            if user_input == "yes":
                if self.retdate == None:
                    self.set_state("retdate")
                    response = "What date do you want to return?"
                    return response
            elif user_input == "no":
                self.set_returnbool(False)
        elif self.state == "retdate":
            retdate, text = extract_date(user_input, self.date)
            if retdate:
                # Check if return date is not earlier than the outgoing journey date
                if retdate >= self.date:  
                    self.set_retdate(retdate)
                else:
                    return "Your return date can't be earlier than your outgoing journey. Please enter a valid return date in the format DD/MM/YYYY. <br> You can type 'stop' to exit this booking process."
            else:
                return "Please enter your date in the format DD/MM/YYYY. <br> You can type 'stop' to exit this booking process."
        elif self.state == "rettime":
            rettime, text = extract_time(user_input)
            if rettime:

                if self.retdate != self.date:
                    self.set_rettime(rettime)
                elif rettime > self.time:
                    self.set_rettime(rettime)
                else:
                    return "Your return time can't be earlier than your outgoing journey. Please enter a valid return time in the format HH:MM or HH am / HH pm <br> You can type 'stop' to exit this booking process."
            else:
                return "Please enter your time in the format HH:MM or HH am / HH pm <br> You can type 'stop' to exit this booking process."
        self.set_state("booking")
        response = self.check_extracted()
        return response
    
    def date_check(self):
        date = datetime.datetime.strptime(self.date, "%d-%m-%y")
        current_date = datetime.datetime.now().date()
        if date < datetime.datetime(current_date.year, current_date.month, current_date.day):
            return False
        else:
            return True
    def time_check(self):
        time = datetime.datetime.strptime(self.time, "%H:%M").time()
        # Convert time to datetime object
        current_datetime = datetime.datetime.now()
        current_time = current_datetime.time()

        # Add 2 minutes to time
        new_datetime = datetime.datetime.combine(current_datetime.date(), time) + timedelta(minutes=2)
        new_time = new_datetime.time()

        print(new_time, current_time)

        if new_time < current_time:
            return False
        else:
            return True
    def station_identical_check(self):
        if self.source == self.destination:
            return False
        else:
            return True
        
    def station_ambiguous_check(self, station_input):
        closest_stations = []
        with open('code/station_name_code.json') as f:
            station_names = json.load(f)

        for station in station_names:
            ratio = fuzz.token_set_ratio(station_input, station)  
            if ratio > 80:
                closest_stations.append((station, ratio))

        closest_stations.sort(key=lambda x: x[1], reverse=True)
        print(closest_stations)

        if len(closest_stations) == 1:
            return True
        
        #check if any ratios are higher than 95, if so return true
        for station in closest_stations:
            if station[0] == station_input:
                return True
            
        if len(closest_stations) > 1 and len(closest_stations) <= 3:
            # slice everything apart from the first element
            station_names = [station[0][0] for station in closest_stations[1:]]
            return True


        elif len(closest_stations) > 3:
            station_names = [station[0][0] for station in closest_stations]  # get the station names from the tuples
            station_codes = [station[0][1] for station in closest_stations]  # get the station codes from the tuples
            station_list = "\n".join(f"{i+1}. {name} (Code: {code})" for i, (name, code) in enumerate(zip(station_names, station_codes)))
            return "I found multiple stations, here are the stations I found:<br><br>" + station_list.replace('\n', '<br>') + "<br><br>Please type the exact station name of the required station (no brackets needed).  <br> You can type 'stop' to exit this booking process."
        else:
            return "I couldn't find that station. Please try again. <br> You can type 'stop' to exit this booking process."

    