#this converts the list of stations to the correct format for spacy NER
import json

def convert_to_spacy_pattern(data):
    patterns = []
    for station in data:
        pattern = {"label": "STATION", "pattern": [{"LOWER": word.lower()} for word in station[0].split()], "id": station[1]}
        patterns.append(pattern)
    return patterns



def main():
    # Read the data from file
    with open("station_name_code.json", "r") as f:
        data = json.load(f)

    # Convert the data to Spacy pattern format
    patterns = convert_to_spacy_pattern(data)
    
    with open("slots.json", "w") as f:
        json.dump(patterns, f)

if __name__ == "__main__":
    main()