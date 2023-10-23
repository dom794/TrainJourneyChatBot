"""
rid - Train RTTI Train Identifier
    tpl - Location TIPLOC (station)
    pta - Planned Time of Arrival
    ptd - Planned Time of Departure
    wta - Working (staff) Time of Arrival
    wtp - Working Time of Passing
    wtd - Working Time of Departure
    arr_et - Estimated Arrival Time
    arr_wet - Working Estimated Time
    arr_atRemoved - true if actual replaced by estimated
    pass_et - Estimated Passing Time
    pass_wet - Working Estimated Time
    pass_atRemoved - true if actual replaced by estimated
    dep_et - Estimated Departure
    dep_wet - Working Estimated Time
    dep_atRemoved - true if actual replaced by estimated
    arr_at - Recorded Actual Time of Arrival
    pass_at - Actual Passing Time
    dep_at - Actual Departure Time
    cr_code - Cancellation Reason Code
    lr_code - Late Running Reason

    The following columns will be removed:
    cr_code
    lr_code
    arr_atRemoved
    pass_atRemoved
    dep_atRemoved

    The following columns will be be converted from categorical to numerical:
    rid
    tpl

    The following columns will be used to get the scheduled time:
        pta wta arr_wet scheduled_arrival
        ptd wtd dep_wet scheduled_departure
        wtp pass_wet scheduled_passing
    
    The following columns will be used to get the actual time:
        arr_at arr_et actual_arrival
        dep_at dep_et actual_departure
        pass_at pass_et actual_passing
"""

import copy
import json
import pandas as pd
import os
import warnings
import numpy as np
import datetime
import pickle
import csv
import re

# Ignore the specific warning message
warnings.filterwarnings("ignore", message="DataFrame is highly fragmented.")

random_state = 1

def pre_process(csv_file, filepath, cat_dict):
    print(filepath)
    """
    This will pre-process the data and return a dataframe to be used for training. 
    Removes unnecessary columns.

    Args:
        csv_file: The name of the train data csv file
        filepath: The filepath to csv file
        cat_dict: A dictionary of categorical values and their corresponding numerical values

    Returns:
        A pre-processed dataframe
    """

    # train data file location
    file_location = os.path.join(filepath, csv_file)

    # reads in the csv file and create a dataframe
    df = pd.read_csv(file_location)

    # removes columns that do not contain the necessary information
    df = df.dropna(subset=["arr_at", "arr_et", "dep_at", "dep_et", "pass_at", "pass_et"], how="all")
    df = df.dropna(subset=["pta", "wta", "arr_wet", "ptd", "wtd", "dep_wet", "wtp", "pass_wet"], how="all")


    # removes unnecessary columns
    df = df.drop(
        columns=[
            "cr_code",
            "lr_code",
            "arr_atRemoved",
            "pass_atRemoved",
            "dep_atRemoved",
        ]
    )

    # converts rid to same type as tpl (string)
    df["rid"] = df["rid"].astype(str)

    # converts rid and tpl from categorical to numerical values
    df["rid"] = df["rid"].map(cat_dict)
    df["tpl"] = df["tpl"].map(cat_dict)

    # fixes the format to include :00 for seconds 
    df["pta"] = df["pta"].apply(fix_format)
    df["ptd"] = df["ptd"].apply(fix_format)
    df["wta"] = df["wta"].apply(fix_format)
    df["wtp"] = df["wtp"].apply(fix_format)
    df["wtd"] = df["wtd"].apply(fix_format)
    df["arr_wet"] = df["arr_wet"].apply(fix_format)
    df["pass_wet"] = df["pass_wet"].apply(fix_format)
    df["dep_wet"] = df["dep_wet"].apply(fix_format)
    df["arr_at"] = df["arr_at"].apply(fix_format)
    df["pass_at"] = df["pass_at"].apply(fix_format)
    df["dep_at"] = df["dep_at"].apply(fix_format)
    df["pass_et"] = df["pass_et"].apply(fix_format)
    df["arr_et"] = df["arr_et"].apply(fix_format)
    df["dep_et"] = df["dep_et"].apply(fix_format)


    # fills in missing values with 0
    df["pta"] = df["pta"].fillna("00:00:00")
    df["ptd"] = df["ptd"].fillna("00:00:00")
    df["wta"] = df["wta"].fillna("00:00:00")
    df["wtp"] = df["wtp"].fillna("00:00:00")
    df["wtd"] = df["wtd"].fillna("00:00:00")
    df["arr_wet"] = df["arr_wet"].fillna("00:00:00")
    df["pass_wet"] = df["pass_wet"].fillna("00:00:00")
    df["dep_wet"] = df["dep_wet"].fillna("00:00:00")
    df["arr_at"] = df["arr_at"].fillna("00:00:00")
    df["pass_at"] = df["pass_at"].fillna("00:00:00")
    df["dep_at"] = df["dep_at"].fillna("00:00:00")
    df["pass_et"] = df["pass_et"].fillna("00:00:00")
    df["arr_et"] = df["arr_et"].fillna("00:00:00")
    df["dep_et"] = df["dep_et"].fillna("00:00:00")

    # converts the time columns to datetime format
    df["pta"] = pd.to_datetime(df["pta"], format="%H:%M:%S")
    df["ptd"] = pd.to_datetime(df["ptd"], format="%H:%M:%S")
    df["wta"] = pd.to_datetime(df["wta"], format="%H:%M:%S")
    df["wtp"] = pd.to_datetime(df["wtp"], format="%H:%M:%S")
    df["wtd"] = pd.to_datetime(df["wtd"], format="%H:%M:%S")
    df["arr_wet"] = pd.to_datetime(df["arr_wet"], format="%H:%M:%S")
    df["pass_wet"] = pd.to_datetime(df["pass_wet"], format="%H:%M:%S")
    df["dep_wet"] = pd.to_datetime(df["dep_wet"], format="%H:%M:%S")
    df["arr_at"] = pd.to_datetime(df["arr_at"], format="%H:%M:%S")
    df["pass_at"] = pd.to_datetime(df["pass_at"], format="%H:%M:%S")
    df["dep_at"] = pd.to_datetime(df["dep_at"], format="%H:%M:%S")
    df["pass_et"] = pd.to_datetime(df["pass_et"], format="%H:%M:%S")
    df["arr_et"] = pd.to_datetime(df["arr_et"], format="%H:%M:%S")
    df["dep_et"] = pd.to_datetime(df["dep_et"], format="%H:%M:%S")


    # converts to have only hh:mm:ss
    df["pta"] = df["pta"].dt.time
    df["ptd"] = df["ptd"].dt.time
    df["wta"] = df["wta"].dt.time
    df["wtp"] = df["wtp"].dt.time
    df["wtd"] = df["wtd"].dt.time
    df["arr_wet"] = df["arr_wet"].dt.time
    df["pass_wet"] = df["pass_wet"].dt.time
    df["dep_wet"] = df["dep_wet"].dt.time
    df["arr_at"] = df["arr_at"].dt.time
    df["pass_at"] = df["pass_at"].dt.time
    df["dep_at"] = df["dep_at"].dt.time
    df["pass_et"] = df["pass_et"].dt.time
    df["arr_et"] = df["arr_et"].dt.time
    df["dep_et"] = df["dep_et"].dt.time


    #arr_at arr_et actual_arrival
    #dep_at dep_et actual_departure
    #pass_at pass_et actual_passing


    #pta wta arr_wet scheduled_arrival
    #ptd wtd dep_wet scheduled_departure
    #wtp pass_wet scheduled_passing
    
    #actual
    df['actual_arrival'] = df.apply(lambda row: row['arr_et'] if row['arr_at'] == '00:00:00' else row['arr_at'], axis=1)
    df['actual_departure'] = df.apply(lambda row: row['dep_et'] if row['dep_at'] == '00:00:00' else row['dep_at'], axis=1)
    df['actual_passing'] = df.apply(lambda row: row['pass_et'] if row['pass_at'] == '00:00:00' else row['pass_at'], axis=1)

    #scheduled
    df['scheduled_arrival'] = df.apply(lambda row: row['wta'] if row['pta'] == '00:00:00' else row['pta'], axis=1)
    df['scheduled_arrival'] = df.apply(lambda row: row['arr_wet'] if row['scheduled_arrival'] == '00:00:00' else row['scheduled_arrival'], axis=1)

    df['scheduled_departure'] = df.apply(lambda row: row['wtd'] if row['ptd'] == '00:00:00' else row['ptd'], axis=1)
    df['scheduled_departure'] = df.apply(lambda row: row['dep_wet'] if row['scheduled_departure'] == '00:00:00' else row['scheduled_departure'], axis=1)

    df['scheduled_passing'] = df.apply(lambda row: row['pass_wet'] if row['wtp'] == '00:00:00' else row['wtp'], axis=1)

    # saves the dataframe to a csv file
    save_processed_dataframe(df, csv_file, filepath)

    # returns the dataframe
    return df

def check_format(column):
    """
    This function checks if a column has the correct time format

    Args:
        column: The column we want to check 

    Returns:
        True if the column has the correct time format, false if not
    """

    # changes from hh:mm to hh:mm:ss by adding :00
    pattern = re.compile(r"^\d{2}:\d{2}$")
    pattern2 = re.compile(r"^(\d{2}:\d{2}:\d{2})$")

    # checks if null
    if pd.isna(column):
        return False
    # checks if the column is in the correct format
    elif pattern.match(column) and not pattern2.match(column):
        return True
    else:
        return False


def fix_format(column):
    """
    This function fixes the time format of a column

    Args:
        column: The column to be fixed

    Returns:
        The column with the fixed time format
    """

    if check_format(column):
        return column + ":00"
    else:
        return column


def get_multiple_unique_values(filename, folderpath, categorical_columns):
    """
    This will return the unique values from all the CSV files
    As there may be different stations in different CSV files
    Also the rid values do not match up between CSV files
    """

    # loads the csv file into a dataframe
    df = pd.read_csv(os.path.join(folderpath, filename))

    # creates an empty dictionary storing the unique values with the column name as the key
    unique_values_dict = {}

    # loops through the columns and gets the unique values for each column
    for column in categorical_columns:
        # gets the unique values for the column
        unique_values = df[column].unique()
        # adds the unique values to the dictionary with the column name as the key and the unique values as the value
        unique_values_dict[column] = unique_values

    return unique_values_dict


def convert_to_categorical(unique_values_dict):
    """
    This will convert the categorical columns to numerical values
    """
    cat_dict = {}
    # loops through the categorical columns and convert them to numerical values
    for key, value in unique_values_dict.items():
        cat_dict[key] = dict(zip(value, range(len(value))))

    return cat_dict


def check_dictionary_list(df,  dictionary):
    """
    This function checks the dictionary for each value in the columns and replaces it with the corresponding value if it is found

    Args:
      df: The DataFrame that contains the columns
      columns: The names of the columns to check
      dictionary: The dictionary to use to look up the values in the columns

    Returns:
      A new DataFrame with the replaced values
    """

    # replace the values in the columns with the corresponding values from the dictionary
    newdf = df.replace(dictionary)

    # return the new DataFrame
    return newdf

def get_all_csv_file_names_in_folder(folder_path):
    """
    Gets all CSV file names in a folder

    Args:
        folder_path: The path to the folder to read the names from

    Returns:
        A list of CSV filenames in the folder
    """

    # creates a list to store the file names
    file_names = []

    # loops through the files in the folder and adds the CSV files to the list
    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            file_names.append(file)

    # returns the list of file names
    return file_names


def get_all_folders_in_folder(folder_path, max_depth=6):
    """
    Gets all folders in a folder, including subfolders, up to a specified depth.

    Args:
        folder_path: The path to the folder
        max_depth: The maximum depth to search

    Returns:
        A list of the deepest folder paths
    """

    # creates a list to store the folder names
    folder_names = []

    # loops through the folders in the folder and adds the folder paths to the list
    for root, dirs, files in os.walk(folder_path):
        for dir in dirs:
            folder_names.append(os.path.join(root, dir))

    # returns the list of folder names in the correct format
    return [folder_name.replace("\\", "/") for folder_name in folder_names[-max_depth:]]

def df_categorical():
    """
    This function will return a dictionary of all the unique values in the categorical columns
    """

    categorical_columns = ["rid", "tpl"]
    unique_values_dict = {}
    # reads all the folders from a folder
    folders = get_all_folders_in_folder("data/raw/train_delay_data/CSV")
    for folder in folders:
        # reads all the files from a folder
        files = get_all_csv_file_names_in_folder(folder)
        for file in files:
            dictionary = get_multiple_unique_values(file, folder, categorical_columns)
            # add the new dictionary to the existing dictionary
            for key, values in dictionary.items():
                if key not in unique_values_dict:
                    unique_values_dict[key] = values
                for val in values:
                    if val not in unique_values_dict[key]:
                        unique_values_dict[key] = np.append(unique_values_dict[key], val)

    

    cat_dict = convert_to_categorical(unique_values_dict)

    new_dict = {}
    for key, value in cat_dict.items():
        new_dict = {**new_dict, **value}

    return new_dict, categorical_columns

def save_processed_dataframe(df, filename, folderpath):
    """
    Saves a DataFrame to a CSV file

    Args:
        df: The DataFrame to be saved
        filename: The name of the CSV
        folderpath: The path to the folder to save the CSV to

    """
    # the original unprocessed data 
    og = 'data/raw/train_delay_data/CSV/WATR_WEYM_2017/2017/'
    folder = folderpath.replace('raw', 'processed2')

    
    if not os.path.exists(folder):
        os.makedirs(folder)
    save_path = os.path.join(folder, filename)

    # saves the DataFrame to a CSV file
    df.to_csv(save_path, index=False)


# def main():
#     #


#     # new_dict, categorical_columns = df_categorical()

    

#     # new_dict2 = copy.deepcopy(new_dict)

#     # # create a new dictionary with string keys
#     # new_dict_str = {}

#     # # convert the keys to strings and assign them to the new dictionary
#     # for key, value in new_dict2.items():
#     #     new_key = str(key)
#     #     new_dict_str[new_key] = value

#     #load the dictionary from a json file
#     with open("data/processed2/categorical_dict.json", "r") as f:
#         cat_dict = json.load(f)




#     # # saves the new dictionary to a json file
#     # with open("data/processed/categorical_dict.json", "w") as f:
#     #     json.dump(new_dict_str, f)
#     # #print(files)
#     # #print(cat_dict)

#     # # print(files)

#     # new_dict, categorical_columns = df_categorical()

#     # # creates the dataframe with relevant columns
#     # df = pre_process(
#     #     "WATRLMN_WEYMTH_OD_a51_2017_1_1.csv",
#     #     "data/raw/train_delay_data/CSV/WATR_WEYM_2017/2017/",
#     #     cat_dict
#     # )

#     # print(df.head(20))

#     # # print row 73 VALUES
#     # print(df.iloc[73].tolist())
#     # print(df.iloc[74].tolist())
#     # print(df.iloc[75].tolist())

#     # #df = df.replace(new_dict)
#     # # prints the  first 20 rows of the dataframe
#     # print(df.head(20))

#     # # # print the first row as a list
#     # # print(df.iloc[0].tolist())

#     # # #get the number of rows and columns
#     # # print(df.shape)

#     #do it for all of the csv files
#     folders = get_all_folders_in_folder("data/raw/train_delay_data/CSV")
#     for folder in folders:
#         # reads all the files from a folder
#         files = get_all_csv_file_names_in_folder(folder)
#         for file in files:
#             df = pre_process(file, folder, cat_dict)
#             print(df.head(20))


# if __name__ == "__main__":
#     main()

# # # arrival - patt_at - pass-et
