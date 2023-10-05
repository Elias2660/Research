# %%
import requests 
from dotenv import load_dotenv
import os
import pandas as pd
from utils import get_data
import numpy as np

#TODO Work on processing on the log dataframes

# %%

load_dotenv()
API_KEY = os.getenv("API_KEY")
SHEET_ID = os.getenv("SHEET_ID")

# %%
frame_count = get_data("frame count")
log_no = get_data("logNo")
log_pos = get_data("logPos")


print(f""" Frame Count Dataframe Shape: {frame_count.shape}""")
print(frame_count.head())
print(f"""\n Log No Dataframe Shape: {log_no.shape}""")
print(log_no.head())
print(f"""\n Log Pos Dataframe Shape: {log_pos.shape}""")
print(log_pos.head())


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
    logs =  pd.concat(unpacked_logs, ignore_index=True)
    merged_dataframe = pd.merge_asof(frame_count, logs,on="time", direction="backward")
    return merged_dataframe
    
#%%
#------------------------------------------------------------------------------------------------------------------------


fc_index, log_no_index, log_pos_index, event_number = 0, 0, 0, 0 #current indicies

current_class =  False if log_no.iloc[0]["time"] < log_pos.iloc[0]["time"] else True

if (min(log_no.iloc[0]["time"], log_pos.iloc[0]["time"]) != frame_count.iloc[0]["time"]):
    current_class = not current_class

#%%
if __name__ == "__main__":
    processed_frame_count = process_frame_count(frame_count)
    processed_log_no = process_log(log_no, "no")


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
