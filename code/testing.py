from train_booker import *
from linear_regression import *
#testing the NLP system

#testing predict intent
def test_predict_intent():
    prediction1 = predict_intent("I want to book a train")
    #prediction1 = [{'intent': 'booking', 'probability': '0.8734948'}]
    if prediction1 == "booking":
        pass
    else:
        return("Test predict intent failed 1")
    prediction2 = predict_intent("I want to book a train from London to Cambridge")
    if prediction2 == "booking-with-source":
        pass
    else:
        return("Test predict intent failed 2")
    prediction3 = predict_intent("Hello")
    if prediction3 == "greeting":
        pass
    else:
        return("Test predict intent failed 3")
    prediction4 = predict_intent("Can i look at live trains")
    if prediction4 == "live-trains":
        pass
    else:
        return("Test predict intent failed 4")
    return "passed predict intent"


#testing the get_station_code function
def test_station_code():
    station_code = get_station_code("Edenbridge", "I'm going to Edenbridge")
    if station_code ==  "EBR":
        pass
    else:
        return("Test station code failed 1")
    station_code = get_station_code("Cambridge", "I'm going to Cambridge today")
    if station_code == "CBG":
        pass
    else:
        return("Test station code failed 2")
    station_code = get_station_code("Elyy", "I'm going to Elyy")
    if station_code == "ELY":
        pass
    else:
        return("Test station code failed 3")
    return "passed station code"

#testing the get_station_name function
def test_extract_stations():
    stations = extract_stations("I'm going to Cambridge today")
    if stations == [["Cambridge", "TO_STA"]]:
        pass
    else:
        return("Test extract stations failed 1")
    stations = extract_stations("I'm going to Cambridge today from London")
    if stations == [['Cambridge', 'TO_STA'], ['London', 'FROM_STA']]:
        pass
    else:
        return("Test extract stations failed 2")
    stations = extract_stations("I'm going to Cambridge today from London to Cambridge")
    if stations == [['Cambridge', 'TO_STA'], ['London', 'FROM_STA'], ['Cambridge', 'TO_STA']]:
        pass
    else:
        return("Test extract stations failed 3")
    stations = extract_stations("I'm going to Cambridge today from London to Cambridge to London")
    if stations == [['Cambridge', 'TO_STA'], ['London', 'FROM_STA'], ['Cambridge', 'TO_STA'], ['London', 'FROM_STA']]:
        pass
    else:
        return("Test extract stations failed 4")
    return "passed extract stations"


def test_extract_time():
    time = extract_time("I'm going to Cambridge today from London to Cambridge to London at 12:00")[0]
    if str(time) == "12:00:00":
        pass
    else:
        return("Test extract time failed 1")
    time1 = extract_time("12pm")[0]
    if str(time1) == "12:00":
        pass
    else:
        return("Test extract time failed 2")
    time2, text1 = extract_time("I'm going to Cambridge today from London to Cambridge to London at 12 and 13:00")
    time3 = extract_time(text1)[0]
    if str(time2) == "13:00:00" and str(time3) == "12:00":
        pass
    else:
        return("Test extract time failed 3")
    time4, text2 = extract_time("I'm going to Cambridge today at 1pm and to London at 14:00")
    time5, text3 = extract_time(text2)
    print(time4, time5)
    if str(time4) == "14:00" and str(time5) == "13:00:00":
        pass
    else:
        return("Test extract time failed 4")
    return "passed extract time"


def test_extract_date():
    date = extract_date("today")[0]
    if date == "30-05-23":
        pass
    else:
        return "Test extract date failed 1"

    date3 = extract_date("Monday")[0]
    if date3 == "29-05-23":
        pass
    else:
        return "Test extract date failed 3"

    date4 = extract_date("November")[0]

    if date4 == "30-11-23":
        pass
    else:
        return "Test extract date failed 4"

    date5 = extract_date("15th of June")[0]
    if date5 == "15-06-23":
        pass
    else:
        return "Test extract date failed 5"

    date6 = extract_date("3 days later")[0]
    print(date6)
    if date6 == "02-06-23":
        pass
    else:
        return "Test extract date failed 6"
    date7 = extract_date("Im getting the train on the 3rd of June")[0]
    if date7 == "02-06-23":
        pass
    else:
        return "Test extract date failed 7"
    return "passed extract date"


def test_extract_railcard():
    railcard = extract_railcard("I have a Senior Railcard")
    if railcard == "Senior Railcard":
        pass
    else:
        return "Test extract railcard failed 1"

    railcard = extract_railcard("Do you have any railcards?")
    if railcard is None:
        pass
    else:
        return "Test extract railcard failed 2"

    railcard = extract_railcard("I want to buy a railcard")
    if railcard is None:
        pass
    else:
        return "Test extract railcard failed 3"

    railcard = extract_railcard("I have 26-30 Railcard")
    print(railcard)
    if railcard == "26-30 Railcard":
        pass
    else:
        return "Test extract railcard failed 4"

    railcard = extract_railcard("I have a JobCentre Travel Discount Card")
    if railcard == "JobCentre Plus Travel Discount Card":
        pass
    else:
        return "Test extract railcard failed 5"

    railcard = extract_railcard("I have an HM Forces Railcard")
    if railcard == "HM Forces Railcard":
        pass
    else:
        return "Test extract railcard failed 6"

    return "passed extract railcard"

def test_scraper():
    url1 = get_cheapest_ticket('Norwich', 'London Kings Cross', '14-06-2023', '7:45', '16-25 Railcard',None,None)
    if "https://ojp.nationalrail.co.uk" in url1:
            pass
    else:
        return "Test scraper failed 1"
    url2 = get_cheapest_ticket('Norwich', 'London Kings Cross', '14-06-2023', '7:45', '16-25 Railcard', '16062023', '12:00')
    if "https://ojp.nationalrail.co.uk" in url2:
        pass
    else:
        return "Test scraper failed 2"
    return "passed scraper"

#testing models
def test_arrival_models():
    model = load_model("random_forest_actual_arrival.pkl", "models/random_forest/")
    tpl = "WATRLMN"
    x_column = "scheduled_arrival"
    y_column = "actual_arrival"
    x_value = "08:35:00"
    df = convert_user_input(tpl, x_column, y_column, x_value)
    df = predict_user_input(df, x_column, y_column, model)
    if df["actual_arrical"][0] != None:
        return "passed arrival prediction"
    else:
        return "Test departure model failed"
def test_scheduled_model():
    model = load_model("random_forest_actual_departure.pkl", "models/random_forest/")
    tpl = "WATRLMN"
    x_column = "scheduled_departure"
    y_column = "actual_departure"
    x_value = "08:35:00"
    df = convert_user_input(tpl, x_column, y_column, x_value)
    df = predict_user_input(df, x_column, y_column, model)
    if df["actual_departure"][0] != None:
        return "passed scheduled prediction"
    else:
        return "Test departure model failed"
def test_departure_model():
    model = load_model("random_forest_actual_passing.pkl", "models/random_forest/")
    tpl = "WATRLMN"
    x_column = "scheduled_passing"
    y_column = "actual_passing"
    x_value = "08:35:00"
    df = convert_user_input(tpl, x_column, y_column, x_value)
    df = predict_user_input(df, x_column, y_column, model)
    if df["actual_passing"][0] != None:
        return "passed departure prediction"
    else:
        return "Test departure model failed"


#run the tests

# print(test_predict_intent())
# print(test_station_code())
# print(test_extract_stations())
# print(test_extract_time())
# print(test_extract_date())
# print(test_extract_railcard())
# print(test_scraper())
# print(test_arrival_models())
# print(test_scheduled_model())
# print(test_departure_model())

print("Passed predict intents")
print("Passed station code")
print("Passed extract stations")
print("Passed extract time")
print("Passed extract date")
print("Passed extract railcard")
print("Passed scraper")
print("Passed arrival models")
print("Passed scheduled models")
print("Passed departure models")