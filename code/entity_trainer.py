from tqdm import tqdm
from pathlib import Path
import json
import spacy
import random
from spacy.training import Example
from spacy.pipeline import EntityRecognizer

# Load the JSON file
train_data = [
    ("Can I get a ticket for a train leaving Birmingham New Street and arriving at Glasgow Central on May 2nd at 13:45?", {
        "entities": [
            (28, 50, "FROM_STA"),
            (64, 80, "TO_STA"),
            (85, 92, "DATE"),
            (96, 101, "TIME")
        ]
    }),
    ("What's the price of a ticket from Birmingham New Street to Manchester Piccadilly on May 3rd at 1:15 PM?", {
        "entities": [
            (28, 48, "FROM_STA"),
            (52, 72, "TO_STA"),
            (76, 83, "DATE"),
            (87, 92, "TIME")
        ]
    }),
    ("Can I get a ticket for a train leaving Birmingham New Street and arriving at Glasgow Central on May 2nd at 13:45?", {
        "entities": [
            (28, 50, "FROM_STA"),
            (64, 80, "TO_STA"),
            (85, 92, "DATE"),
            (96, 101, "TIME")
        ]
    }),
    ("I need to travel from Newcastle to Manchester Piccadilly on the 17th of June at 11:30. How much does it cost?", {
        "entities": [
            (22, 30, "FROM_STA"),
            (34, 53, "TO_STA"),
            (58, 69, "DATE"),
            (73, 78, "TIME")
        ]
    }),
    ("What's the fare for a train from Leeds to London St Pancras on the 25th of July at 09:15?", {
        "entities": [
            (32, 37, "FROM_STA"),
            (41, 60, "TO_STA"),
            (65, 76, "DATE"),
            (80, 85, "TIME")
        ]
    }),
    ("What's the price of a ticket from Birmingham New Street to Manchester Piccadilly on May 3rd at 1:15 PM?", {
        "entities": [
            (28, 48, "FROM_STA"),
            (52, 72, "TO_STA"),
            (76, 83, "DATE"),
            (87, 92, "TIME")
        ]
    }),
    ("On the 17th of June at 11:30",
     {
         "entities": [
             (7, 18, "DATE"),
             (23, 27, "TIME")
         ]
     }),
    ("21st February at 12:00",
     {
         "entities": [
             (0, 12, "DATE"),
             (17, 21, "TIME")
         ]
     }),
    ("I'd like a ticket for a train leaving Manchester Piccadilly on July 18th at 15:30, arriving at London Euston. Can I use my Senior Railcard?",
     {
         "entities": [
            (39, 59, "FROM_STA"),
            (96, 108, "TO_STA"),
            (64, 72, "DATE"),
            (77, 81, "TIME"), 
            (124, 138, "DISCOUNT")
         ]
     }),
    ("Can I get a ticket for a train to Bristol Temple Meads from Edinburgh Waverley on June 5th at 11:45? I have a Family & Friends Railcard.",###
     {
         "entities": [
            (61, 78, "FROM_STA"), 
            (35, 54, "TO_STA"), 
            (83, 90, "DATE"), 
            (95, 99, "TIME"), 
            (111, 135, "DISCOUNT")
         ]
    }),
    ("I'm looking for a train to Liverpool Lime Street from Nottingham on August 14th at 9:15. Do you accept the 26-30 Railcard?",###
     {
         "entities": [
            (55, 64, "FROM_STA"), 
            (28, 48, "TO_STA"), 
            (69, 79, "DATE"), 
            (84, 87, "TIME"), 
            (108, 121, "DISCOUNT")
         ]
    }),
    ("Can you help me find a train leaving Leeds at 12:30 on September 7th, arriving at York? I have a Disabled Persons Railcard.",
     {
         "entities": [
            (38, 42, "FROM_STA"), 
            (83, 86, "TO_STA"), 
            (47, 51, "TIME"), 
            (56, 68, "DATE"), 
            (98, 122, "DISCOUNT")
         ]
    }),
    ("I need a ticket for a train to London Waterloo from Brighton on October 2nd at 8:00. Can I use my Two Together Railcard?",###
     {
             "entities": [
            (53, 60, "FROM_STA"), 
            (32, 46, "TO_STA"), 
            (65, 75, "DATE"), 
            (80, 83, "TIME"), 
            (99, 119, "DISCOUNT")
         ]
    }),
    ("Is there a train from Newcastle to Leeds on November 10th at 16:20? I have a 16-25 Railcard.",
     {
         "entities": [
            (23, 31, "FROM_STA"), 
            (36, 40, "TO_STA"), 
            (45, 57, "DATE"), 
            (62, 66, "TIME"), 
            (78, 91, "DISCOUNT")
         ]
    }),
    ("Can you tell me if there's a train to Birmingham New Street from Manchester Piccadilly on December 1st at 11:00? I have a Network Railcard.",###
     {
         "entities": [
            (66, 86, "FROM_STA"), 
            (39, 59, "TO_STA"), 
            (91, 102, "DATE"), 
            (107, 111, "TIME"), 
            (123, 138, "DISCOUNT")
         ]
    }),
    ("I'd like to book a train from Glasgow Queen Street to Inverness on January 5th at 13:15. Will my Veterans Railcard be valid?",
     {
         "entities": [
            (31, 50, "FROM_STA"), 
            (55, 63, "TO_STA"), 
            (68, 78, "DATE"), 
            (83, 87, "TIME"), 
            (98, 114, "DISCOUNT")
         ]
    }),
    ("Is there a train to Coventry from London Euston on June 15th at 9:30? I have a 26-30 Railcard.",###
         {"entities": [
            (35, 47, "FROM_STA"),
            (21, 28, "TO_STA"),
            (52, 60, "DATE"),
            (65, 68, "TIME"),
            (80, 93, "DISCOUNT")
         ]
    }),
    ("Can you tell me if there's a train from Brighton to Southampton Central on August 8th at 14:15? I have a Disabled Persons Railcard.",
         {"entities": [
            (41, 48, "FROM_STA"),
            (53, 71, "TO_STA"),
            (76, 85, "DATE"),
            (90, 94, "TIME"),
            (106, 130, "DISCOUNT")
         ]
    }),
    ("I'd like to book a train to Oxford from Manchester Piccadilly on October 2nd at 12:00. Will my Two Together Railcard be valid?",###
         {"entities": [
            (41, 61, "FROM_STA"),
            (29, 34, "TO_STA"),
            (66, 76, "DATE"),
            (81, 85, "TIME"),
            (96, 116, "DISCOUNT")
         ]
    }),
    ("Is there a train from Edinburgh Waverley to Birmingham New Street on December 20th at 16:45? I have a 16-25 Railcard.",
         {"entities": [
            (23, 40, "FROM_STA"),
            (45, 65, "TO_STA"),
            (70, 82, "DATE"),
            (87, 91, "TIME"),
            (103, 116, "DISCOUNT")
         ]
    }),
    ("Can you tell me if there's a train to Plymouth from Bristol Temple Meads on September 10th at 11:30? I have a Family & Friends Railcard.",###
         {"entities": [
            (53, 72, "FROM_STA"),
            (39, 46, "TO_STA"),
            (77, 90, "DATE"),
            (95, 99, "TIME"),
            (111, 135, "DISCOUNT")
         ]
    }),
    ("I'd like to book a train from Liverpool Lime Street to Newcastle on May 1st at 15:00. Will my Senior Railcard be valid?",
         {"entities": [
            (31, 51, "FROM_STA"),
            (56, 64, "TO_STA"),
            (69, 75, "DATE"),
            (80, 84, "TIME"),
            (95, 109, "DISCOUNT")
         ]
    }),
    ("Is there a train to York from London Kings Cross on July 5th at 10:15? I have a 16-17 Saver.",###
         {"entities": [
            (31, 48, "FROM_STA"),
            (21, 24, "TO_STA"),
            (53, 60, "DATE"),
            (65, 69, "TIME"),
            (81, 91, "DISCOUNT")
         ]
    }),
    ("Can you tell me if there's a train from Bristol Parkway to Manchester Oxford Road on October 28th at 13:30? I have a Network Railcard.",
         {"entities": [
            (41, 55, "FROM_STA"),
            (60, 81, "TO_STA"),
            (86, 97, "DATE"),
            (102, 106, "TIME"),
            (118, 133, "DISCOUNT")
         ]
    }),
    ("I'd like to book a train from Aberdeen to Inverness on November 15th at 16:00. Will my 26-30 Railcard be valid?",
         {"entities": [
            (31, 38, "FROM_STA"),
            (43, 51, "TO_STA"),
            (56, 68, "DATE"),
            (73, 77, "TIME"),
            (88, 101, "DISCOUNT")
         ]
    }),
    ("Is there a train to Cambridge from Nottingham on January 20th at 9:45? I have a Senior Railcard.",###
         {"entities": [
            (33, 45, "FROM_STA"),
            (21, 29, "TO_STA"),
            (50, 61, "DATE"),
            (66, 69, "TIME"),
            (81, 95, "DISCOUNT")
         ]
    }),
("Can you tell me if there's a train from London Victoria to Canterbury West on September 5th at 11:15? I have a 16-25 Railcard.",
         {"entities": [
            (41, 55, "FROM_STA"),
            (60, 74, "TO_STA"),
            (79, 91, "DATE"),
            (96, 100, "TIME"),
            (112, 125, "DISCOUNT")
         ]
    }),
("I'd like to book a train to Southampton Central from Brighton on February 18th at 14:20. Will my Disabled Persons Railcard be valid?",###
         {"entities": [
            (54, 61, "FROM_STA"),
            (29, 47, "TO_STA"),
            (66, 78, "DATE"),
            (83, 87, "TIME"),
            (98, 122, "DISCOUNT")
         ]
    }),
("Is there a train from Glasgow Central to Edinburgh Waverley on April 2nd at 12:30? I have a Family & Friends Railcard.",
         {"entities": [
            (23, 37, "FROM_STA"),
            (42, 59, "TO_STA"),
            (64, 72, "DATE"),
            (77, 81, "TIME"),
            (93, 117, "DISCOUNT")
         ]
    }),
("Can you tell me if there's a train to Manchester Piccadilly from Bristol Temple Meads on August 12th at 10:00? I have a Two Together Railcard.",###
         {"entities": [
            (66, 85, "FROM_STA"),
            (39, 59, "TO_STA"),
            (90, 100, "DATE"),
            (105, 109, "TIME"),
            (121, 141, "DISCOUNT")
         ]
    }),
("I'd like to book a train from Birmingham New Street to Plymouth on March 25th at 15:45. Will my Veterans Railcard be valid?",
         {"entities": [
            (31, 51, "FROM_STA"),
            (56, 63, "TO_STA"),
            (68, 77, "DATE"),
            (82, 86, "TIME"),
            (97, 122, "DISCOUNT")
         ]
    }),
("Is there a train to Newcastle from York on May 30th at 17:00? I have a 26-30 Railcard.",###
         {"entities": [
            (36, 39, "FROM_STA"),
            (21, 29, "TO_STA"),
            (44,51, "DATE"),
            (56, 60, "TIME"),
            (72, 85, "DISCOUNT")
         ]
    }),
("Can you tell me if there's a train from London Euston to Liverpool Lime Street on June 14th at 13:15? I have a 16-17 Saver.",
         {"entities": [
            (41, 53, "FROM_STA"),
            (58, 78, "TO_STA"),
            (83, 91, "DATE"),
            (96, 100, "TIME"),
            (112, 122, "DISCOUNT")
         ]
    }),
("I'd like to book a train to Bristol Temple Meads from Bath Spa on July 7th at 9:00. Will my Family & Friends Railcard be valid?",###
         {"entities": [
            (55, 62, "FROM_STA"),
            (29, 48, "TO_STA"),
            (67, 74, "DATE"),
            (79, 82, "TIME"),
            (93, 117, "DISCOUNT")
         ]
    }),
("Is there a train from Edinburgh Waverley to Glasgow Queen Street on August 20th at 16:30? I have a Senior Railcard.",
         {"entities": [
            (23, 40, "FROM_STA"),
            (45, 64, "TO_STA"),
            (69, 79, "DATE"),
            (84, 88, "TIME"),
            (100, 114, "DISCOUNT")
         ]
    }),
("Can you tell me if there's a train to Nottingham from Leicester on September 3rd at 14:00? I have a Disabled Persons Railcard.",###
         {"entities": [
            (55, 63, "FROM_STA"),
            (39, 48, "TO_STA"),
            (68, 80, "DATE"),
            (85, 89, "TIME"),
            (101, 125, "DISCOUNT")
         ]
    })
]

""" nlp = spacy.blank('en')
print("Created blank 'en' model")

# set up the pipeline
ner = nlp.add_pipe('ner')

# get labels
for _, annotations in train_data:
    for ent in annotations.get('entities'):
        print("entity = ", ent)
        ner.add_label(ent[2])

# train the model
optimizer = nlp.begin_training()
for i in range(5000):
    random.shuffle(train_data)
    losses = {}
    for text, annotations in tqdm(train_data):
        example = Example.from_dict(nlp.make_doc(text), annotations)
        nlp.update(
            [example],
            drop=0.5,
            sgd=optimizer,
            losses=losses)

# Save trained model
nlp.to_disk(Path("new_new_test_model"))
print("Saved model to new_new_test_model") """