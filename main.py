# %%
import requests 
from dotenv import load_dotenv
import os
import pandas as pd
from utils import get_data
import numpy as np


"""
TODO: Finish implementation so that it can add headings and process
the test cases

"""

#%%
#first, I'm probably going to have to create a new dataframe with standardized timestamps
#by second

#let's start with the frame count dataframe
def process_frame_count(frame_count: pd.DataFrame) -> pd.DataFrame:
    """
    DESCRIPTION
    ----------
    Given the frame count dataframe, add a column called "time" which has timestamps 
    taken from the Filename column

    Format of the frame count filename: "2023-08-09_2023-08-12/2023-08-09 07:42:21.978565.h264'"
    2023-08-09 07:42:21.978565 -> YYYY-MM-DD HH:MM:SS.SSSSSS

    CONTRACT
    --------
    pd.Dataframe -> pd.Dataframe
    """
    processed= pd.DataFrame()
    processed["time"] = pd.to_datetime(frame_count["Filename"].apply(lambda x: x.split("/")[1][:-6]),
                                          format="%Y-%m-%d %H:%M:%S.%f")
    processed["Filename"], processed["begin frame"], processed[["end frame", "class"]] = frame_count["Filename"], 0, np.nan
    processed = processed[["Filename", "class", "begin frame", "end frame", "time"]]
    return processed
#%%
"""
now, let's do the same for the log_no and the lot_pos dataframes

since they're the same structure-wise, I'm going to do it in a single function

Time structure of logno/logpos dataframes: 20230809_083952
20230809_083952 -> YYYYMMDD_HHMMSS
"""

def process_log(log: pd.DataFrame, event_change_type:str) -> pd.DataFrame:
    """
    DESCRIPTION
    -----------
    Given a log dataframe, return the same dataframe with a "time" column
    and class column

    CONTRACT
    --------
    process_logs(log) -> pd.Dataframe
    log: log dataframe to be processed
    """
    log["time"] = pd.to_datetime(log["year/month/day_hour/min/sec"],
                                 format="%Y%m%d_%H%M%S")
    log["class"] = event_change_type
    processed = pd.DataFrame()
    processed[["time", "class"]] = log[["time", "class"]]
    processed["begin frame"], processed[["end frame", "filename"]] = np.nan, np.nan
    processed  = processed[['filename', 'class', 'begin frame', 'end frame', "time"]]
    return  processed



# %%
def create_unified_dataframe(frame_count: pd.DataFrame, *args: pd.DataFrame) -> pd.DataFrame:
    """
    DESCRIPTION
    -----------
    Given a dataframe, create unified dataframe
    Columns of unified dataframe is:
    filename, class, begin frame, end frame

    CONTACT
    create_unified_dataframe(frame_count, logs, log_pos) -> pd.DataFrame
    frame_count: frame count dataframe
    logs: combined data types
    """
    unpacked_logs = list(args)
    logs =  pd.concat(unpacked_logs)
    merged_dataframe = pd.concat([frame_count, logs])
    merged_dataframe.sort_values(by="time", inplace=True)
    merged_dataframe.reset_index(inplace=True)
    return merged_dataframe.sort_index()

def get_classes_from_dataframe(dataframe: pd.DataFrame) -> list:
    """
    DESCRIPTION
    -----------
    Given a dataframe, return a list of all the classes

    CONTRACT
    --------
    get_classes_from_dataframe(dataframe) -> list
    dataframe: dataframe to be processed
    """
    return list(dataframe["class"].unique())


# %% 
def run_algo(unified_dataframe:pd.DataFrame, frame_count: pd.DataFrame) -> pd.DataFrame:
    """
    DESCRIPTION
    1- Sort the values of the datafame by time
    2- Fill in the values for the dataframe
        For the log dataframe, you need the begin frame, filename, and end frame.

        Begin frame = Time elapsd since last frame filechange, 

        End frame =  Time of next - time of last, unless it changes as a frame change

        Filename: filename of the last file change


        For the frame count dataframes, you need the class name and the end frame

        Classname = class of the last event change, or the opposite of the next event change
    CONTRACT
    run_algo(pd.Dataframe) -> pd.DataFrame
    unified_dataframe: the (sorted) unified dataframe containing all the classes and such

    REMINDERs
    Remember to fix the edge cases
    """
    final = unified_dataframe.copy(deep=True)
    for (index, row) in final.iterrows():
        #Filename: filename of the last file change if index is !0, filename is NAN
        if (pd.isnull(row["Filename"]) and index != 0):
            final.loc[index,"Filename"] = final.loc[index - 1,"Filename"] 

        #class of the last event change, or the opposite of the next event change
        if (pd.isnull(row["class"])):
             #assumes the if the first row is nan, the second row is an class change
             #TODO: fix assumption and find out how to fix the class change problems
            final.loc[index,"class"] = final.loc[index - 1,"class"] if index != 0 else final.loc[index + 1,"class"]
        
        #begin frame,
        if (pd.isnull(row["begin frame"])):
            #if this is the first frame, just assume np.nan (because if it's not zero, you don't know when the begin frame is)
            final.loc[index,"begin frame"] = final.loc[index - 1,"end frame"] if index != 0 else np.nan
        
        #end frame
        if (pd.isnull(row["end frame"])):
            """
            by default, we're going to assume the end frame is time difference is 
            the time difference between the time of the next event and the current time times 24
            however if the next event is a frame change we're just going to assume the end frame is the last frame filename
            """
            if(index == final.shape[0] - 1):
                #if this is the last event
                final.loc[index,"end frame"] = pd.to_numeric(frame_count.loc[frame_count["Filename"] == final.loc[index,"Filename"]].iloc[0]["Frame count"])
            elif (final.loc[index + 1,"Filename"] != row["Filename"] and not pd.isnull(final.loc[index + 1,"Filename"]) ):
                #if the next event is a frame change
                final.loc[index,"end frame"] = pd.to_numeric(frame_count.loc[frame_count["Filename"] == final.loc[index,"Filename"]].iloc[0]["Frame count"])
            else:
                 final.loc[index,"end frame"] = (final.loc[index + 1,"time"] - row["time"]).seconds * 24
        
    return final[['Filename', 'class', 'begin frame', 'end frame']]
                


    
#%%
if __name__ == "__main__":
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    SHEET_ID = os.getenv("SHEET_ID")


    frame_count = get_data("frame count")
    log_no = get_data("logNo")
    log_pos = get_data("logPos")
    processed_frame_count = process_frame_count(frame_count)
    processed_log_pos = process_log(log_pos, "logPos")
    processed_log_no = process_log(log_no, "logNo")
    unified_dataframe = create_unified_dataframe(processed_frame_count, processed_log_pos, processed_log_no)
    final = run_algo(unified_dataframe, frame_count)


# %%
final.to_csv("final.csv")
# %%
