# %%
import requests 
from dotenv import load_dotenv
import os
import pandas as pd
from utils import get_data
import numpy as np

#todo: check about having the time row as the index, it could break downstream stuff :(




# %%
"""
We have different timestamps and have to combine them to a single timeline, with the correct frame counts

If that's so I guess I'm going to have to add everything together and the sort by timestamp

The standardized timestamp would be by second...
"""

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

    frame_count["time"] = pd.to_datetime(frame_count["Filename"].apply(lambda x: x.split("/")[1][:-6]),
                                          format="%Y-%m-%d %H:%M:%S.%f")
    processed= pd.DataFrame()
    processed[["Filename", "time"]] = frame_count[["Filename", "time"]]
    processed["begin frame"], processed[["end frame", "class"]] = 0, np.nan
    processed.set_index("time", inplace=True, drop = True)
    processed = processed[["Filename", "class", "begin frame", "end frame"]]
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
    processed.set_index("time", inplace=True, drop = True)
    processed  = processed[['filename', 'class', 'begin frame', 'end frame']]
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
    return merged_dataframe.sort_index()


# %% 
def run_algo(unified_dataframe:pd.DataFrame) -> pd.DataFrame:
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

    for (index, row) in unified_dataframe.iterrows():
    
#%%
if __name__ == "__main__":
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    SHEET_ID = os.getenv("SHEET_ID")


    frame_count = get_data("frame count")
    log_no = get_data("logNo")
    log_pos = get_data("logPos")
    processed_frame_count = process_frame_count(frame_count)
    processed_log_no = process_log(log_no, "logNo")
    print(f""" Frame Count Dataframe Shape: {frame_count.shape}""")
    print(frame_count.head())
    print(f"""\n Log No Dataframe Shape: {log_no.shape}""")
    print(log_no.head())
    print(f"""\n Log Pos Dataframe Shape: {log_pos.shape}""")
    print(log_pos.head())

#%%
"""
ALGORITHM

""" 

final = pd.DataFrame(columns=["filename", "class", "begin frame", "end frame"])

#%%

        
        

# %%

# %%
final.to_csv("final.csv")
# %%
