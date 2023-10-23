import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import accuracy_score
import numpy as np
from preprocessing import *

def create_df_all():
    """
    Will loop through all of the csv files and create a dataframe with all of the data
    """
    # creates a blank df
    df = pd.DataFrame()

    # gets all of the folders in the folder with the unprocessed data
    folders = get_all_folders_in_folder("data/processed/train_delay_data/CSV")
    for folder in folders:
        # reads all the files from a folder
        files = get_all_csv_file_names_in_folder(folder)
        for file in files:
            file_path = os.path.join(folder, file)
            # loads the csv file into a dataframe
            df_temp = pd.read_csv(file_path)
            # appends the dataframe to the main dataframe
            df = df.append(df_temp, ignore_index=True)
    
    # saves the dataframe to a csv file
    # df.to_csv("data/processed2/all_data.csv", index=False)
    return df

def create_linear_regression(all_data_filepath, y_column, X_columns_to_remove, x_column_test): 
    """
    This will create a linear regression model using the sklearn library

    Args:
        df: A dataframe of the preprocessed data

    Returns:
        A linear regression model
    """

    # reads in the csv file and creates a dataframe
    df = pd.read_csv(all_data_filepath)

    # drops the columns that have 00:00:00 as the value for the independent variable
    df = df[df[f"{y_column}"] != '00:00:00']

    # converts the time columns to datetime
    df[f"{x_column_test}"] = pd.to_datetime(df[f"{x_column_test}"], format="%H:%M:%S")
    df[f"{y_column}"] = pd.to_datetime(df[f"{y_column}"], format="%H:%M:%S")

    # converts the datetime to time
    df[f"{x_column_test}"] = df[f"{x_column_test}"].dt.time
    df[f"{y_column}"] = df[f"{y_column}"].dt.time


    # converts dt.time to seconds
    df[f"{x_column_test}"] = df[f"{x_column_test}"].apply(lambda x: x.hour + x.minute/60)
    df[f"{y_column}"] = df[f"{y_column}"].apply(lambda x: x.hour + x.minute/60)

    # # print the first row as a list
    # print(df.iloc[0].tolist())
    # print(df.iloc[1].tolist())

    # creates the model
    model = LinearRegression()

    # list of columns that are always removed
    columns_to_remove = ["rid", "pta", "ptd", "wta", "wtp", "wtd", "arr_et", "arr_wet", "pass_et", "pass_wet", "dep_et", "dep_wet", "arr_at", "pass_at", "dep_at"]

    # adds the x_columns_to_remove to the columns_to_remove list
    columns_to_remove.extend(X_columns_to_remove)
    # adds the y_column to the columns_to_remove list
    columns_to_remove.append(y_column)

    # print(columns_to_remove)

    # creates the x and y values for the model
    # actual_arrival,actual_departure,actual_passing,scheduled_arrival,scheduled_departure,scheduled_passing
    X = df.drop(columns=columns_to_remove)
    y = df[f"{y_column}"]

    # print(X)
    # print(y)

    # splits into train and validation sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # # saves the X_train and y_train to a csv file
    # X_train.to_csv("data/processed2/X_train.csv", index=False)
    # y_train.to_csv("data/processed2/y_train.csv", index=False)

    # # saves the X_test and y_test to a csv file
    # X_test.to_csv("data/processed2/X_test.csv", index=False)
    # y_test.to_csv("data/processed2/y_test.csv", index=False)



    # fits the model
    model.fit(X_train, y_train)

    # returns the model, X_test, and y_test
    return model, X_test, y_test

def create_knn(all_data_filepath, y_column, X_columns_to_remove, x_column_test):
    """
    This will create a KNN model using the sklearn library

    Args:
        df: A dataframe of the preprocessed data

    Returns:
        A KNN model
    """

    # reads in the csv file and create a dataframe
    df = pd.read_csv(all_data_filepath)

    # drops the columns that have 00:00:00 as the value for the independent variable
    df = df[df[f"{y_column}"] != '00:00:00']

    # converts the time columns to datetime
    df[f"{x_column_test}"] = pd.to_datetime(df[f"{x_column_test}"], format="%H:%M:%S")
    df[f"{y_column}"] = pd.to_datetime(df[f"{y_column}"], format="%H:%M:%S")

    # converts the datetime to time
    df[f"{x_column_test}"] = df[f"{x_column_test}"].dt.time
    df[f"{y_column}"] = df[f"{y_column}"].dt.time

    # converts dt.time to seconds
    df[f"{x_column_test}"] = df[f"{x_column_test}"].apply(lambda x: x.hour + x.minute/60)
    df[f"{y_column}"] = df[f"{y_column}"].apply(lambda x: x.hour + x.minute/60)

    # # prints the first row as a list
    # print(df.iloc[0].tolist())
    # print(df.iloc[1].tolist())

    # creates the model
    model = KNeighborsRegressor(n_neighbors=5)

    # list of columns that are always removed
    columns_to_remove = ["rid", "pta", "ptd", "wta", "wtp", "wtd", "arr_et", "arr_wet", "pass_et", "pass_wet", "dep_et", "dep_wet", "arr_at", "pass_at", "dep_at"]

    # adds the x_columns_to_remove to the columns_to_remove list
    columns_to_remove.extend(X_columns_to_remove)
    # adds the y_column to the columns_to_remove list
    columns_to_remove.append(y_column)
    print(columns_to_remove)

    # creates the x and y values for the model
    # actual_arrival,actual_departure,actual_passing,scheduled_arrival,scheduled_departure,scheduled_passing
    X = df.drop(columns=columns_to_remove)
    y = df[f"{y_column}"]

    # print(X)
    # print(y)

    # split into train and validation sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # fits the model
    model.fit(X_train, y_train)

    return model, X_test, y_test

def create_random_forest(all_data_filepath, y_column, X_columns_to_remove, x_column_test):
    """
    This will create a model using random forest regression

    Args:
        df: A dataframe of the preprocessed data

    Returns:
        A random forest model
    """

    # reads in the csv file and create a dataframe
    df = pd.read_csv(all_data_filepath)

    # drops the columns that have 00:00:00 as the value for the independent variable
    df = df[df[f"{y_column}"] != '00:00:00']

    # converts the time columns to datetime
    df[f"{x_column_test}"] = pd.to_datetime(df[f"{x_column_test}"], format="%H:%M:%S")
    df[f"{y_column}"] = pd.to_datetime(df[f"{y_column}"], format="%H:%M:%S")

    # converts the datetime to time
    df[f"{x_column_test}"] = df[f"{x_column_test}"].dt.time
    df[f"{y_column}"] = df[f"{y_column}"].dt.time

    # converts dt.time to seconds
    df[f"{x_column_test}"] = df[f"{x_column_test}"].apply(lambda x: x.hour + x.minute/60)
    df[f"{y_column}"] = df[f"{y_column}"].apply(lambda x: x.hour + x.minute/60)

    # # print the first row as a list
    # print(df.iloc[0].tolist())
    # print(df.iloc[1].tolist())

    # creates the model
    model = RandomForestRegressor(n_estimators=100)

    # list of columns that are always removed
    columns_to_remove = ["rid", "pta", "ptd", "wta", "wtp", "wtd", "arr_et", "arr_wet", "pass_et", "pass_wet", "dep_et", "dep_wet", "arr_at", "pass_at", "dep_at"]

    # adds the x_columns_to_remove to the columns_to_remove list
    columns_to_remove.extend(X_columns_to_remove)
    # adds the y_column to the columns_to_remove list
    columns_to_remove.append(y_column)
    print(columns_to_remove)

    # creates the x and y values for the model
    # actual_arrival,actual_departure,actual_passing,scheduled_arrival,scheduled_departure,scheduled_passing
    X = df.drop(columns=columns_to_remove)
    y = df[f"{y_column}"]

    # print(X)
    # print(y)

    # split into train and validation sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # fits the model
    model.fit(X_train, y_train)

    return model, X_test, y_test

def save_model(model, filename, folderpath):
    """
    This will save a model to a pickle file

    Args:
        model: The model to save.
        filename: The name of the file to save the model to.
        folderpath: The path to the folder where the file should be saved.
    """

    # creates the path to the file
    filepath = os.path.join(folderpath, filename)

    # creates the folder if it doesn't exist
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)

    # saves the model to the file
    with open(filepath, "wb") as f:
        pickle.dump(model, f)

def load_model(filename, folderpath):
    """
    This will load a model from a file.

    Args:
        filename: The name of the file to load the model from
        folderpath: The path to the folder where the file is located

    Returns:
        A trained model
    """

    # creates the path to the file
    filepath = os.path.join(folderpath, filename)
    # checks if the file exists
    if not os.path.exists(filepath):
        print("The file does not exist")

    # loads the model from the file
    with open(filepath, "rb") as f:
        model = pickle.load(f)

    return model

def predict(model, X_test, y_test, predicting, model_name):
    """
    This function will predict the actual arrival time of a train
    """
    filepath = "output/results/"

    # checks the folder exists and if not then create it
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    # predict the actual time of a certain action (arrival, departure, passing)
    predicted_arrival_time = model.predict(X_test)

    # evaluates the model on the test set
    score = model.score(X_test, y_test)

    # saves this score to a csv file at the filepath
    with open("model_scores.csv", "a") as f:
        # checks if there is a header in the file already and if not then add one
        if os.stat("model_scores.csv").st_size == 0:
            f.write("model,score\n")
        f.write(f"{model_name}, {predicting}, {score}\n")

    # returns the predicted delay and the model score
    return predicted_arrival_time, score

def convert_seconds_to_hh_mm_ss(seconds):
    """
    Converts the seconds to hh:mm:ss

    Args:
        seconds: The number of seconds to convert

    Returns:
        The formatted time
    """

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    seconds = round(seconds)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def convert_user_input(tpl, x_column, y_column, x_value):
    """
    Converts the user input to a format that can be used by the model

    Args:
        tpl: The tpl of the station
        scheduled_time: The scheduled time of the train

    Returns:
        The formatted time
    """

    #load the dictionary from a json file
    with open("data/processed/categorical_dict.json", "r") as f:
        cat_dict = json.load(f)

    # creates a dataframe with two blank rows

    df = pd.DataFrame()
    # fill in the first two rows of the dataframe 
    df["tpl"] = [tpl] 
    df[f"{x_column}"] = [x_value] 
    df[f"{y_column}"] = ["00:00:00"] 

    # converts the time columns to datetime
    df[f"{x_column}"] = pd.to_datetime(df[f"{x_column}"], format="%H:%M:%S")
    df[f"{y_column}"] = pd.to_datetime(df[f"{y_column}"], format="%H:%M:%S")

    # converts the datetime to time
    df[f"{x_column}"] = df[f"{x_column}"].dt.time
    df[f"{y_column}"] = df[f"{y_column}"].dt.time

    # converts dt.time to seconds
    df[f"{x_column}"] = df[f"{x_column}"].apply(lambda x: x.hour + x.minute/60)
    df[f"{y_column}"] = df[f"{y_column}"].apply(lambda x: x.hour + x.minute/60)


    df["tpl"] = df["tpl"].map(cat_dict)

    return df



def predict_user_input(df, x_column, y_column, model):
    """
    Predicts the actual time of the train
    """
    X = df.drop(columns=[f"{y_column}"])

    # predict the actual time of a certain action (arrival, departure, passing)
    predicted_time = model.predict(X)

    #add the predicted time to the dataframe in the 
    df[f"{y_column}"] = predicted_time

    # convert the hours to seconds
    df[f"{y_column}"] = df[f"{y_column}"].apply(lambda x: x * 3600)

    # round the seconds to the nearest second
    df[f"{y_column}"] = df[f"{y_column}"].apply(lambda x: round(x))

    # convert the seconds to hh:mm:ss
    df[f"{y_column}"] = df[f"{y_column}"].apply(lambda x: convert_seconds_to_hh_mm_ss(x))

    # returns the predicted delay and the model score
    return df


def main():

    # # for "actual_arrival" drop "actual_departure", "actual_passing", "scheduled_departure", "scheduled_passing"
    # # for "actual_departure" drop "actual_arrival", "actual_passing", "scheduled_arrival", "scheduled_passing"
    # # for "actual_passing" drop "actual_arrival", "actual_departure", "scheduled_arrival", "scheduled_departure"
    # y_columns = ["actual_arrival", "actual_departure", "actual_passing"]
    # x_column_test = ["scheduled_arrival", "scheduled_departure", "scheduled_passing"]
    # X_columns_remove_list = [["actual_departure", "actual_passing", "scheduled_departure", "scheduled_passing"],
    #              ["actual_arrival", "actual_passing", "scheduled_arrival", "scheduled_passing"],
    #              ["actual_arrival", "actual_departure", "scheduled_arrival", "scheduled_departure"]] 
    

    # # linear regression
    # for i in range(len(y_columns)):
    #     # creates the dataframe with relevant columns
    #     model, X_test, y_test  = create_linear_regression(
    #         "data/processed2/all_data.csv",
    #         y_columns[i],
    #         X_columns_remove_list[i],
    #         x_column_test[i]
    #     )

    #     # saves the model
    #     save_model(model, f"linear_regression_{y_columns[i]}.pkl", "data/output/models/linear_regression/")
    
    #     # predict the predicted time
    #     predicted_arrival_time, score = predict(model, X_test, y_test, y_columns[i], "linear_regression")

    #     # print the score
    #     print(f"Score: {score} for {y_columns[i]}")

    #     # put predicted time into a dataframe
    #     df = pd.DataFrame(predicted_arrival_time, columns=[f"predicted_{y_columns[i]}"])

    #     # convert the hours to seconds
    #     df[f"predicted_{y_columns[i]}"] = df[f"predicted_{y_columns[i]}"].apply(lambda x: x * 3600)

    #     # round the seconds to the nearest second
    #     df[f"predicted_{y_columns[i]}"] = df[f"predicted_{y_columns[i]}"].apply(lambda x: round(x))

    #     # convert the seconds to hh:mm:ss
    #     df[f"predicted_{y_columns[i]}"] = df[f"predicted_{y_columns[i]}"].apply(lambda x: convert_seconds_to_hh_mm_ss(x))

    #     # print the dataframe
    #     print(df)

    
    # # random forest
    # for i in range(len(y_columns)):
    #     # creates the dataframe with relevant columns
    #     model, X_test, y_test  = create_random_forest(
    #         "data/processed2/all_data.csv",
    #         y_columns[i],
    #         X_columns_remove_list[i],
    #         x_column_test[i]
    #     )

    #     # saves the model
    #     save_model(model, f"random_forest_{y_columns[i]}.pkl", "data/output/models/random_forest/")
    
    #     # predicts the predicted time 
    #     predicted_arrival_time, score = predict(model, X_test, y_test, y_columns[i], "random_forest")

    #     # print the score
    #     print(f"Score: {score} for {y_columns[i]}")

    #     # put predicted time into a dataframe
    #     df = pd.DataFrame(predicted_arrival_time, columns=[f"predicted_{y_columns[i]}"])

    #     # convert the hours to seconds
    #     df[f"predicted_{y_columns[i]}"] = df[f"predicted_{y_columns[i]}"].apply(lambda x: x * 3600)

    #     # round the seconds to the nearest second
    #     df[f"predicted_{y_columns[i]}"] = df[f"predicted_{y_columns[i]}"].apply(lambda x: round(x))

    #     # convert the seconds to hh:mm:ss
    #     df[f"predicted_{y_columns[i]}"] = df[f"predicted_{y_columns[i]}"].apply(lambda x: convert_seconds_to_hh_mm_ss(x))

    #     # print the dataframe
    #     print(df)

    # # knn
    # for i in range(len(y_columns)):
    #     # creates the dataframe with relevant columns
    #     model, X_test, y_test  = create_knn(
    #         "data/processed2/all_data.csv",
    #         y_columns[i],
    #         X_columns_remove_list[i],
    #         x_column_test[i]
    #     )

    #     # saves the model
    #     save_model(model, f"knn_{y_columns[i]}.pkl", "data/output/models/knn/")
    
    #     # predicts the predicted time
    #     predicted_arrival_time, score = predict(model, X_test, y_test, y_columns[i], "knn")

    #     # prints the score
    #     print(f"Score: {score} for {y_columns[i]}")

    #     # put predicted time into a dataframe
    #     df = pd.DataFrame(predicted_arrival_time, columns=[f"predicted_{y_columns[i]}"])

    #     # convert the hours to seconds
    #     df[f"predicted_{y_columns[i]}"] = df[f"predicted_{y_columns[i]}"].apply(lambda x: x * 3600)

    #     # round the seconds to the nearest second
    #     df[f"predicted_{y_columns[i]}"] = df[f"predicted_{y_columns[i]}"].apply(lambda x: round(x))

    #     # convert the seconds to hh:mm:ss
    #     df[f"predicted_{y_columns[i]}"] = df[f"predicted_{y_columns[i]}"].apply(lambda x: convert_seconds_to_hh_mm_ss(x))

    #     # print the dataframe
    #     print(df)

    # I want to know when my train to London Waterloo is going to arrive, the scheduled arrival time is 10:00:00
    model = load_model("random_forest_actual_arrival.pkl", "data/output/models/random_forest/")
    tpl = "WATRLMN"
    x_column = "scheduled_arrival"
    y_column = "actual_arrival"
    x_value = "08:25:00"
    df = convert_user_input(tpl, x_column, y_column, x_value)
    print (df)
    df = predict_user_input(df, x_column, y_column, model)
    print (df)

    
if __name__ == "__main__":
    main()